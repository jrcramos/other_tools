@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ========================================================================
::          Universal Stream & Segmented Media Downloader Launcher
:: ========================================================================

set "scriptDir=%~dp0"
set "pythonScript=%scriptDir%stream_downloader.py"

:: Check if Python is installed
set "pythonExe="
where python >nul 2>&1
if !errorlevel! equ 0 (
    set "pythonExe=python"
) else (
    where py >nul 2>&1
    if !errorlevel! equ 0 (
        set "pythonExe=py"
    ) else if exist "C:\Python311\python.exe" (
        set "pythonExe=C:\Python311\python.exe"
    ) else if exist "C:\Python312\python.exe" (
        set "pythonExe=C:\Python312\python.exe"
    ) else if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe" (
        set "pythonExe=%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe"
    ) else if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe" (
        set "pythonExe=%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe"
    ) else (
        echo ERROR: Python is not installed or not found in system PATH.
        echo Please install Python 3.8+ from https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

:: Run Python script
"!pythonExe!" "!pythonScript!"

