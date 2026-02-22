@echo off
title CNC AI Trading System
color 0A

echo.
echo  ================================================
echo   CNC AI TRADING SYSTEM - Launcher
echo  ================================================
echo.

:: ── Check if Python is installed ──────────────────────────────────────────────
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (

    IF EXIST "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
        SET "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"
        goto check_deps
    )
    IF EXIST "C:\Program Files\Python311\python.exe" (
        SET "PATH=C:\Program Files\Python311;C:\Program Files\Python311\Scripts;%PATH%"
        goto check_deps
    )

    echo  [!] Python not found. Downloading and installing Python 3.11...
    echo      This only happens once. Please wait.
    echo.

    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile '%TEMP%\python_installer.exe'"

    IF NOT EXIST "%TEMP%\python_installer.exe" (
        echo  [ERROR] Could not download Python. Check your internet connection.
        pause
        exit /b 1
    )

    "%TEMP%\python_installer.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_launcher=0

    echo  [OK] Python installed.
    echo  [..] Relaunching with updated PATH...
    start "CNC AI Trading System" cmd /k ""%~f0""
    exit /b
)

:check_deps
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo  [ERROR] Python not accessible. Close this window and run LAUNCH.bat again.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo  [OK] Python %PYVER% found.

echo.
echo  [..] Checking dependencies...

python -c "import flask" >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo  [..] Installing required packages (first run only)...
    python -m pip install -r "%~dp0requirements.txt" flask flask-cors --quiet --no-warn-script-location
    IF %ERRORLEVEL% NEQ 0 (
        echo  [ERROR] Failed to install packages. Try running as Administrator.
        pause
        exit /b 1
    )
    echo  [OK] Packages installed.
) ELSE (
    echo  [OK] Dependencies OK.
)

:: ── Kill anything on port 5000 ─────────────────────────────────────────────────
echo.
echo  [..] Checking port 5000...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":5000 "') do (
    taskkill /F /PID %%a >nul 2>&1
)

:: ── Open browser after 3 second delay (separate process) ──────────────────────
echo  [OK] Scheduling browser open...
start "" cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:5000"

:: ── Run Flask in foreground — this keeps the window alive ────────────────────
echo  [OK] Starting server...
echo.
echo  ================================================
echo   Dashboard: http://localhost:5000
echo   Close this window to stop the server.
echo  ================================================
echo.

cd /d "%~dp0"
python server.py

:: If we get here Flask crashed
echo.
echo  [!] Server stopped. See errors above.
pause
