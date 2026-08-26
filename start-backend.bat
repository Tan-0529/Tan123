@echo off
cd /d "%~dp0backend"
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul
if %errorlevel%==0 (
    echo [SmartShop] Backend already running at http://127.0.0.1:8000
) else (
    echo [SmartShop] Starting backend...
    start "SmartShop-Backend" .venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
    echo Started. Verify at http://127.0.0.1:8000/docs
)
pause
