@echo off
chcp 65001
title ETF图片自动拼接
color 0A
cls

echo ========================================
echo     ETF图片自动拼接程序
echo ========================================
echo.
echo 功能：
echo 1. 将实时拼接结果中的图片自动拼接
echo 2. 每5张ETF截图合并为1张大图
echo 3. 节省80%%的OCR调用次数
echo.
echo 按任意键开始运行...
pause > nul

echo.
echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python！
    pause
    exit
)

echo.
echo 安装必要的库...
pip install pillow --quiet
pip install pandas --quiet

echo.
echo 启动拼接程序...
python "图片拼接程序.py"

echo.
echo 程序运行结束！
pause