@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo LARA for Android - Private WiFi server
where python >nul 2>&1
if errorlevel 1 (echo Python is required & pause & exit /b 1)
echo WARNING: Android connection exposes port 8765 on your trusted local network.
echo Do not run on public Wi-Fi. Do not open router ports.
set /p ANSWER=Allow local network access? type YES: 
if /I not "%ANSWER%"=="YES" exit /b 0
set LARA_LAN=1
ipconfig | findstr /i "IPv4"
python server.py
pause
