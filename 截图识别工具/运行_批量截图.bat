@echo off
chcp 65001
title ETF数据提取 - 第一阶段：极速批量截图
color 0A
cls

echo ========================================
echo     第一阶段：ETF极速批量截图
echo ========================================
echo.
echo 功能说明：
echo 1. 以最快速度完成所有ETF截图
echo 2. 不进行OCR识别，只保存图片
echo 3. 目标速度：20+ ETF/分钟
echo 4. 截图保存到"截图缓存"文件夹
echo.
echo 注意：此阶段只截图，不识别文字
echo 识别文字请运行第二阶段程序
echo.
echo 按任意键开始运行...
pause > nul

echo.
echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python！
    echo 请先安装Python 3.8+并添加到PATH
    pause
    exit
)

echo.
echo 安装必要的Python库...
echo 正在安装pyautogui...
pip install pyautogui --quiet
echo 正在安装pandas...
pip install pandas openpyxl --quiet

echo.
echo 启动截图程序...
python "阶段1_批量截图.py"

echo.
echo 第一阶段完成！
pause