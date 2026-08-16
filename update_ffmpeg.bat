@echo off
setlocal enabledelayedexpansion

:: Configuration
set "PARENT_DIR=C:\ffmpeg"
set "TEMP_DIR=%TEMP%\ffmpeg_update"
set "ZIP_URL=https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z"
set "ZIP_FILE=%TEMP_DIR%\ffmpeg.7z"

echo ============================================
echo       FFmpeg Git-Build Multi-Updater
echo ============================================
echo.

:: Create a clean temp directory
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"

:: 1. Download the latest release .7z using PowerShell (Progress hidden for speed)
echo [*] Downloading latest FFmpeg .7z package...
powershell -Command "$ProgressPreference = 'SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%ZIP_URL%' -OutFile '%ZIP_FILE%'"
if %ERRORLEVEL% neq 0 (
    echo [X] Error: Download failed.
    goto cleanup
)

:: 2. Download a portable 7za.exe helper to extract the .7z archive natively
echo [*] Fetching extraction helper...
powershell -Command "$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://www.7-zip.org/a/7zr.exe' -OutFile '%TEMP_DIR%\7zr.exe'"

:: 3. Extract the .7z package
echo [*] Extracting .7z package contents...
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

:: 5. Safely swap /bin, /presets, and /doc
echo [*] Syncing folders to %PARENT_DIR%...

:: Update /bin
if exist "%EXTRACTED_ROOT%\bin" (
    echo     - Updating bin...
    if not exist "%PARENT_DIR%\bin" mkdir "%PARENT_DIR%\bin"
    xcopy "%EXTRACTED_ROOT%\bin\*" "%PARENT_DIR%\bin\" /Y /Q
)

:: Update /presets
if exist "%EXTRACTED_ROOT%\presets" (
    echo     - Updating presets...
    if not exist "%PARENT_DIR%\presets" mkdir "%PARENT_DIR%\presets"
    xcopy "%EXTRACTED_ROOT%\presets\*" "%PARENT_DIR%\presets\" /Y /Q
)

:: Update /doc
if exist "%EXTRACTED_ROOT%\doc" (
    echo     - Updating doc...
    if not exist "%PARENT_DIR%\doc" mkdir "%PARENT_DIR%\doc"
    xcopy "%EXTRACTED_ROOT%\doc\*" "%PARENT_DIR%\doc\" /Y /Q
)

echo.
echo [^!] FFmpeg components updated successfully. New version info:
echo ----------------------------------------------------
"%PARENT_DIR%\bin\ffmpeg.exe" -version | findstr /B "ffmpeg version"
echo ----------------------------------------------------

:cleanup
echo [*] Cleaning up temporary download files...
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
echo [*] Done.
pause