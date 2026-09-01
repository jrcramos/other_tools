@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ========================================================================
::          Stream & Segment Tools Portable Updater / Installer
::                 (N_m3u8DL-RE, Streamlink, FFmpeg)
:: ========================================================================

set "SCRIPT_DIR=%~dp0"
set "PYTHON_SCRIPT=%SCRIPT_DIR%update_stream_tools.py"

:: Check if Python is available
where python >nul 2>&1
if %errorlevel% equ 0 (
    python "%PYTHON_SCRIPT%"
    goto finish
)

where py >nul 2>&1
if %errorlevel% equ 0 (
    py "%PYTHON_SCRIPT%"
    goto finish
)

if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe" (
    "%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe" "%PYTHON_SCRIPT%"
    goto finish
)

if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe" (
    "%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe" "%PYTHON_SCRIPT%"
    goto finish
)

echo [!] Python was not detected in PATH.
echo [!] Please install Python or run update_stream_tools.py directly.

:finish
echo.
pause
