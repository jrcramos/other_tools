@echo off
setlocal enabledelayedexpansion

:: ========================================================================
:: CONFIGURATION SECTION - Customize these settings to your preference
:: ========================================================================

:: Path to ffmpeg.exe (will auto-detect if not found at specified location)
:: You can change this to your ffmpeg installation path if needed
set "ffmpeg=C:\ffmpeg\bin\ffmpeg.exe"

:: ========================================================================
:: END CONFIGURATION SECTION
:: ========================================================================

:: Auto-detect ffmpeg if not found at the configured location
if not exist "%ffmpeg%" (
    echo INFO: ffmpeg not found at "%ffmpeg%"
    echo Attempting to auto-detect ffmpeg...
    
    :: Check if ffmpeg is in PATH
    where ffmpeg >nul 2>&1
    if !errorlevel! equ 0 (
        set "ffmpeg=ffmpeg"
        echo SUCCESS: Found ffmpeg in system PATH
    ) else (
        :: Check common installation locations
        if exist "C:\Program Files\ffmpeg\bin\ffmpeg.exe" (
            set "ffmpeg=C:\Program Files\ffmpeg\bin\ffmpeg.exe"
            echo SUCCESS: Found ffmpeg at C:\Program Files\ffmpeg\bin\ffmpeg.exe
        ) else if exist "%USERPROFILE%\ffmpeg\bin\ffmpeg.exe" (
            set "ffmpeg=%USERPROFILE%\ffmpeg\bin\ffmpeg.exe"
            echo SUCCESS: Found ffmpeg at %USERPROFILE%\ffmpeg\bin\ffmpeg.exe
        ) else (
            echo ERROR: ffmpeg not found!
            echo.
            echo Please install ffmpeg and either:
            echo   1. Add it to your system PATH, or
            echo   2. Update the ffmpeg path in this script's CONFIGURATION SECTION
            echo.
            echo Download ffmpeg from: https://ffmpeg.org/download.html
            pause
            exit /b
        )
    )
)

:main_loop
cls
echo ================================
echo    FFmpeg Video Converter v1.0
echo ================================
echo.
echo Select target resolution:
echo   1. 360p  (640x360)
echo   2. 480p  (854x480)
echo   3. 720p  (1280x720)
echo   4. 1080p (1920x1080)
echo   5. Exit
echo.

set "choice="
set /p "choice=Enter your choice (1-5): "

if "%choice%"=="1" (
    set "resolution=360"
    set "scaleHeight=360"
) else if "%choice%"=="2" (
    set "resolution=480"
    set "scaleHeight=480"
) else if "%choice%"=="3" (
    set "resolution=720"
    set "scaleHeight=720"
) else if "%choice%"=="4" (
    set "resolution=1080"
    set "scaleHeight=1080"
) else if "%choice%"=="5" (
    exit /b
) else (
    echo Invalid choice. Please try again.
    timeout /t 2 >nul
    goto main_loop
)

echo.
echo Selected resolution: !resolution!p
echo.
echo Please drag and drop your video file here and press ENTER:
echo (or type/paste the full path to the video file)
echo.

set "inputFile="
set /p "inputFile=File path: "

:: Clean and normalize path (strip quotes/spaces, fix slashes & missing drive colons)
call :clean_path "!inputFile!"
set "inputFile=!cleanPath!"

:: Check if file exists
if "!inputFile!"=="" (
    echo No file specified. Returning to main menu...
    timeout /t 2 >nul
    goto main_loop
)

if not exist "!inputFile!" (
    echo ERROR: File not found: "!inputFile!"
    echo Please check the path and try again.
    pause
    goto main_loop
)

:: Extract file name without extension and get the extension
for %%F in ("!inputFile!") do (
    set "fileName=%%~nF"
    set "fileExt=%%~xF"
    set "fileDir=%%~dpF"
)

:: Remove the leading dot from extension if present
set "fileExt=!fileExt:~1!"

:: Define output file path
set "outputFile=!fileDir!!fileName!_!resolution!p.!fileExt!"

:: Check if output file already exists
if exist "!outputFile!" (
    echo.
    echo WARNING: Output file already exists: "!outputFile!"
    set "overwrite="
    set /p "overwrite=Overwrite? (Y/N): "
    if /i not "!overwrite!"=="Y" (
        echo Conversion cancelled.
        pause
        goto main_loop
    )
)

echo.
echo ================================
echo Starting video conversion...
echo ================================
echo Input:      !inputFile!
echo Output:     !outputFile!
echo Resolution: !resolution!p
echo.
echo Please wait, this may take several minutes depending on the video size...
echo.

:: Run ffmpeg conversion with scale filter
"%ffmpeg%" -i "!inputFile!" -vf scale=-2:!scaleHeight! -c:a copy "!outputFile!"

if errorlevel 1 (
    echo.
    echo ERROR: Video conversion failed.
    echo Please check that the input file is a valid video file.
    pause
    goto main_loop
)

echo.
echo ================================
echo SUCCESS! Conversion complete.
echo ================================
echo Output saved to: "!outputFile!"
echo.
pause
goto main_loop


:: ========================================================================
:: HELPER SUBROUTINES
:: ========================================================================

:clean_path
set "cleanPath=%~1"
if not defined cleanPath set "cleanPath=%*"
if not defined cleanPath goto :eof

:: 1. Remove quotes
set "cleanPath=!cleanPath:"=!"
set "cleanPath=!cleanPath:'=!"

:: 2. Trim leading spaces
:clean_path_trim_lead
if "!cleanPath:~0,1!"==" " (
    set "cleanPath=!cleanPath:~1!"
    goto clean_path_trim_lead
)

:: 3. Trim trailing spaces
:clean_path_trim_trail
if "!cleanPath:~-1!"==" " (
    set "cleanPath=!cleanPath:~0,-1!"
    goto clean_path_trim_trail
)

:: 4. Replace forward slashes with backslashes
set "cleanPath=!cleanPath:/=\!"

:: 5. Fix missing drive colon: e.g. "c\folder" -> "c:\folder"
if "!cleanPath:~1,1!"=="\" (
    set "driveLetter=!cleanPath:~0,1!"
    echo !driveLetter!| findstr /i "[a-z]" >nul
    if !errorlevel! equ 0 set "cleanPath=!driveLetter!:\!cleanPath:~2!"
)

:: 6. Remove trailing backslash if not root (e.g. "C:\folder\" -> "C:\folder")
if not "!cleanPath:~1!"==":\" if "!cleanPath:~-1!"=="\" set "cleanPath=!cleanPath:~0,-1!"
goto :eof

