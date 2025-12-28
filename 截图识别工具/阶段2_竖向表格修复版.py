#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第二阶段：批量OCR识别 - 竖向表格完全修复版
修复表头跳过逻辑，确保正确解析
"""

import os
import sys
import time
import json
import base64
import requests
import pandas as pd
from datetime import datetime
from PIL import Image
import re

# ========== 配置 ==========
class Config:
    # 百度OCR配置
    BAIDU_API_KEY = "Ru2GZsFF0jZII4GEwOZ6uoDB"
    BAIDU_SECRET_KEY = "duGtjcMzuswkTyZRT67G7OpmDAWxisaN"
    BAIDU_TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"
    BAIDU_OCR_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
    
    # 文件路径
    SCREENSHOT_FOLDER = "实时拼接结果"
    OUTPUT_FOLDER = "数据结果_修复版"
    
    # 性能配置
    TIMEOUT = 30
    RETRY_COUNT = 3

# ========== 竖向表格完全修复解析器 ==========
class VerticalTableParserFixed:
    def __init__(self):
        self.api_key = Config.BAIDU_API_KEY
        self.secret_key = Config.BAIDU_SECRET_KEY
        self.access_token = None
        
        # 创建输出文件夹
        if not os.path.exists(Config.OUTPUT_FOLDER):
            os.makedirs(Config.OUTPUT_FOLDER)
            print(f"✓ 创建结果文件夹: {Config.OUTPUT_FOLDER}")
        
        # 检查截图文件夹
        if not os.path.exists(Config.SCREENSHOT_FOLDER):
            print(f"✗ 截图文件夹不存在: {Config.SCREENSHOT_FOLDER}")
            sys.exit(1)
    
    def get_access_token(self):
        """获取访问令牌"""
        if self.access_token:
            return self.access_token
        
        try:
            params = {
                'grant_type': 'client_credentials',
                'client_id': self.api_key,
                'client_secret': self.secret_key
            }
            
            response = requests.get(Config.BAIDU_TOKEN_URL, params=params, timeout=10)
            result = response.json()
            
            if 'access_token' in result:
                self.access_token = result['access_token']
                print("✓ 获取百度OCR令牌成功")
                return self.access_token
        except Exception as e:
            print(f"✗ 获取令牌失败: {e}")
        
        return None
    
    def ocr_recognize(self, image_path):
        """OCR识别图片"""
        try:
            if not self.access_token:
                if not self.get_access_token():
                    return None, "无法获取令牌", None
            
            # 读取图片
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # 准备请求
            url = f"{Config.BAIDU_OCR_URL}?access_token={self.access_token}"
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = {
                'image': image_data,
                'language_type': 'CHN_ENG',
                'detect_direction': 'false',
                'paragraph': 'false',
                'probability': 'false'
            }
            
            # 发送请求
            response = requests.post(url, headers=headers, data=data, timeout=Config.TIMEOUT)
            result = response.json()
            
            if 'words_result' in result:
                # 提取所有文字
                text_lines = [item['words'] for item in result['words_result']]
                text = '\n'.join(text_lines)
                
                return text, None, text_lines
            else:
                error_msg = result.get('error_msg', '未知错误')
                return None, f"OCR失败: {error_msg}", None
                
        except Exception as e:
            return None, f"异常: {str(e)[:50]}", None
    
    def extract_etf_info(self, filename):
        """从文件名提取ETF信息"""
        # 格式: 0001_传媒ETF_512980.jpg
        try:
            parts = filename.split('_')
            if len(parts) >= 3:
                etf_code = parts[2].split('.')[0]  # 移除扩展名
                etf_name = parts[1]
                return etf_code, etf_name
        except:
            pass
        
        return "未知", "未知ETF"
    
    def parse_vertical_table_fixed(self, text_lines, etf_code, etf_name, filename):
        """完全修复的竖向表格解析"""
        if not text_lines:
            return None, "无文本行"
        
        print(f"  OCR返回 {len(text_lines)} 行文本")
        
        # 保存解析过程
        debug_file = os.path.join(Config.OUTPUT_FOLDER, f"FIXED_DEBUG_{etf_code}_{etf_name}.txt")
        
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(f"=== 竖向表格完全修复解析调试 ===\n")
            f.write(f"ETF: {etf_code} {etf_name}\n")
            f.write(f"文件: {filename}\n")
            f.write(f"时间: {datetime.now()}\n")
            f.write(f"总行数: {len(text_lines)}\n")
            f.write("="*60 + "\n")
            
            for i, line in enumerate(text_lines, 1):
                f.write(f"{i:3d}: {line}\n")
            
            f.write("\n" + "="*60 + "\n")
            f.write("解析过程:\n")
        
        # 查找表头位置 - 寻找"股票名称"所在行
        header_start = -1
        for i, line in enumerate(text_lines):
            if '股票名称' in line:
                header_start = i
                with open(debug_file, 'a', encoding='utf-8') as f:
                    f.write(f"找到'股票名称'表头在第{i+1}行\n")
                break
        
        if header_start == -1:
            with open(debug_file, 'a', encoding='utf-8') as f:
                f.write("未找到'股票名称'表头，尝试从第1行开始解析\n")
            header_start = 0
        
        # 关键修复：表头是4行，所以数据从 header_start + 4 开始
        data_start = header_start + 4
        with open(debug_file, 'a', encoding='utf-8') as f:
            f.write(f"表头从第{header_start+1}行开始，共4行\n")
            f.write(f"数据从第{data_start+1}行开始\n")
        
        # 检查是否有足够的数据
        if data_start >= len(text_lines):
            with open(debug_file, 'a', encoding='utf-8') as f:
                f.write(f"数据起始行{data_start+1}超出总行数{len(text_lines)}\n")
            return None, f"数据不足: 需要从{data_start+1}行开始，但只有{len(text_lines)}行"
        
        # 每4行一组处理
        data_rows = []
        line_count = 0
        
        for i in range(data_start, len(text_lines) - 3, 4):
            # 确保不越界
            if i + 3 >= len(text_lines):
                break
            
            # 提取4行数据
            stock_name = text_lines[i].strip()
            stock_code = text_lines[i+1].strip()
            stock_quantity = text_lines[i+2].strip()
            stock_percentage = text_lines[i+3].strip()
            
            line_count += 1
            
            with open(debug_file, 'a', encoding='utf-8') as f:
                f.write(f"\n处理第{line_count}组数据 (行{i+1}-{i+4}):\n")
                f.write(f"  名称: {stock_name}\n")
                f.write(f"  代码: {stock_code}\n")
                f.write(f"  数量: {stock_quantity}\n")
                f.write(f"  占比: {stock_percentage}\n")
            
            # 验证股票名称：至少2个字符，且不包含"股票"、"名称"等关键词
            if (len(stock_name) < 2 or 
                '股票' in stock_name or 
                '名称' in stock_name or
                '代码' in stock_name or
                '数量' in stock_name or
                '占比' in stock_name):
                with open(debug_file, 'a', encoding='utf-8') as f:
                    f.write(f"  ⚠ 跳过：股票名称不符合要求\n")
                continue
            
            # 验证股票代码：6位数字
            if not re.match(r'^\d{6}$', stock_code):
                with open(debug_file, 'a', encoding='utf-8') as f:
                    f.write(f"  ⚠ 跳过：股票代码不是6位数字: {stock_code}\n")
                continue
            
            # 验证股票数量：数字，可能包含逗号
            if not re.match(r'^[\d,]+$', stock_quantity.replace(',', '')):
                with open(debug_file, 'a', encoding='utf-8') as f:
                    f.write(f"  ⚠ 跳过：股票数量不是数字: {stock_quantity}\n")
                continue
            
            # 验证市值占比：数字+% 或 纯数字
            percentage_clean = stock_percentage.replace('%', '')
            if not re.match(r'^[\d.]+$', percentage_clean):
                with open(debug_file, 'a', encoding='utf-8') as f:
                    f.write(f"  ⚠ 跳过：市值占比不是有效数字: {stock_percentage}\n")
                continue
            
            # 确保百分比有%符号
            if '%' not in stock_percentage:
                stock_percentage = stock_percentage + '%'
                with open(debug_file, 'a', encoding='utf-8') as f:
                    f.write(f"  ✓ 修复：添加%符号 -> {stock_percentage}\n")
            
            # 添加到数据行
            data_rows.append([stock_name, stock_code, stock_quantity, stock_percentage])
            with open(debug_file, 'a', encoding='utf-8') as f:
                f.write(f"  ✓ 添加记录 {len(data_rows)}\n")
        
        with open(debug_file, 'a', encoding='utf-8') as f:
            f.write(f"\n解析结果: 找到 {len(data_rows)} 条有效记录\n")
        
        if not data_rows:
            return None, f"未解析出有效数据记录"
        
        # 创建DataFrame
        try:
            headers = ["股票名称", "股票代码", "股票数量", "市值占比"]
            df = pd.DataFrame(data_rows, columns=headers)
            
            # 添加ETF信息
            df.insert(0, 'ETF代码', etf_code)
            df.insert(1, 'ETF名称', etf_name)
            df.insert(2, '提取日期', datetime.now().strftime('%Y-%m-%d'))
            df.insert(3, '提取时间', datetime.now().strftime('%H:%M:%S'))
            
            with open(debug_file, 'a', encoding='utf-8') as f:
                f.write(f"\n最终数据: {len(df)} 行\n")
                f.write(df.to_string())
            
            return df, None
            
        except Exception as e:
            with open(debug_file, 'a', encoding='utf-8') as f:
                f.write(f"创建DataFrame失败: {str(e)}\n")
            return None, f"创建DataFrame失败: {str(e)[:50]}"
    
    def process_image(self, image_path, filename):
        """处理单张图片"""
        print(f"\n处理: {filename}")
        
        # 提取ETF信息
        etf_code, etf_name = self.extract_etf_info(filename)
        print(f"  ETF: {etf_code} {etf_name}")
        
        # OCR识别
        text, error, text_lines = self.ocr_recognize(image_path)
        
        if error:
            print(f"  ✗ OCR失败: {error}")
            return None, f"OCR失败: {error}", etf_code, etf_name
        
        if not text_lines:
            print(f"  ⚠ 无文本行")
            return None, "无文本行", etf_code, etf_name
        
        print(f"  ✓ OCR识别成功: {len(text_lines)} 行文本")
        
        # 解析竖向表格
        df, parse_error = self.parse_vertical_table_fixed(text_lines, etf_code, etf_name, filename)
        
        if parse_error:
            print(f"  ⚠ 解析失败: {parse_error}")
            return None, parse_error, etf_code, etf_name
        
        print(f"  ✓ 解析成功: {len(df)} 行数据")
        return df, None, etf_code, etf_name
    
    def create_excel(self, df, etf_code, etf_name, status="成功"):
        """创建Excel文件"""
        if df is None:
            # 创建错误文件
            df = pd.DataFrame({
                'ETF代码': [etf_code],
                'ETF名称': [etf_name],
                '提取时间': [datetime.now().strftime('%H:%M:%S')],
                '状态': [status],
                '错误信息': [status]
            })
        
        # 保存Excel
        excel_filename = f"{etf_name}_{etf_code}_持仓数据.xlsx"
        excel_path = os.path.join(Config.OUTPUT_FOLDER, excel_filename)
        
        try:
            df.to_excel(excel_path, index=False)
            return excel_path, len(df)
        except Exception as e:
            print(f"  保存Excel失败: {e}")
            return None, 0
    
    def run(self):
        """运行主程序"""
        print("="*60)
        print("     竖向表格完全修复版")
        print("="*60)
        print(f"开始时间: {datetime.now().strftime('%H:%M:%S')}")
        print("修复内容: 正确跳过4行表头，从第5行开始解析数据")
        print("="*60)
        
        # 获取所有图片
        image_files = []
        for filename in sorted(os.listdir(Config.SCREENSHOT_FOLDER)):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_path = os.path.join(Config.SCREENSHOT_FOLDER, filename)
                image_files.append((image_path, filename))
        
        if not image_files:
            print("✗ 没有找到截图文件")
            return
        
        print(f"找到 {len(image_files)} 张截图")
        
        # 获取访问令牌
        if not self.get_access_token():
            return
        
        print("\n开始处理...")
        
        all_results = []
        all_data = []
        
        for idx, (image_path, filename) in enumerate(image_files, 1):
            print(f"\n[{idx}/{len(image_files)}] ", end="")
            start_time = time.time()
            
            # 处理图片
            df, error, etf_code, etf_name = self.process_image(image_path, filename)
            
            # 创建Excel
            excel_path, row_count = self.create_excel(df, etf_code, etf_name, error if error else "成功")
            
            elapsed = time.time() - start_time
            
            result = {
                'filename': filename,
                'etf_code': etf_code,
                'etf_name': etf_name,
                'success': df is not None,
                'rows': row_count,
                'time': elapsed,
                'excel_path': excel_path,
                'error': error
            }
            
            all_results.append(result)
            
            if df is not None and len(df) > 1:  # 不是错误文件
                all_data.append(df)
            
            print(f"  耗时: {elapsed:.1f}秒")
        
        # 保存汇总
        if all_data:
            try:
                combined_df = pd.concat(all_data, ignore_index=True)
                summary_file = os.path.join(
                    Config.OUTPUT_FOLDER,
                    f"所有ETF持仓汇总_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                )
                combined_df.to_excel(summary_file, index=False)
                print(f"\n✓ 汇总文件: {summary_file}")
                print(f"  总数据行数: {len(combined_df)}")
            except Exception as e:
                print(f"汇总失败: {e}")
        
        # 显示统计
        success_count = sum(1 for r in all_results if r['success'])
        
        print("\n" + "="*60)
        print("处理完成！")
        print("="*60)
        print(f"总截图: {len(image_files)} 张")
        print(f"成功解析: {success_count} 张")
        print(f"失败: {len(image_files) - success_count} 张")
        
        if success_count > 0:
            print("\n成功解析的ETF:")
            for r in all_results:
                if r['success']:
                    print(f"  ✓ {r['etf_name']} ({r['etf_code']}): {r['rows']}行数据")
        
        if len(image_files) - success_count > 0:
            print("\n解析失败的ETF:")
            for r in all_results:
                if not r['success']:
                    print(f"  ✗ {r['etf_name']} ({r['etf_code']}): {r.get('error', '未知错误')}")
        
        print(f"\n调试文件保存在: {os.path.abspath(Config.OUTPUT_FOLDER)}")
        print("="*60)
        
        # 打开文件夹
        os.startfile(os.path.abspath(Config.OUTPUT_FOLDER))

# ========== 主程序 ==========
def main():
    try:
        parser = VerticalTableParserFixed()
        parser.run()
    except KeyboardInterrupt:
        print("\n\n⚠ 处理被中断")
    except Exception as e:
        print(f"\n程序错误: {e}")
    finally:
        input("\n按回车退出...")

if __name__ == "__main__":
    main()