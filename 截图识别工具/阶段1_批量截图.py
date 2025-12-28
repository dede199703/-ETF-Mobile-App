#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第一阶段：批量截图并实时拼接
边截图边拼接，提高效率
"""

import os
import sys
import time
import json
import pandas as pd
import pyautogui
from datetime import datetime
from PIL import Image
import re

# ========== 配置 ==========
class Config:
    # 文件路径
    COORD_FILE = "坐标配置.json"
    ETF_LIST_FILE = "ETF列表.xlsx"
    OUTPUT_FOLDER = "实时拼接结果"
    
    # 时间配置
    WAIT_TIME = 1.0
    CLICK_DELAY = 0.08
    PAGE_LOAD = 1.2
    SCREENSHOT_WAIT = 0.3
    BETWEEN_ETF = 0.05
    
    # 拼接配置
    BATCH_SIZE = 5               # 每批拼接数量
    RESIZE_WIDTH = 1200          # 统一宽度
    SPACING = 20                 # 图片间距
    
    # 性能优化
    MAX_RETRY = 1
    QUALITY = 80

# ========== 实时拼接截图器 ==========
class RealTimeMergerScreenshotter:
    def __init__(self):
        self.coordinates = None
        self.etf_list = []
        self.current_batch = []
        self.batch_count = 0
        
        # 创建输出文件夹
        if not os.path.exists(Config.OUTPUT_FOLDER):
            os.makedirs(Config.OUTPUT_FOLDER)
            print(f"✓ 创建输出文件夹: {Config.OUTPUT_FOLDER}")
    
    def load_config(self):
        """加载配置"""
        print("="*60)
        print("     实时拼接截图器")
        print("="*60)
        print(f"开始时间: {datetime.now().strftime('%H:%M:%S')}")
        print(f"每批拼接: {Config.BATCH_SIZE} 个ETF")
        print("="*60)
        
        # 检查坐标文件
        if not os.path.exists(Config.COORD_FILE):
            print(f"✗ 找不到坐标文件: {Config.COORD_FILE}")
            return False
        
        # 加载坐标
        try:
            with open(Config.COORD_FILE, 'r', encoding='utf-8') as f:
                self.coordinates = json.load(f)
            
            required_keys = ["搜索框", "F10按钮", "投资组合", "申赎清单", "截图左上角", "截图右下角"]
            for key in required_keys:
                if key not in self.coordinates:
                    print(f"✗ 缺少坐标: {key}")
                    return False
            
            print("✓ 坐标配置加载成功")
        except Exception as e:
            print(f"✗ 加载坐标失败: {e}")
            return False
        
        return True
    
    def load_etf_list(self):
        """加载ETF列表"""
        if not os.path.exists(Config.ETF_LIST_FILE):
            etf_data = {
                "ETF代码": ["512980", "510300", "510500", "159919", "159915"],
                "ETF名称": ["传媒ETF", "沪深300ETF", "中证500ETF", "沪深300", "创业板"]
            }
            
            df = pd.DataFrame(etf_data)
            df.to_excel(Config.ETF_LIST_FILE, index=False)
            print(f"✓ 创建ETF列表文件: {Config.ETF_LIST_FILE}")
            print("  请用Excel添加您的ETF")
            input("  按回车继续...")
        
        try:
            df = pd.read_excel(Config.ETF_LIST_FILE)
            self.etf_list = df.to_dict('records')
            print(f"✓ 加载 {len(self.etf_list)} 个ETF")
            
            # 显示前几个
            print("\n前5个ETF:")
            for i, etf in enumerate(self.etf_list[:5], 1):
                print(f"  {i}. {etf['ETF代码']} - {etf['ETF名称']}")
                
        except Exception as e:
            print(f"✗ 加载ETF列表失败: {e}")
            return False
        
        return True
    
    def ultra_clear(self):
        """极速清空"""
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.01)
        pyautogui.press('delete')
    
    def ultra_input(self, text):
        """极速输入"""
        pyautogui.write(str(text), interval=0.003)
    
    def ultra_click(self, point_name):
        """极速点击"""
        x, y = self.coordinates[point_name]
        pyautogui.click(x, y)
        time.sleep(Config.CLICK_DELAY)
    
    def take_screenshot(self, etf_code, etf_name, index):
        """截图"""
        time.sleep(Config.SCREENSHOT_WAIT)
        
        x1, y1 = self.coordinates["截图左上角"]
        x2, y2 = self.coordinates["截图右下角"]
        width = x2 - x1
        height = y2 - y1
        
        screenshot = pyautogui.screenshot(region=(x1, y1, width, height))
        
        return screenshot, f"{etf_name}_{etf_code}"
    
    def add_to_batch(self, screenshot, etf_code, etf_name, index):
        """添加到当前批次"""
        self.current_batch.append({
            'image': screenshot,
            'etf_code': etf_code,
            'etf_name': etf_name,
            'index': index
        })
        
        print(f"  ✓ 添加到批次 {len(self.current_batch)}/{Config.BATCH_SIZE}")
        
        # 检查是否达到批次大小
        if len(self.current_batch) >= Config.BATCH_SIZE:
            self.merge_and_save_batch()
    
    def merge_and_save_batch(self):
        """合并并保存当前批次"""
        if not self.current_batch:
            return
        
        self.batch_count += 1
        
        # 调整所有图片到相同宽度
        resized_images = []
        max_width = 0
        total_height = 0
        etf_info_list = []
        
        for item in self.current_batch:
            try:
                img = item['image']
                # 调整宽度
                if img.width > Config.RESIZE_WIDTH:
                    ratio = Config.RESIZE_WIDTH / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((Config.RESIZE_WIDTH, new_height), Image.Resampling.LANCZOS)
                elif img.width < Config.RESIZE_WIDTH:
                    # 如果宽度较小，填充到标准宽度
                    new_img = Image.new('RGB', (Config.RESIZE_WIDTH, img.height), (255, 255, 255))
                    x_offset = (Config.RESIZE_WIDTH - img.width) // 2
                    new_img.paste(img, (x_offset, 0))
                    img = new_img
                
                resized_images.append(img)
                
                # 更新最大宽度和总高度
                if img.width > max_width:
                    max_width = img.width
                total_height += img.height
                
                etf_info_list.append(f"{item['etf_name']}({item['etf_code']})")
                
            except Exception as e:
                print(f"  处理图片失败: {e}")
                continue
        
        if not resized_images:
            return
        
        # 计算总高度（包括间距）
        total_height_with_spacing = total_height + (Config.SPACING * (len(resized_images) - 1))
        
        # 创建新图片
        merged_image = Image.new('RGB', (max_width, total_height_with_spacing), color=(255, 255, 255))
        
        # 拼接图片
        y_offset = 0
        for i, img in enumerate(resized_images):
            x_offset = (max_width - img.width) // 2
            merged_image.paste(img, (x_offset, y_offset))
            y_offset += img.height + Config.SPACING
        
        # 保存拼接图片
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        merged_filename = f"批次{self.batch_count:03d}_{timestamp}.jpg"
        merged_path = os.path.join(Config.OUTPUT_FOLDER, merged_filename)
        
        merged_image.save(merged_path, format='JPEG', quality=Config.QUALITY, optimize=True)
        
        print(f"\n✓ 保存拼接批次 {self.batch_count}")
        print(f"  文件名: {merged_filename}")
        print(f"  尺寸: {merged_image.width}x{merged_image.height}")
        print(f"  包含: {', '.join(etf_info_list)}")
        print(f"  预计节省OCR调用: {len(self.current_batch)-1} 次")
        
        # 清空当前批次
        self.current_batch = []
    
    def process_etf(self, etf_code, etf_name, index, total):
        """处理单个ETF"""
        start_time = time.time()
        
        try:
            # 1. 搜索ETF
            self.ultra_click("搜索框")
            self.ultra_clear()
            self.ultra_input(etf_code)
            time.sleep(0.03)
            pyautogui.press('enter')
            time.sleep(Config.WAIT_TIME)
            
            # 2. 点击F10
            self.ultra_click("F10按钮")
            time.sleep(Config.PAGE_LOAD)
            
            # 3. 点击投资组合
            self.ultra_click("投资组合")
            time.sleep(0.05)
            
            # 4. 点击申赎清单
            self.ultra_click("申赎清单")
            time.sleep(Config.PAGE_LOAD)
            
            # 5. 截图
            screenshot, info = self.take_screenshot(etf_code, etf_name, index)
            
            # 6. 添加到批次
            self.add_to_batch(screenshot, etf_code, etf_name, index)
            
            elapsed = time.time() - start_time
            return True, elapsed
            
        except Exception as e:
            elapsed = time.time() - start_time
            return False, f"{str(e)[:30]}"
    
    def run(self):
        """运行主程序"""
        if not self.load_config():
            return
        
        if not self.load_etf_list():
            return
        
        print(f"\n开始处理 {len(self.etf_list)} 个ETF")
        print(f"将分为 {len(self.etf_list) // Config.BATCH_SIZE + 1} 批进行拼接")
        print(f"预计节省OCR调用: {len(self.etf_list) - (len(self.etf_list) // Config.BATCH_SIZE + 1)} 次")
        
        input("按回车开始（确保东方财富窗口在最前）...")
        
        # 激活窗口
        print("激活窗口...")
        time.sleep(1)
        
        success_count = 0
        start_total = time.time()
        
        for idx, etf in enumerate(self.etf_list, 1):
            etf_code = str(etf['ETF代码']).strip()
            etf_name = str(etf['ETF名称']).strip()
            
            print(f"\n[{idx}/{len(self.etf_list)}] 处理: {etf_code} - {etf_name}")
            
            success, result = self.process_etf(etf_code, etf_name, idx, len(self.etf_list))
            
            if success:
                success_count += 1
                print(f"  ✓ 完成: {result:.1f}s")
            else:
                print(f"  ✗ 失败: {result}")
            
            # 等待
            if idx < len(self.etf_list):
                time.sleep(Config.BETWEEN_ETF)
        
        # 处理最后一批（如果不满一批）
        if self.current_batch:
            self.merge_and_save_batch()
        
        # 统计
        total_time = time.time() - start_total
        original_calls = len(self.etf_list)
        merged_calls = self.batch_count
        saved_calls = original_calls - merged_calls
        
        print("\n" + "="*60)
        print("处理完成！")
        print("="*60)
        print(f"总ETF数: {len(self.etf_list)} 个")
        print(f"成功处理: {success_count} 个")
        print(f"生成拼接图片: {self.batch_count} 张")
        print(f"总耗时: {total_time:.1f}秒")
        print(f"节省OCR调用: {saved_calls} 次")
        print(f"节省比例: {saved_calls/original_calls*100:.1f}%")
        print("="*60)
        
        os.startfile(os.path.abspath(Config.OUTPUT_FOLDER))
        input("\n按回车退出...")

# ========== 主程序 ==========
def main():
    pyautogui.PAUSE = 0.01
    
    try:
        merger = RealTimeMergerScreenshotter()
        merger.run()
    except KeyboardInterrupt:
        print("\n\n⚠ 处理被中断")
    except Exception as e:
        print(f"\n程序错误: {e}")
    finally:
        pass

if __name__ == "__main__":
    main()