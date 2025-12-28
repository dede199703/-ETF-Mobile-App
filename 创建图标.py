#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建ETF手机App图标
"""

from PIL import Image, ImageDraw, ImageFont
import os

def 创建图标():
    """创建应用图标"""
    # 创建256x256像素的图标
    size = 256
    图片 = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    画笔 = ImageDraw.Draw(图片)
    
    # 绘制背景圆形
    画笔.ellipse([10, 10, size-10, size-10], fill=(102, 126, 234, 255))
    
    # 绘制内圆
    画笔.ellipse([30, 30, size-30, size-30], fill=(118, 75, 162, 255))
    
    # 绘制文字
    try:
        字体 = ImageFont.truetype("arial.ttf", 80)
    except:
        字体 = ImageFont.load_default()
    
    # 绘制"ETF"文字
    画笔.text((size//2-60, size//2-40), "ETF", font=字体, fill=(255, 255, 255, 255))
    
    # 保存为ICO文件
    图片.save("icon.ico", format="ICO", sizes=[(256, 256)])
    
    # 保存为PNG文件用于其他用途
    图片.save("icon.png")
    
    print("✅ 图标创建完成: icon.ico, icon.png")
    
    return True

if __name__ == "__main__":
    创建图标()