@echo off
setlocal
cd /d "%~dp0"

echo ======================================================================
echo Launching Edge-ASL Real-Time Sign Language Translator...
echo ======================================================================

set "VENV_PY=%~dp0MediaPipe-ASL-sign-language-recognition\.venv\Scripts\python.exe"

if exist "%VENV_PY%" (
    echo [INFO] Using virtual environment Python: %VENV_PY%
    "%VENV_PY%" "%~dp0run_translator.py" %*
) else (
    echo [INFO] Virtual environment not found at default path, using system Python...
    python "%~dp0run_translator.py" %*
)

if errorlevel 1 (
    echo.
    echo [ERROR] Translator exited with error code %errorlevel%.
    pause
)
endlocal
