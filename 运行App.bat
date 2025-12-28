@echo off
chcp 65001
title ETF手机App - 电脑测试版
color 0A
cls

echo ========================================
echo     ETF手机App - 电脑测试版
echo ========================================
echo 在电脑上模拟手机环境运行
echo 功能与手机版完全一致
echo.
echo 按任意键启动...
pause > nul

echo 检查环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python
    pause
    exit
)

echo 安装必要库...
pip install kivy pandas openpyxl

echo.
echo 启动ETF手机App...
python main.py

echo.
echo App已关闭！
pause