@echo off
chcp 65001
title 使用Docker构建APK
color 0A
cls

echo ========================================
echo     使用Docker构建ETF手机App APK
echo ========================================
echo.
echo 注意：这需要先安装Docker Desktop
echo 如果还没安装，请访问：https://www.docker.com/products/docker-desktop
echo.
echo 按任意键继续...
pause > nul

echo 检查Docker是否安装...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Docker！
    echo 请先安装Docker Desktop
    pause
    exit
)

echo 正在使用Docker构建APK...
echo 这可能需要10-20分钟，请耐心等待...
echo.

docker run --rm \
  -v %cd%:/home/user/hostcwd \
  -v ~/.buildozer:/home/user/.buildozer \
  -v ~/.android:/home/user/.android \
  -e P4A_RELEASE_KEYSTORE=/home/user/hostcwd/keystore.jks \
  -e P4A_RELEASE_KEYSTORE_PASSWD=android \
  -e P4A_RELEASE_KEYALIAS_PASSWD=android \
  -e P4A_RELEASE_KEYALIAS=key \
  czaks/kivy-buildozer-android:latest \
  /bin/bash -c "cd /home/user/hostcwd && buildozer -v android debug"

if errorlevel 1 (
    echo.
    echo ❌ 构建失败！
    echo 请查看上面的错误信息
) else (
    echo.
    echo ✅ 构建成功！
    echo APK文件在: bin/ETF手机App-0.1-debug.apk
)

echo.
pause