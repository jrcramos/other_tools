@echo off
setlocal enabledelayedexpansion

:input_loop
echo ================================
echo  YouTube Downloader Script
echo ================================
echo.
set /p videoUrl="Enter video URL: "
set /p fileName="Enter file name (optional, press Enter to use video title): "
set /p refererUrl="Enter Referer URL (optional, press Enter to skip): "

:: --- CONFIGURATION ---
set "ytDlp=C:\Users\joao3\Videos\yt-dlp-master"
set "cookies=C:\Users\joao3\Videos\yt-dlp-master"
set "saveLocation=C:\Users\joao3\Videos"
set "ffmpeg=C:\ffmpeg"

:: Define your SOCKS5 proxy here
:: Format: socks5://user:password@host:port OR socks5://host:port
set "myProxy=socks5://pvetbwz00882:lsp3hmupkzzu@lis.socks.privado.io:1080" 
:: ---------------------

if "%fileName%"=="" (
    set "outputTemplate=%saveLocation%\%%(title)s.%%(ext)s"
) else (
    set "outputTemplate=%saveLocation%\%fileName%.%%(ext)s" 
)

if "%videoUrl%"=="" (
    echo ERROR: Video URL is required!
    pause >nul
    goto input_loop
)

if "%refererUrl%"=="" (
    echo Running first download command...
    "%ytDlp%\yt-dlp.exe" --proxy "%myProxy%" --newline -i --all-subs -o "!outputTemplate!" --ignore-config --hls-prefer-native -f bestvideo+bestaudio/b --cookies "%cookies%\chrome" --buffer-size 16k --no-warning --remux-video mp4 --ffmpeg-location "%ffmpeg%\bin" "%videoUrl%"
) else (
    echo Running second download command...
    "%ytDlp%\yt-dlp.exe" --proxy "%myProxy%" -o "!outputTemplate!" --add-header "Referer: %refererUrl%" --add-header "Origin: %refererUrl%" --add-header "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36" "%videoUrl%"
)

echo.
echo Download process completed.
goto input_loop