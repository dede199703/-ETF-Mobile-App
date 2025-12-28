#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETF截图自动拼接程序
将多个ETF截图拼接成一张大图，节省OCR调用次数
"""

import os
import sys
import time
from PIL import Image
from datetime import datetime
import re
import math

# ========== 配置 ==========
class Config:
    # 输入输出文件夹
    INPUT_FOLDER = "截图缓存"        # 截图文件夹
    OUTPUT_FOLDER = "拼接图片"       # 拼接后图片文件夹
    MERGED_LOG = "拼接记录.xlsx"     # 拼接记录
    
    # 拼接配置
    MAX_PER_IMAGE = 5               # 每张拼接图最多包含的ETF数量
    RESIZE_WIDTH = 1200             # 统一宽度
    QUALITY = 80                    # 输出图片质量
    SPACING = 20                    # 图片间距（像素）

# ========== 图片拼接器 ==========
class ImageMerger:
    def __init__(self):
        self.input_folder = Config.INPUT_FOLDER
        self.output_folder = Config.OUTPUT_FOLDER
        self.merged_log = Config.MERGED_LOG
        
        # 创建输出文件夹
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
            print(f"✓ 创建拼接文件夹: {self.output_folder}")
    
    def extract_etf_info(self, filename):
        """从文件名提取ETF信息"""
        # 格式: 0001_传媒ETF_512980.jpg
        match = re.search(r'(\d{4})_([^_]+)_(\d{6})', filename)
        if match:
            index = int(match.group(1))
            etf_name = match.group(2)
            etf_code = match.group(3)
            return index, etf_name, etf_code
        return 0, "未知", "000000"
    
    def get_image_files(self):
        """获取所有图片文件并排序"""
        image_files = []
        
        for filename in os.listdir(self.input_folder):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                # 提取序号用于排序
                index, etf_name, etf_code = self.extract_etf_info(filename)
                if index > 0:
                    image_path = os.path.join(self.input_folder, filename)
                    image_files.append({
                        'path': image_path,
                        'filename': filename,
                        'index': index,
                        'etf_name': etf_name,
                        'etf_code': etf_code
                    })
        
        # 按序号排序
        image_files.sort(key=lambda x: x['index'])
        return image_files
    
    def resize_image(self, img, target_width):
        """等比例调整图片宽度"""
        if img.width <= target_width:
            return img
        
        # 计算新高度
        ratio = target_width / img.width
        new_height = int(img.height * ratio)
        
        return img.resize((target_width, new_height), Image.Resampling.LANCZOS)
    
    def merge_images_vertical(self, images, batch_num):
        """垂直拼接多张图片"""
        if not images:
            return None
        
        # 调整所有图片到相同宽度
        resized_images = []
        max_width = 0
        total_height = 0
        
        for img_info in images:
            try:
                img = Image.open(img_info['path'])
                resized_img = self.resize_image(img, Config.RESIZE_WIDTH)
                resized_images.append(resized_img)
                
                # 更新最大宽度和总高度
                if resized_img.width > max_width:
                    max_width = resized_img.width
                total_height += resized_img.height
            except Exception as e:
                print(f"  处理图片失败 {img_info['filename']}: {e}")
                continue
        
        if not resized_images:
            return None
        
        # 计算总高度（包括间距）
        total_height_with_spacing = total_height + (Config.SPACING * (len(resized_images) - 1))
        
        # 创建新图片
        merged_image = Image.new('RGB', (max_width, total_height_with_spacing), color=(255, 255, 255))
        
        # 拼接图片
        y_offset = 0
        for i, img in enumerate(resized_images):
            # 将图片粘贴到指定位置
            x_offset = (max_width - img.width) // 2
            merged_image.paste(img, (x_offset, y_offset))
            
            y_offset += img.height + Config.SPACING
        
        return merged_image
    
    def process_batch_merging(self):
        """批量处理图片拼接"""
        print("="*60)
        print("     图片自动拼接程序")
        print("="*60)
        print(f"开始时间: {datetime.now().strftime('%H:%M:%S')}")
        print(f"每张拼接图包含: {Config.MAX_PER_IMAGE} 个ETF")
        print("="*60)
        
        # 获取所有图片
        image_files = self.get_image_files()
        
        if not image_files:
            print("✗ 没有找到图片文件")
            return []
        
        print(f"找到 {len(image_files)} 张图片")
        
        # 分批处理
        batch_count = math.ceil(len(image_files) / Config.MAX_PER_IMAGE)
        all_batches = []
        
        print(f"\n将分为 {batch_count} 批进行拼接")
        print("开始处理...\n")
        
        for batch_num in range(batch_count):
            start_idx = batch_num * Config.MAX_PER_IMAGE
            end_idx = min(start_idx + Config.MAX_PER_IMAGE, len(image_files))
            
            batch_images = image_files[start_idx:end_idx]
            
            print(f"处理批次 {batch_num+1}/{batch_count} (图片 {start_idx+1}-{end_idx})")
            
            # 获取ETF信息
            etf_info = []
            for img_info in batch_images:
                etf_info.append(f"{img_info['etf_name']}({img_info['etf_code']})")
            
            # 拼接图片
            merged_image = self.merge_images_vertical(batch_images, batch_num+1)
            
            if merged_image:
                # 保存拼接后的图片
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                merged_filename = f"合并批次{batch_num+1:03d}_{timestamp}.jpg"
                merged_path = os.path.join(self.output_folder, merged_filename)
                
                merged_image.save(merged_path, format='JPEG', quality=Config.QUALITY, optimize=True)
                
                # 记录批次信息
                batch_record = {
                    'batch_num': batch_num + 1,
                    'merged_file': merged_filename,
                    'etf_count': len(batch_images),
                    'etf_list': '; '.join(etf_info),
                    'width': merged_image.width,
                    'height': merged_image.height,
                    'size_kb': os.path.getsize(merged_path) // 1024
                }
                
                all_batches.append(batch_record)
                
                print(f"  ✓ 保存: {merged_filename}")
                print(f"    尺寸: {merged_image.width}x{merged_image.height}")
                print(f"    包含: {', '.join(etf_info)}")
            else:
                print(f"  ✗ 批次 {batch_num+1} 拼接失败")
        
        return all_batches
    
    def run(self):
        """运行主程序"""
        all_batches = self.process_batch_merging()
        
        if not all_batches:
            return
        
        # 显示统计
        print("\n" + "="*60)
        print("拼接完成！")
        print("="*60)
        
        total_images = sum(batch['etf_count'] for batch in all_batches)
        total_merged = len(all_batches)
        original_calls = total_images
        merged_calls = total_merged
        saved_calls = original_calls - merged_calls
        saved_percent = (saved_calls / original_calls * 100) if original_calls > 0 else 0
        
        print(f"原始图片数量: {total_images} 张")
        print(f"拼接后图片数量: {total_merged} 张")
        print(f"预计节省OCR调用: {saved_calls} 次")
        print(f"节省比例: {saved_percent:.1f}%")
        
        if original_calls > 0:
            cost_per_call = 0.005  # 假设每次0.005元
            saved_money = saved_calls * cost_per_call
            print(f"预计节省费用: {saved_money:.2f} 元")
        
        print(f"\n拼接图片保存在: {os.path.abspath(self.output_folder)}")
        print("="*60)
        
        # 打开文件夹
        os.startfile(os.path.abspath(self.output_folder))
        
        input("\n按回车退出...")

# ========== 主程序 ==========
def main():
    try:
        merger = ImageMerger()
        merger.run()
    except KeyboardInterrupt:
        print("\n\n⚠ 处理被中断")
    except Exception as e:
        print(f"\n程序错误: {e}")
    finally:
        pass

if __name__ == "__main__":
    main()