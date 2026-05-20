@echo off
set VENV_DIR=venv

python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo Python not found
        pause
        exit /b
    ) else (
        set PYTHON_CMD=py
    )
) else (
    set PYTHON_CMD=python
)

if not exist %VENV_DIR% (
    echo Venv...
    %PYTHON_CMD% -m venv %VENV_DIR%
)

call %VENV_DIR%\Scripts\activate.bat

echo Pip...
python -m pip install --upgrade pip --quiet
pip install ultralytics torch torchvision numpy opencv-python pygame mss pywin32 --quiet
echo Launch...
python ai.py

pause
