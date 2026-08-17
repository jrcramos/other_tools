@echo off
setlocal enabledelayedexpansion

:input_loop
cls
echo ========================================================================
echo               yt-dlp Video Downloader (Proxy Mode)
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

:: --- CONFIGURATION ---
set "ytDlp=C:\Users\joao3\Videos\yt-dlp-master"
set "cookies=C:\Users\joao3\Videos\yt-dlp-master"
set "saveLocation=C:\Users\joao3\Videos"
set "ffmpeg=C:\ffmpeg"

:: Define your SOCKS5 proxy here
set "myProxy=socks5://pvetbwz00882:lsp3hmupkzzu@lis.socks.privado.io:1080"
:: ---------------------

:: Auto-detect yt-dlp executable
set "ytDlpExe=!ytDlp!\yt-dlp.exe"
if not exist "!ytDlpExe!" (
    where yt-dlp >nul 2>&1
    if !errorlevel! equ 0 (
        set "ytDlpExe=yt-dlp"
    ) else if exist "%USERPROFILE%\yt-dlp.exe" (
        set "ytDlpExe=%USERPROFILE%\yt-dlp.exe"
    )
)

:: Auto-detect ffmpeg
set "ffmpegLoc=!ffmpeg!\bin"
if not exist "!ffmpegLoc!\ffmpeg.exe" (
    if exist "C:\Program Files\ffmpeg\bin\ffmpeg.exe" (
        set "ffmpegLoc=C:\Program Files\ffmpeg\bin"
    ) else if exist "%USERPROFILE%\ffmpeg\bin\ffmpeg.exe" (
        set "ffmpegLoc=%USERPROFILE%\ffmpeg\bin"
    )
)

:: Set output filename template
if "!fileName!"=="" (
    set "outputTemplate=%saveLocation%\%%(title)s.%%(ext)s"
) else (
    set "outputTemplate=%saveLocation%\!fileName!.%%(ext)s" 
)

echo.
echo ========================================================================
echo Starting Proxy Download via SOCKS5...
echo ========================================================================
echo.

:: Execute download command through proxy
if "!refererUrl!"=="" (
    "!ytDlpExe!" --proxy "%myProxy%" --newline -i --all-subs -o "!outputTemplate!" --ignore-config --hls-prefer-native -f bestvideo+bestaudio/b --cookies "%cookies%\chrome" --buffer-size 16k --no-warning --remux-video mp4 --audio-multistreams --sub-langs all --ffmpeg-location "!ffmpegLoc!" "!videoUrl!"
) else (
    "!ytDlpExe!" --proxy "%myProxy%" --newline -i --all-subs -o "!outputTemplate!" --add-header "Referer: !refererUrl!" --add-header "Origin: !refererUrl!" --add-header "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36" --ignore-config --hls-prefer-native -f bestvideo+bestaudio/b --buffer-size 16k --no-warning --remux-video mp4 --audio-multistreams --sub-langs all --ffmpeg-location "!ffmpegLoc!" "!videoUrl!"
)

echo.
echo ========================================================================
echo Download process completed.
echo ========================================================================
echo.
pause
goto input_loop