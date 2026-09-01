@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: Get the directory where this script is located
set "scriptDir=%~dp0"
cd /d "%scriptDir%"

:: Check if Python is installed
where python >nul 2>&1
if !errorlevel! neq 0 (
    echo.
    echo ERROR: Python is not found in your system PATH!
    echo Please install Python 3.10+ and make sure to check "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

:: Check if CustomTkinter is installed
python -c "import customtkinter" >nul 2>&1
if !errorlevel! neq 0 (
    echo.
    echo ========================================================================
    echo  First-time Setup: Installing CustomTkinter and UI dependencies...
    echo ========================================================================
    echo.
    pip install -r "%scriptDir%requirements.txt"
    if !errorlevel! neq 0 (
        echo.
        echo ERROR: Failed to install requirements. Please check your internet connection.
        echo.
        pause
        exit /b 1
    )
    echo.
    echo Dependencies installed successfully!
    echo.
)

:: Launch the CustomTkinter Desktop Hub
start "" python "%scriptDir%app.py"
