@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: Get the directory where this script is located
set "scriptDir=%~dp0"

:: ========================================================================
:: CONFIGURATION SECTION - Customize these settings to your preference
:: ========================================================================
set "ffmpeg=C:\ffmpeg\bin\ffmpeg.exe"
set "ffprobe=C:\ffmpeg\bin\ffprobe.exe"
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

:: Auto-detect ffprobe
if not exist "%ffprobe%" (
    where ffprobe >nul 2>&1
    if !errorlevel! equ 0 (
        set "ffprobe=ffprobe"
    ) else if exist "C:\Program Files\ffmpeg\bin\ffprobe.exe" (
        set "ffprobe=C:\Program Files\ffmpeg\bin\ffprobe.exe"
    ) else if exist "%USERPROFILE%\ffmpeg\bin\ffprobe.exe" (
        set "ffprobe=%USERPROFILE%\ffmpeg\bin\ffprobe.exe"
    ) else (
        set "ffprobe="
    )
)

:main_menu
cls
echo ========================================================================
echo               FFmpeg Video Snapshots ^& Contact Sheet Maker v1.0
echo            (Create Thumbnail Grids, Frame Extracts, or Single Stills)
echo ========================================================================
echo.
echo Drag and drop a video file into this window and press ENTER:
echo (or enter path to video file, 0 to exit)
echo.

set "inputFile="
set /p "inputFile=Video File path (or 0 to exit): "

if "!inputFile!"=="0" exit /b
if "!inputFile!"=="" goto main_menu

:: Clean and normalize path
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
echo Select Snapshot Mode:
echo   1. Contact Sheet / Thumbnail Grid (Single composite image preview)
echo   2. Extract Frames at Intervals (e.g. 1 image every 5s, 10s, 30s)
echo   3. Single Still Frame at Specific Timestamp (e.g. 00:02:15)
echo   0. Back to Main Menu
echo.

set "modeChoice="
set /p "modeChoice=Select Option (1-3) [Default 1]: "
if "!modeChoice!"=="" set "modeChoice=1"
if "!modeChoice!"=="0" goto main_menu

if "!modeChoice!"=="1" goto mode_contact_sheet
if "!modeChoice!"=="2" goto mode_interval_extract
if "!modeChoice!"=="3" goto mode_single_still

echo Invalid choice.
timeout /t 2 >nul
goto main_menu


:: ========================================================================
:: MODE 1: CONTACT SHEET / THUMBNAIL GRID
:: ========================================================================
:mode_contact_sheet
cls
echo ========================================================================
echo Mode: Contact Sheet / Thumbnail Grid
echo Video: "!inputName!!inputExt!"
echo ========================================================================
echo.
echo Select Grid Layout:
echo   1. 3x3 Grid  (9  Thumbnails) [Default]
echo   2. 4x4 Grid  (16 Thumbnails)
echo   3. 2x2 Grid  (4  Thumbnails - Quick glance)
echo   4. 5x5 Grid  (25 Thumbnails - Detailed index)
echo.

set "gridChoice="
set /p "gridChoice=Select Grid (1-4) [Default 1]: "
if "!gridChoice!"=="" set "gridChoice=1"

set "cols=3"
set "rows=3"
set "totalFrames=9"
set "thumbWidth=480"

if "!gridChoice!"=="2" (
    set "cols=4"
    set "rows=4"
    set "totalFrames=16"
    set "thumbWidth=400"
) else if "!gridChoice!"=="3" (
    set "cols=2"
    set "rows=2"
    set "totalFrames=4"
    set "thumbWidth=640"
) else if "!gridChoice!"=="4" (
    set "cols=5"
    set "rows=5"
    set "totalFrames=25"
    set "thumbWidth=360"
)

echo.
echo Timestamp Overlay on Thumbnails:
echo   1. Yes (Show HH:MM:SS on each frame) [Default]
echo   2. No  (Clean frames only)
echo.
set "timeChoice="
set /p "timeChoice=Include Timestamps (1-2) [Default 1]: "
if "!timeChoice!"=="" set "timeChoice=1"

:: Calculate video duration if ffprobe is available
set "durationSec=0"
if defined ffprobe (
    for /f "tokens=1 delims=." %%a in ('"%ffprobe%" -v error -show_entries format^=duration -of default^=noprint_wrappers^=1:nokey^=1 "!inputFile!" 2^>nul') do (
        set "durationSec=%%a"
    )
)

:: Calculate interval based on duration
set /a "stepSec=10"
if !durationSec! gtr 0 (
    set /a "numIntervals=!totalFrames! + 1"
    set /a "stepSec=!durationSec! / !numIntervals!"
    if !stepSec! leq 0 set "stepSec=1"
)

