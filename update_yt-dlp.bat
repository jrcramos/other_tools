@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "BIN_DIR=%SCRIPT_DIR%bin"
set "YT_DLP_EXE=%BIN_DIR%\yt-dlp.exe"

echo ========================================================
echo        yt-dlp Portable Updater / Installer
echo ========================================================
echo [*] Target Binary: %YT_DLP_EXE%
echo.

if not exist "%BIN_DIR%" mkdir "%BIN_DIR%"

if exist "%YT_DLP_EXE%" (
    echo [*] Updating existing yt-dlp binary...
    "%YT_DLP_EXE%" -U
) else (
    echo [*] yt-dlp.exe not found in .\bin\. Downloading latest release from GitHub...
    powershell -Command "$ProgressPreference = 'SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe' -OutFile '%YT_DLP_EXE%'"
    if !errorlevel! equ 0 (
        echo [+] SUCCESS: yt-dlp installed into .\bin\
    ) else (
        echo [X] Error: Failed to download yt-dlp.exe.
    )
)

if exist "%YT_DLP_EXE%" (
    echo.
    "%YT_DLP_EXE%" --version
)
echo.
pause