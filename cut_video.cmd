@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: Get the directory where this script is located
set "scriptDir=%~dp0"

:: ========================================================================
:: CONFIGURATION SECTION - Customize these settings to your preference
:: ========================================================================
set "ffmpeg=C:\ffmpeg\bin\ffmpeg.exe"
:: ========================================================================
:: END CONFIGURATION SECTION
:: ========================================================================

:: Auto-detect ffmpeg if not found at configured location
if not exist "%ffmpeg%" (
    where ffmpeg >nul 2>&1
    if !errorlevel! equ 0 (
        set "ffmpeg=ffmpeg"
    ) else if exist "C:\Program Files\ffmpeg\bin\ffmpeg.exe" (
        set "ffmpeg=C:\Program Files\ffmpeg\bin\ffmpeg.exe"
    ) else if exist "%USERPROFILE%\ffmpeg\bin\ffmpeg.exe" (
        set "ffmpeg=%USERPROFILE%\ffmpeg\bin\ffmpeg.exe"
    ) else (
        echo ERROR: ffmpeg.exe not found!
        echo Please install ffmpeg or update the path in this script.
        pause
        exit /b
    )
)

:main_menu
cls
echo ========================================================================
echo                   FFmpeg Video Cutter / Trimmer v1.0
echo                 (Cut/Trim Videos Fast without Quality Loss)
echo ========================================================================
echo.
echo Drag and drop a video file into this window and press ENTER:
echo (or enter path to video file, 0 to exit)
echo.

set "inputFile="
set /p "inputFile=Video File path (or 0 to exit): "

if "!inputFile!"=="0" exit /b
if "!inputFile!"=="" goto main_menu

:: Clean and normalize path (strip spaces/quotes, fix slashes & missing drive colons)
call :clean_path "!inputFile!"
set "inputFile=!cleanPath!"

if not exist "!inputFile!" (
    echo.
    echo ERROR: File not found: "!inputFile!"
    pause
    goto main_menu
)

:: Extract folder, filename and extension
for %%F in ("!inputFile!") do (
    set "inputFolder=%%~dpF"
    set "inputName=%%~nF"
    set "inputExt=%%~xF"
)

cls
echo ========================================================================
echo Selected Video File: "!inputName!!inputExt!"
echo ========================================================================
echo.
echo Enter Start Time (HH:MM:SS or MM:SS or seconds, e.g. 00:11:05 or 70):
echo Press ENTER for start of video (00:00:00).
echo.
set "startTime="
set /p "startTime=Start Time [Default 00:00:00]: "
if "!startTime!"=="" set "startTime=00:00:00"

:: Clean startTime
call :clean_path "!startTime!"
set "startTime=!cleanPath!"

echo.
echo Select Cut Mode / End Specifier:
echo   1. End Timestamp (e.g. 00:15:30)
echo   2. Cut Duration  (e.g. 00:04:25 or 300)
echo   3. Cut until End of Video
echo.
set "cutOption="
set /p "cutOption=Select Option (1-3) [Default 1]: "
if "!cutOption!"=="" set "cutOption=1"

set "endParam="

if "!cutOption!"=="1" (
    echo.
    echo Enter End Timestamp (HH:MM:SS or MM:SS, e.g. 00:15:30):
    set "endTime="
    set /p "endTime=End Timestamp: "
    if not "!endTime!"=="" (
        call :clean_path "!endTime!"
        set "endParam=-to !cleanPath!"
    )
) else if "!cutOption!"=="2" (
    echo.
    echo Enter Duration length to keep (HH:MM:SS or seconds, e.g. 00:04:25 or 120):
    set "duration="
    set /p "duration=Duration: "
    if not "!duration!"=="" (
        call :clean_path "!duration!"
        set "endParam=-t !cleanPath!"
    )
)

echo.
echo Select Encoding Mode:
echo   1. Fast Cut (Stream Copy - Instant, no quality loss) [Default]
echo   2. Re-encode Video (Frame accurate, H.264 + Copy Audio)
echo.
set "encodeChoice="
set /p "encodeChoice=Choice (1-2) [Default 1]: "
if "!encodeChoice!"=="" set "encodeChoice=1"

set "codecParam=-c copy"
if "!encodeChoice!"=="2" (
    set "codecParam=-c:v libx264 -preset fast -crf 18 -c:a copy"
)

:: Prepare output filename
set "safeStart=!startTime::=-!"
set "outputFile=!inputFolder!!inputName!_cut_!safeStart!!inputExt!"

echo.
echo ========================================================================
echo Cutting Video...
echo Output File: "!outputFile!"
echo ========================================================================
echo.

"%ffmpeg%" -y -ss !startTime! !endParam! -i "!inputFile!" !codecParam! "!outputFile!"

if errorlevel 1 (
    echo.
    echo ERROR: Video cut failed!
    pause
    goto main_menu
)

echo.
echo ========================================================================
echo SUCCESS! Video cut created successfully.
echo Output: "!outputFile!"
echo ========================================================================
echo.
pause
goto main_menu


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
