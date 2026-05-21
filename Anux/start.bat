@echo off
set VENV_DIR=venv
set PYTHON_PATH=%VENV_DIR%\Scripts\python.exe

python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo Python not found
        pause
        exit /b
    ) else (
        set BASE_PYTHON=py
    )
) else (
    set BASE_PYTHON=python
)

if not exist %VENV_DIR% (
    echo Creating Venv...
    %BASE_PYTHON% -m venv %VENV_DIR%
)

echo Installing requirements...
%PYTHON_PATH% -m pip install --upgrade pip --quiet
%PYTHON_PATH% -m pip install ultralytics torch torchvision numpy opencv-python pygame mss pywin32 --quiet

echo Launching...
%PYTHON_PATH% ai.py

pause
