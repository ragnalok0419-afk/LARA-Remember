@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist "server.py" (
 echo [ERROR] LARA_Enhanced\server.py not found. Extract the full ZIP first.
 pause
 exit /b 1
)
set "PY_CMD=python"
where python >nul 2>nul
if errorlevel 1 (
 where py >nul 2>nul
 if errorlevel 1 (
   echo [ERROR] Python is not installed. Install Python 3 from https://www.python.org/downloads/windows/
   pause
   exit /b 1
 )
 set "PY_CMD=py -3"
)
where ollama >nul 2>nul
if errorlevel 1 (
 echo [ERROR] Ollama was not found. Restart terminal or install Ollama.
 pause
 exit /b 1
)
echo Checking Qwen3 model...
ollama list | findstr /i "qwen3:1.7b" >nul
if errorlevel 1 (
 echo [ERROR] Model not found. In CMD run: ollama pull qwen3:1.7b
 pause
 exit /b 1
)
echo.
echo Launching LARA. This window must stay open.
echo Visit http://127.0.0.1:8765/ in your browser.
echo.
start "" cmd /c "timeout /t 3 /nobreak >nul & start http://127.0.0.1:8765/"
%PY_CMD% server.py
if errorlevel 1 (
 echo.
 echo [ERROR] Server exited. Check messages above.
)
pause
