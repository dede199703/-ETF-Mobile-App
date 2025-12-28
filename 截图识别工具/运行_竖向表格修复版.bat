@echo off
chcp 65001
title ETF OCR - Vertical Table Parser Fixed
color 0A
cls

echo ========================================
echo     ETF OCR - Vertical Table Parser Fixed
echo ========================================
echo.
echo Press any key to start...
pause > nul

echo.
echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit
)

echo.
echo Installing libraries...
pip install pandas openpyxl --quiet
pip install requests --quiet
pip install pillow --quiet

echo.
echo Starting OCR processor...
python "阶段2_竖向表格修复版.py"

echo.
echo Process completed!
pause