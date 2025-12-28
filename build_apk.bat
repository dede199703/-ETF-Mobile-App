@echo off
chcp 65001
title 构建ETF手机App APK
color 0A
cls

echo ========================================
echo     构建ETF手机App APK
echo ========================================
echo.
echo 注意：这需要安装Buildozer
echo 如果还没安装，请先运行:
echo pip install buildozer
echo.
echo 按任意键开始构建...
pause > nul

echo 正在构建APK...
buildozer -v android debug

echo.
echo 构建完成！
echo APK文件在: bin/ETF手机App-0.1-debug.apk
pause