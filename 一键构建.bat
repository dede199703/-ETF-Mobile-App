@echo off
chcp 65001
title ETF手机App - 一键构建工具
color 0A
cls

echo ========================================
echo     ETF手机App - 一键构建工具
echo ========================================
echo 使用Python直接打包，无需复杂配置
echo.

echo 第一步：检查环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python
    pause
    exit
)

echo 第二步：安装必要库...
echo 这可能需要几分钟...
pip install pyinstaller

echo 第三步：打包成Windows可执行文件...
echo 正在打包，请稍候...

pyinstaller --onefile ^
  --windowed ^
  --name "ETF手机App" ^
  --icon icon.ico ^
  --add-data "data;data" ^
  --add-data "database;database" ^
  --add-data "exports;exports" ^
  --hidden-import kivy ^
  --hidden-import pandas ^
  --hidden-import openpyxl ^
  --hidden-import sqlite3 ^
  main.py

if errorlevel 1 (
    echo ❌ 打包失败！
    echo 请查看上面的错误信息
    pause
    exit
)

echo 第四步：复制资源文件...
if not exist "dist\ETF手机App" mkdir "dist\ETF手机App"
xcopy "data" "dist\ETF手机App\data" /E /I /Y
xcopy "database" "dist\ETF手机App\database" /E /I /Y
xcopy "exports" "dist\ETF手机App\exports" /E /I /Y

echo 第五步：创建启动脚本...
echo @echo off > "dist\ETF手机App\启动App.bat"
echo chcp 65001 >> "dist\ETF手机App\启动App.bat"
echo title ETF手机App >> "dist\ETF手机App\启动App.bat"
echo color 0A >> "dist\ETF手机App\启动App.bat"
echo cls >> "dist\ETF手机App\启动App.bat"
echo echo 正在启动ETF手机App... >> "dist\ETF手机App\启动App.bat"
echo ETF手机App.exe >> "dist\ETF手机App\启动App.bat"
echo pause >> "dist\ETF手机App\启动App.bat"

echo ✅ 打包完成！
echo.
echo 文件位置: dist\ETF手机App\
echo 包含文件:
echo   📱 ETF手机App.exe - 主程序
echo   📁 data/ - 数据文件夹
echo   📁 database/ - 数据库文件夹
echo   📁 exports/ - 导出文件夹
echo   🏃 启动App.bat - 启动脚本
echo.
echo 您可以将整个"dist\ETF手机App"文件夹复制到任何Windows电脑运行
echo.

pause