@echo off
chcp 65001 >nul
cd /d "%~dp0backend"

netstat -ano | findstr ":8000" | findstr "LISTENING" >nul
if %errorlevel%==0 (
    echo [SmartShop] 后端已在运行，无需重复启动。
    echo 地址: http://127.0.0.1:8000
) else (
    echo [SmartShop] 正在启动后端...
    start "SmartShop-Backend" .venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
    echo 已启动。浏览器访问 http://127.0.0.1:8000/docs 可验证。
)
pause
