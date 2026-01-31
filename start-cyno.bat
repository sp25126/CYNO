@echo off
echo ========================================
echo    CYNO - AI Job Search Agent
echo    Starting Full Stack Application
echo ========================================
echo.

REM Check if in correct directory
if not exist "frontend\package.json" (
    echo ERROR: Run this script from the job-agent-production directory
    pause
    exit /b 1
)

echo [1/3] Starting FastAPI Backend...
start "CYNO API" cmd /k "cd /d %~dp0 && python api/server.py"

echo [2/3] Waiting for API to start...
timeout /t 3 /nobreak > nul

echo [3/3] Starting React Frontend...
start "CYNO Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================
echo    CYNO is starting up!
echo ========================================
echo.
echo    Frontend: http://localhost:5173
echo    API:      http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.
echo    Press any key to open the browser...
pause > nul

start http://localhost:5173
