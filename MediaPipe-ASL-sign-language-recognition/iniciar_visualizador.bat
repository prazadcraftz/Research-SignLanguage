@echo off
setlocal
cd /d "%~dp0"
echo Starting ASL translator with filter visualizer...

if exist ".\.venv\Scripts\activate.bat" (
    call .\.venv\Scripts\activate.bat
) else if exist ".\venv312\Scripts\activate.bat" (
    call .\venv312\Scripts\activate.bat
)

python realtime_translator.py --activations
if errorlevel 1 pause
endlocal

