@echo off
:: Check for Admin Privileges
::net session >nul 2>&1
::if %errorLevel% neq 0 (
::    echo Requesting administrative privileges...
::    powershell -Command "Start-Process '%0' -Verb RunAs"
::    exit /b
::)

setlocal enabledelayedexpansion

:input_loop
:: cls
echo ================================
echo  YouTube Downloader Script
echo ================================
echo.
set /p videoUrl="Enter video URL: "
set /p fileName="Enter file name (optional, press Enter to use video title): "
set /p refererUrl="Enter Referer URL (optional, press Enter to skip): "


:: Set paths from environment variables or manually
set "ytDlp=C:\Users\joao3\Videos\yt-dlp-master"
set "cookies=C:\Users\joao3\Videos\yt-dlp-master"
set "saveLocation=C:\Users\joao3\Videos"
set "ffmpeg=C:\ffmpeg"

:: Set output filename template
if "%fileName%"=="" (
    set "outputTemplate=%saveLocation%\%%(title)s.%%(ext)s"
) else (
    set "outputTemplate=%saveLocation%\%fileName%.%%(ext)s" 
)


:: Check if videoUrl is empty (required field)
if "%videoUrl%"=="" (
    echo.
    echo ERROR: Video URL is required!
    echo Press any key to retry...
    pause >nul
    goto input_loop
)


:: Check if refererUrl is provided
if "%refererUrl%"=="" (
    echo Running first download command...
    "%ytDlp%\yt-dlp.exe" --newline -i --all-subs -o "!outputTemplate!" --ignore-config --hls-prefer-native -f bestvideo+bestaudio/b --cookies "%cookies%\chrome" --buffer-size 16k --no-warning --remux-video mp4 --audio-multistreams --sub-langs all --ffmpeg-location "%ffmpeg%\bin" "%videoUrl%"
) else (
    echo Running second download command...
    "%ytDlp%\yt-dlp.exe" -o "!outputTemplate!" --add-header "Referer: %refererUrl%" --add-header "Origin: %refererUrl%" --add-header "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36" "%videoUrl%"
)

echo.
echo Download process completed.
echo Press any key to download another video...
:: pause >nul
goto input_loop


