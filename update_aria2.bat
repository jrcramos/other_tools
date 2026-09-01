@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

title Update / Install aria2c (Turbo Download Accelerator)

echo ========================================================================
echo        aria2c Portable Installer ^& Updater (to .\bin\)
echo ========================================================================
echo.

set "scriptDir=%~dp0"
python "%scriptDir%update_aria2.py"

if errorlevel 1 (
    echo.
    echo [!] Installation encountered an issue.
) else (
    echo.
    echo [✓] aria2c is ready in .\bin\aria2c.exe!
)

echo.
pause