:: Build drawtext filter if requested
set "fontOption="
if exist "C:\Windows\Fonts\arial.ttf" (
    set "fontOption=:fontfile='C\:/Windows/Fonts/arial.ttf'"
) else if exist "C:\Windows\Fonts\segoeui.ttf" (
    set "fontOption=:fontfile='C\:/Windows/Fonts/segoeui.ttf'"
)

set "drawtextFilter="
if "!timeChoice!"=="1" (
    set "drawtextFilter=,drawtext=text='%%{pts\:hms}'!fontOption!:fontsize=16:fontcolor=white:box=1:boxcolor=black@0.65:boxborderw=4:x=w-tw-8:y=h-th-8"
)

set "outputFile=!inputFolder!!inputName!_grid_!cols!x!rows!.jpg"

echo.
echo ========================================================================
echo Generating !cols!x!rows! Contact Sheet...
echo Output File: "!outputFile!"
echo ========================================================================
echo.

"%ffmpeg%" -y -i "!inputFile!" -vf "fps=1/!stepSec!,scale=!thumbWidth!:-1!drawtextFilter!,tile=!cols!x!rows!" -frames:v 1 -q:v 2 "!outputFile!"

if errorlevel 1 (
    echo.
    echo Retrying without drawtext filter in case font engine failed...
    "%ffmpeg%" -y -i "!inputFile!" -vf "fps=1/!stepSec!,scale=!thumbWidth!:-1,tile=!cols!x!rows!" -frames:v 1 -q:v 2 "!outputFile!"
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to generate contact sheet!
        pause
        goto main_menu
    )
)

echo.
echo ========================================================================
echo SUCCESS! Contact sheet created successfully.
echo Saved to: "!outputFile!"
echo ========================================================================
echo.
pause
goto main_menu


:: ========================================================================
:: MODE 2: EXTRACT FRAMES AT INTERVALS
:: ========================================================================
:mode_interval_extract
cls
echo ========================================================================
echo Mode: Extract Frames at Intervals
echo Video: "!inputName!!inputExt!"
echo ========================================================================
echo.
echo Enter interval between frame snapshots in seconds:
echo (e.g. 5 for every 5s, 10 for every 10s, 60 for every minute)
echo.
set "interval="
set /p "interval=Interval in seconds [Default 10]: "
if "!interval!"=="" set "interval=10"

call :clean_path "!interval!"
set "interval=!cleanPath!"

echo.
echo Select Output Image Format:
echo   1. JPG (High quality, compact) [Default]
echo   2. PNG (Lossless)
echo.
set "imgFormat="
set /p "imgFormat=Select Format (1-2) [Default 1]: "
if "!imgFormat!"=="" set "imgFormat=1"

set "imgExt=jpg"
set "qParam=-q:v 2"
if "!imgFormat!"=="2" (
    set "imgExt=png"
    set "qParam="
)

set "outputDir=!inputFolder!!inputName!_frames"
if not exist "!outputDir!" mkdir "!outputDir!"

echo.
echo ========================================================================
echo Extracting frames every !interval! seconds...
echo Output Directory: "!outputDir!"
echo ========================================================================
echo.

"%ffmpeg%" -y -i "!inputFile!" -vf "fps=1/!interval!" !qParam! "!outputDir!\frame_%%04d.!imgExt!"

if errorlevel 1 (
    echo.
    echo ERROR: Frame extraction failed!
    pause
    goto main_menu
)

echo.
echo ========================================================================
echo SUCCESS! Frames extracted successfully.
echo Saved in: "!outputDir!"
echo ========================================================================
echo.
pause
goto main_menu


:: ========================================================================
:: MODE 3: SINGLE STILL FRAME AT TIMESTAMP
:: ========================================================================
:mode_single_still
cls
echo ========================================================================
echo Mode: Single Still Frame at Specific Timestamp
echo Video: "!inputName!!inputExt!"
echo ========================================================================
echo.
echo Enter timestamp to capture (HH:MM:SS or MM:SS or seconds, e.g. 00:02:15 or 45):
echo.
set "stillTime="
set /p "stillTime=Timestamp [Default 00:00:01]: "
if "!stillTime!"=="" set "stillTime=00:00:01"

call :clean_path "!stillTime!"
set "stillTime=!cleanPath!"

set "safeTime=!stillTime::=-!"
set "outputFile=!inputFolder!!inputName!_still_!safeTime!.jpg"

echo.
echo ========================================================================
echo Capturing Still Frame at !stillTime!...
echo Output File: "!outputFile!"
echo ========================================================================
echo.

"%ffmpeg%" -y -ss !stillTime! -i "!inputFile!" -frames:v 1 -q:v 2 "!outputFile!"

if errorlevel 1 (
    echo.
    echo ERROR: Still frame capture failed!
    pause
    goto main_menu
)

echo.
echo ========================================================================
echo SUCCESS! Still frame captured successfully.
echo Saved to: "!outputFile!"
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
