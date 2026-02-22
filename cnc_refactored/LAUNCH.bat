@echo off
title CNC AI Trading System
color 0A

echo.
echo  ================================================
echo   CNC AI TRADING SYSTEM - Launcher
echo  ================================================
echo.

:: ── Python check ──────────────────────────────────────────────────────────────
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
    echo  [!] Python not found. Downloading...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile '%TEMP%\python_installer.exe'"
    IF NOT EXIST "%TEMP%\python_installer.exe" ( echo  [ERROR] Download failed. & pause & exit /b 1 )
    "%TEMP%\python_installer.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_launcher=0
    echo  [OK] Python installed. Relaunching...
    start "CNC AI Trading System" cmd /k ""%~f0""
    exit /b
)

:check_deps
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo  [OK] Python %PYVER%

echo  [..] Checking packages...
python -c "import flask" >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo  [..] Installing packages (first run only)...
    python -m pip install -r "%~dp0requirements.txt" flask flask-cors --quiet
    IF %ERRORLEVEL% NEQ 0 ( echo  [ERROR] pip failed. Try Run as Administrator. & pause & exit /b 1 )
    echo  [OK] Packages installed.
) ELSE (
    echo  [OK] Packages OK.
)

:: ── Test server.py imports before launching ────────────────────────────────────
echo  [..] Testing server imports...
cd /d "%~dp0"
python -c "import server" >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo  [ERROR] server.py failed to import. Running diagnostic...
    echo.
    python -c "import server"
    echo.
    pause
    exit /b 1
)
echo  [OK] Server imports OK.

:: ── Kill port 5000 ────────────────────────────────────────────────────────────
echo  [..] Clearing port 5000...
powershell -Command "Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"
echo  [OK] Port clear.

:: ── Open browser via python webbrowser after 4s delay ────────────────────────
echo  [..] Scheduling browser launch...
start "" python -c "import time,webbrowser; time.sleep(4); webbrowser.open('http://127.0.0.1:5000')"
echo  [OK] Browser will open in 4 seconds.

echo.
echo  ================================================
echo   Dashboard : http://localhost:5000
echo   Close this window to stop the server.
echo  ================================================
echo.

:: ── Run Flask in foreground ───────────────────────────────────────────────────
python server.py

echo.
echo  [!] Server stopped. See any errors above.
pause
