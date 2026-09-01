@echo off
setlocal enabledelayedexpansion

:input_loop
cls
echo ========================================================================
echo                   yt-dlp Video Downloader
echo ========================================================================
echo.
echo Tip: If you copied with [+ Ref] in Video Link Extractor, just paste it below.
echo.

set "videoUrl="
set "refererUrl="
set "fileName="

set /p "videoUrl=Enter video URL (or paste URL|Referer): "

:: Check if videoUrl is empty
if "!videoUrl!"=="" (
    echo.
    echo ERROR: Video URL is required!
    pause
    goto input_loop
)

:: Clean quotes
set "videoUrl=!videoUrl:"=!"

:: Auto-detect piped URL|Referer format from Video Link Extractor
for /f "tokens=1* delims=|" %%A in ("!videoUrl!") do (
    set "videoUrl=%%A"
    set "refererUrl=%%B"
)

if not "!refererUrl!"=="" (
    echo Auto-detected Referer: !refererUrl!
    echo.
)

set /p "fileName=Enter file name (optional, press Enter to use video title): "

:: Only prompt for referer if not already auto-detected from piped string
if "!refererUrl!"=="" (
    set /p "refererUrl=Enter Referer URL (optional, press Enter to skip): "
)

:: Set paths from environment variables, config_manager, or portable .\bin\
set "scriptDir=%~dp0"
set "saveLocation=C:\Users\joao3\Videos"
if exist "%scriptDir%config_manager.py" (
    for /f "delims=" %%D in ('python "%scriptDir%config_manager.py" --get-download-dir 2^>nul') do (
        if not "%%D"=="" set "saveLocation=%%D"
    )
)
set "cookies=C:\Users\joao3\Videos\yt-dlp-master"
if exist "%scriptDir%cookies" set "cookies=%scriptDir%cookies"

:: Auto-detect yt-dlp executable (prioritizing portable .\bin\)
set "ytDlpExe="
if exist "%scriptDir%bin\yt-dlp.exe" (
    set "ytDlpExe=%scriptDir%bin\yt-dlp.exe"
) else if exist "%scriptDir%yt-dlp.exe" (
    set "ytDlpExe=%scriptDir%yt-dlp.exe"
) else if exist "C:\Users\joao3\Videos\yt-dlp-master\yt-dlp.exe" (
    set "ytDlpExe=C:\Users\joao3\Videos\yt-dlp-master\yt-dlp.exe"
) else (
    where yt-dlp >nul 2>&1
    if !errorlevel! equ 0 (
        set "ytDlpExe=yt-dlp"
    ) else if exist "%USERPROFILE%\yt-dlp.exe" (
        set "ytDlpExe=%USERPROFILE%\yt-dlp.exe"
    )
)

:: Auto-detect ffmpeg (prioritizing portable .\bin\)
set "ffmpegLoc="
if exist "%scriptDir%bin\ffmpeg.exe" (
    set "ffmpegLoc=%scriptDir%bin"
) else if exist "%scriptDir%bin\ffmpeg\bin\ffmpeg.exe" (
    set "ffmpegLoc=%scriptDir%bin\ffmpeg\bin"
) else if exist "%scriptDir%ffmpeg.exe" (
    set "ffmpegLoc=%scriptDir%"
) else if exist "C:\ffmpeg\bin\ffmpeg.exe" (
    set "ffmpegLoc=C:\ffmpeg\bin"
) else if exist "C:\Program Files\ffmpeg\bin\ffmpeg.exe" (
    set "ffmpegLoc=C:\Program Files\ffmpeg\bin"
) else if exist "%USERPROFILE%\ffmpeg\bin\ffmpeg.exe" (
    set "ffmpegLoc=%USERPROFILE%\ffmpeg\bin"
) else (
    where ffmpeg >nul 2>&1
    if !errorlevel! equ 0 set "ffmpegLoc="
)

:: Set output filename template
if "!fileName!"=="" (
    set "outputTemplate=%saveLocation%\%%(title)s.%%(ext)s"
) else (
    set "outputTemplate=%saveLocation%\!fileName!.%%(ext)s" 
)

echo.
echo ========================================================================
echo Starting Download...
echo ========================================================================
echo.

:: Execute download command
if "!refererUrl!"=="" (
    "!ytDlpExe!" --newline -i --all-subs -o "!outputTemplate!" --ignore-config --hls-prefer-native -f bestvideo+bestaudio/b --cookies "%cookies%\chrome" --buffer-size 16k --no-warning --remux-video mp4 --audio-multistreams --sub-langs all --ffmpeg-location "!ffmpegLoc!" "!videoUrl!"
) else (
    "!ytDlpExe!" --newline -i --all-subs -o "!outputTemplate!" --add-header "Referer: !refererUrl!" --add-header "Origin: !refererUrl!" --add-header "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36" --ignore-config --hls-prefer-native -f bestvideo+bestaudio/b --buffer-size 16k --no-warning --remux-video mp4 --audio-multistreams --sub-langs all --ffmpeg-location "!ffmpegLoc!" "!videoUrl!"
)

echo.
echo ========================================================================
echo Download process completed.
echo ========================================================================
echo.
pause
goto input_loop
