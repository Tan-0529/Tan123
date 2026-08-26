@echo off
chcp 65001 >nul
cd /d "%~dp0windows\SmartShop"
echo [SmartShop] 正在启动客户端...
start "" "bin\Debug\net8.0-windows\SmartShop.exe"
