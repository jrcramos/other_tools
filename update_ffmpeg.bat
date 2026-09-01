@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: Configuration - Install directly inside portable .\bin\ folder
set "SCRIPT_DIR=%~dp0"
set "PARENT_DIR=%SCRIPT_DIR%bin"
set "TEMP_DIR=%TEMP%\ffmpeg_update_%RANDOM%"
set "ZIP_URL=https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z"
set "ZIP_FILE=%TEMP_DIR%\ffmpeg.7z"

echo ========================================================
echo       FFmpeg Git-Build Portable Updater / Installer
echo ========================================================
echo [*] Target Directory: %PARENT_DIR%
echo.

:: Ensure destination bin directory exists
if not exist "%PARENT_DIR%" mkdir "%PARENT_DIR%"

:: Create clean temp directory
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"

:: 1. Download the latest release .7z using PowerShell
echo [*] Downloading latest FFmpeg .7z package from Gyan.dev...
powershell -Command "$ProgressPreference = 'SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%ZIP_URL%' -OutFile '%ZIP_FILE%'"
if %ERRORLEVEL% neq 0 (
    echo [X] Error: Download failed.
    goto cleanup
)

:: 2. Download portable 7za.exe helper to extract the .7z archive natively
echo [*] Fetching 7z extraction helper...
powershell -Command "$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://www.7-zip.org/a/7zr.exe' -OutFile '%TEMP_DIR%\7zr.exe'"

:: 3. Extract the .7z package
echo [*] Extracting FFmpeg package contents...
"%TEMP_DIR%\7zr.exe" x "%ZIP_FILE%" -o"%TEMP_DIR%" -y > nul
if %ERRORLEVEL% neq 0 (
    echo [X] Error: Extraction failed.
    goto cleanup
)

:: 4. Locate the newly extracted root folder
set "EXTRACTED_ROOT="
for /d %%i in ("%TEMP_DIR%\*") do (
    if exist "%%i\bin" set "EXTRACTED_ROOT=%%i"
)

if "%EXTRACTED_ROOT%"=="" (
    echo [X] Error: Could not locate the extracted build folder structure.
    goto cleanup
)

:: 5. Copy binaries directly into .\bin\ for zero-config portability
echo [*] Installing binaries to %PARENT_DIR%...
if exist "%EXTRACTED_ROOT%\bin" (
    xcopy "%EXTRACTED_ROOT%\bin\*" "%PARENT_DIR%\" /Y /Q >nul
    if not exist "%PARENT_DIR%\bin" mkdir "%PARENT_DIR%\bin"
    xcopy "%EXTRACTED_ROOT%\bin\*" "%PARENT_DIR%\bin\" /Y /Q >nul
)

echo.
echo [^!] FFmpeg components installed successfully. Version info:
echo ----------------------------------------------------
if exist "%PARENT_DIR%\ffmpeg.exe" (
    "%PARENT_DIR%\ffmpeg.exe" -version | findstr /B "ffmpeg version"
) else if exist "%PARENT_DIR%\bin\ffmpeg.exe" (
    "%PARENT_DIR%\bin\ffmpeg.exe" -version | findstr /B "ffmpeg version"
)
echo ----------------------------------------------------

:cleanup
echo [*] Cleaning up temporary download files...
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
echo [*] Done.
pause