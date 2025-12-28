@echo off
chcp 65001
title ETF手机App - 完整打包流程
color 0A
cls

echo ========================================
echo     ETF手机App - 完整打包流程
echo ========================================
echo 从代码到可执行文件的完整流程
echo 请按步骤操作
echo.

echo 步骤1/6：检查项目结构...
if not exist "main.py" (
    echo ❌ 未找到main.py文件
    echo 请确保在正确的文件夹中运行
    pause
    exit
)

if not exist "data" mkdir data
if not exist "database" mkdir database
if not exist "exports" mkdir exports

echo ✅ 项目结构正常
echo.

echo 步骤2/6：安装依赖库...
pip install kivy pandas openpyxl >nul 2>&1
if errorlevel 1 (
    echo ⚠ 安装库失败，尝试继续...
) else (
    echo ✅ 依赖库安装完成
)
echo.

echo 步骤3/6：测试应用运行...
echo 正在启动应用测试...
start python main.py
echo 请确认应用能正常运行
echo 按任意键继续...
pause > nul
echo.

echo 步骤4/6：准备资源文件...
if not exist "icon.ico" (
    echo 正在创建图标...
    python 创建图标.py
    if errorlevel 1 (
        echo ⚠ 图标创建失败，使用默认图标
        copy NUL icon.ico >nul
    )
)
echo ✅ 资源文件准备完成
echo.

echo 步骤5/6：打包为可执行文件...
call 一键构建.bat
if errorlevel 1 (
    echo ❌ 打包失败！
    pause
    exit
)
echo.

echo 步骤6/6：创建分发包...
echo 正在创建ZIP分发包...
cd dist
if exist "ETF手机App_完整版.zip" del "ETF手机App_完整版.zip"
powershell Compress-Archive -Path "ETF手机App" -DestinationPath "ETF手机App_完整版.zip" -Force
cd ..

echo.
echo ========================================
echo     🎉 打包完成！🎉
echo ========================================
echo 已生成的文件：
echo   📦 dist\ETF手机App_完整版.zip - 完整分发包
echo   📁 dist\ETF手机App\ - 可执行文件目录
echo   📱 ETF手机App.exe - 主程序
echo.
echo 使用说明：
echo 1. 将ZIP文件发送到其他电脑
echo 2. 解压后运行"启动App.bat"
echo 3. 无需安装Python，开箱即用
echo.
echo 注意：这是一个Windows应用
echo 如需Android版本，请使用WSL2或Linux
echo ========================================
echo.

pause