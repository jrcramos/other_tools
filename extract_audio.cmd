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
echo                  FFmpeg Audio Extractor v1.0
echo           (Extract Audio Tracks / Clip Audio from Videos)
echo ========================================================================
echo.
echo Drag and drop video file(s) or a folder into this window:
echo You can enter multiple file paths (one per line).
echo Press ENTER on an empty line when done adding files (0 to exit).
echo.

set "fileListFile=%TEMP%\audio_ext_batch_%RANDOM%.txt"
if exist "%fileListFile%" del "%fileListFile%" >nul
set "fileCount=0"

:file_entry_loop
set "filePath="
set /p "filePath=Enter file or folder path (ENTER when done, 0 to exit): "

if "!filePath!"=="0" (
    if exist "%fileListFile%" del "%fileListFile%" >nul
    exit /b
)

if "!filePath!"=="" (
    if !fileCount! equ 0 (
        echo.
        echo No files entered. Please enter at least one file or folder path.
        echo.
        goto file_entry_loop
    ) else (
        goto options_menu
    )
)

:: Clean and normalize path (strip quotes/spaces, fix slashes & missing drive colons)
call :clean_path "!filePath!"
set "filePath=!cleanPath!"

if not exist "!filePath!" (
    echo.
    echo ERROR: File or folder not found: "!filePath!"
    echo.
    goto file_entry_loop
)

:: Check if path is a directory
if exist "!filePath!\*" (
    echo.
    echo Scanning folder for video files: "!filePath!"
    set "prevCount=!fileCount!"
    call :scan_folder_videos "!filePath!"
    set /a "addedCount=fileCount - prevCount"
    echo   + Added !addedCount! video file(s) from folder.
    echo Total files queued so far: !fileCount!
    echo.
    goto file_entry_loop
) else (
    echo !filePath!>> "%fileListFile%"
    set /a fileCount+=1
    for %%F in ("!filePath!") do echo   + Added: %%~nxF
    echo Total files queued so far: !fileCount!
    echo.
    goto file_entry_loop
)

:options_menu
cls
echo ========================================================================
echo               Audio Extraction Options (!fileCount! video(s))
echo ========================================================================
echo.
echo Select Output Audio Format:
echo   1. MP3 (VBR High Quality -q:a 2) [Default]
echo   2. MP3 (CBR 320 kbps High Quality)
echo   3. WAV (Lossless Uncompressed PCM 16-bit)
echo   4. AAC / M4A (High Quality Audio)
echo   5. Copy Original Audio Stream (-c:a copy)
echo.
set "fmtChoice="
set /p "fmtChoice=Select Format (1-5) [Default 1]: "
if "!fmtChoice!"=="" set "fmtChoice=1"

set "audioCodec="
set "audioExt=.mp3"

if "!fmtChoice!"=="1" (
    set "audioCodec=-vn -acodec libmp3lame -q:a 2"
    set "audioExt=.mp3"
) else if "!fmtChoice!"=="2" (
    set "audioCodec=-vn -acodec libmp3lame -b:a 320k"
    set "audioExt=.mp3"
) else if "!fmtChoice!"=="3" (
    set "audioCodec=-vn -acodec pcm_s16le"
    set "audioExt=.wav"
) else if "!fmtChoice!"=="4" (
    set "audioCodec=-vn -c:a aac -b:a 192k"
    set "audioExt=.m4a"
) else if "!fmtChoice!"=="5" (
    set "audioCodec=-vn -c:a copy"
    set "audioExt=.mka"
)

echo.
echo Enter Start Time (HH:MM:SS or MM:SS or seconds, e.g. 00:11:05):
echo Press ENTER to extract from start of video (00:00:00).
echo.
set "startTime="
set /p "startTime=Start Time [Default 00:00:00]: "
if "!startTime!"=="" set "startTime=00:00:00"

call :clean_path "!startTime!"
set "startTime=!cleanPath!"

echo.
echo Enter Duration / End Time (optional):
echo   - Leave BLANK (Press ENTER) to extract till end of video
echo   - Or enter End Time (e.g. 00:15:30) / Duration (e.g. 00:05:00)
echo.
set "endTime="
set /p "endTime=End Time / Duration [Optional]: "

set "timeParams="
if not "!startTime!"=="00:00:00" (
    set "timeParams=-ss !startTime!"
)
if not "!endTime!"=="" (
    call :clean_path "!endTime!"
    set "timeParams=!timeParams! -to !cleanPath!"
)

cls
echo ========================================================================
echo Starting Audio Extraction (!fileCount! video file(s))...
echo ========================================================================
echo.

set "successCount=0"
for /f "usebackq delims=" %%V in ("%fileListFile%") do (
    for %%F in ("%%V") do (
        set "vFolder=%%~dpF"
        set "vName=%%~nF"
    )
    
    if not "!startTime!"=="00:00:00" (
        set "safeStart=!startTime::=-!"
        set "outAudio=!vFolder!!vName!_audio_!safeStart!!audioExt!"
    ) else (
        set "outAudio=!vFolder!!vName!!audioExt!"
    )
    
    echo Processing: %%~nxV
    echo Output:     !outAudio!
    
    "%ffmpeg%" -y !timeParams! -i "%%V" !audioCodec! "!outAudio!" >nul 2>&1
    
    if errorlevel 1 (
        echo   [ERROR] Failed to extract audio for %%~nxV
    ) else (
        echo   [SUCCESS] Saved !outAudio!
        set /a successCount+=1
    )
    echo.
)

if exist "%fileListFile%" del "%fileListFile%" >nul

echo ========================================================================
echo COMPLETED: Successfully extracted audio for !successCount! / !fileCount! video(s).
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


:scan_folder_videos
:: Scans a directory recursively using parameter expansion for 'for /r'
for /r "%~1" %%V in (*.mp4 *.mkv *.avi *.mov *.webm *.m4v *.ts *.flv *.wmv) do (
    echo %%V>> "%fileListFile%"
    set /a fileCount+=1
    echo   + Added: %%~nxV
)
goto :eof
