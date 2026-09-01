@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: Get the directory where this script is located
set "scriptDir=%~dp0"

:: ========================================================================
:: CONFIGURATION SECTION - Customize these settings to your preference
:: ========================================================================
set "ytDlp=C:\Users\joao3\Videos\yt-dlp-master"
set "cookies=C:\Users\joao3\Videos\yt-dlp-master"
set "ffmpeg=C:\ffmpeg"
set "defaultSaveLocation=%USERPROFILE%\Music"
:: ========================================================================
:: END CONFIGURATION SECTION
:: ========================================================================

:: Auto-detect yt-dlp executable
set "ytDlpExe=!ytDlp!\yt-dlp.exe"
if not exist "!ytDlpExe!" (
    where yt-dlp >nul 2>&1
    if !errorlevel! equ 0 (
        set "ytDlpExe=yt-dlp"
    ) else if exist "%USERPROFILE%\yt-dlp.exe" (
        set "ytDlpExe=%USERPROFILE%\yt-dlp.exe"
    ) else if exist "%scriptDir%yt-dlp.exe" (
        set "ytDlpExe=%scriptDir%yt-dlp.exe"
    ) else (
        echo.
        echo ERROR: yt-dlp.exe not found!
        echo Please ensure yt-dlp is installed or run update_yt-dlp.bat first.
        echo.
        pause
        exit /b
    )
)

:: Auto-detect ffmpeg
set "ffmpegLoc=!ffmpeg!\bin"
if not exist "!ffmpegLoc!\ffmpeg.exe" (
    where ffmpeg >nul 2>&1
    if !errorlevel! equ 0 (
        set "ffmpegLoc="
    ) else if exist "C:\Program Files\ffmpeg\bin\ffmpeg.exe" (
        set "ffmpegLoc=C:\Program Files\ffmpeg\bin"
    ) else if exist "%USERPROFILE%\ffmpeg\bin\ffmpeg.exe" (
        set "ffmpegLoc=%USERPROFILE%\ffmpeg\bin"
    ) else if exist "%scriptDir%ffmpeg.exe" (
        set "ffmpegLoc=%scriptDir%"
    )
)

:: Ensure default save directory exists
if not exist "%defaultSaveLocation%" mkdir "%defaultSaveLocation%" >nul 2>&1

:: Check if URL or file was passed as argument or dragged onto script icon
if not "%~1"=="" (
    set "inputUrl=%~1"
    goto parse_input_target
)

:main_menu
cls
echo ========================================================================
echo                  yt-dlp Audio ^& Music Downloader v1.0
echo       (Download High-Bitrate Audio with Metadata, Cover Art ^& Tags)
echo ========================================================================
echo.
echo Tip: Paste a URL, a piped "URL|Referer", or drag-and-drop a .txt list of URLs.
echo.

set "inputUrl="
set "refererUrl="
set "fileName="
set "isBatchFile=0"

set /p "inputUrl=Enter URL or drag .txt file (0 to exit): "

if "!inputUrl!"=="0" exit /b
if "!inputUrl!"=="" goto main_menu

:parse_input_target

:: Clean quotes
set "inputUrl=!inputUrl:"=!"
set "inputUrl=!inputUrl:'=!"

:: Check if input is a text file
if exist "!inputUrl!" (
    for %%F in ("!inputUrl!") do (
        if /i "%%~xF"==".txt" (
            set "isBatchFile=1"
            set "batchFilePath=!inputUrl!"
            echo.
            echo Detected URL batch file: "!batchFilePath!"
            goto format_selection
        )
    )
)

:: Auto-detect piped URL|Referer format
for /f "tokens=1* delims=|" %%A in ("!inputUrl!") do (
    set "inputUrl=%%A"
    set "refererUrl=%%B"
)

if not "!refererUrl!"=="" (
    echo Auto-detected Referer: !refererUrl!
)

:format_selection
echo.
echo ========================================================================
echo Select Audio Output Format:
echo ========================================================================
echo   1. MP3  - Best Quality (VBR ~320 kbps) [Recommended]
echo   2. MP3  - Balanced / Compact (CBR 192 kbps)
echo   3. M4A  - AAC Best Quality (Apple / iTunes / Mobile Compatible)
echo   4. FLAC - Lossless Studio Quality (Archival / Highest Fidelity)
echo   5. OPUS - Next-Gen High Efficiency (160 kbps, Superior Quality/Size)
echo   6. WAV  - Uncompressed PCM Audio
echo   7. Best Original Audio (Direct extraction, No re-encoding)
echo   0. Back to Main Menu
echo.

set "formatChoice="
set /p "formatChoice=Select Format (1-7) [Default 1]: "
if "!formatChoice!"=="" set "formatChoice=1"
if "!formatChoice!"=="0" goto main_menu

set "audioExt=mp3"
set "audioQuality=0"
set "audioArgs=--extract-audio --audio-format mp3 --audio-quality 0"

if "!formatChoice!"=="1" (
    set "audioExt=mp3"
    set "audioArgs=--extract-audio --audio-format mp3 --audio-quality 0"
) else if "!formatChoice!"=="2" (
    set "audioExt=mp3"
    set "audioArgs=--extract-audio --audio-format mp3 --audio-quality 192K"
) else if "!formatChoice!"=="3" (
    set "audioExt=m4a"
    set "audioArgs=--extract-audio --audio-format m4a --audio-quality 0"
) else if "!formatChoice!"=="4" (
    set "audioExt=flac"
    set "audioArgs=--extract-audio --audio-format flac --audio-quality 0"
) else if "!formatChoice!"=="5" (
    set "audioExt=opus"
    set "audioArgs=--extract-audio --audio-format opus --audio-quality 0"
) else if "!formatChoice!"=="6" (
    set "audioExt=wav"
    set "audioArgs=--extract-audio --audio-format wav"
) else if "!formatChoice!"=="7" (
    set "audioExt=best"
    set "audioArgs=--extract-audio --audio-quality 0"
)

:: Metadata & Thumbnail embedding options
echo.
echo ========================================================================
echo Embed Cover Art ^& Metadata:
echo ========================================================================
echo   1. Yes - Embed Thumbnail Art, Artist, Title, Album ^& Tags [Default]
echo   2. No  - Basic Audio Download Only
echo.

set "metaChoice="
set /p "metaChoice=Select Option (1-2) [Default 1]: "
if "!metaChoice!"=="" set "metaChoice=1"

set "metaArgs=--embed-metadata --embed-chapters"
if "!metaChoice!"=="1" (
    set "metaArgs=--embed-thumbnail --embed-metadata --embed-chapters --convert-thumbnails jpg"
) else (
    set "metaArgs="
)

:: Chapter Splitting option
set "splitArgs="
if "!isBatchFile!"=="0" (
    echo.
    echo Split video into separate tracks by chapters if available?
    echo   1. No  - Single full audio file [Default]
    echo   2. Yes - Split into multiple files per chapter
    echo.
    set /p "splitChoice=Select Option (1-2) [Default 1]: "
    if "!splitChoice!"=="2" (
        set "splitArgs=--split-chapters"
    )
)

:: Destination folder
echo.
echo Save Directory (Press ENTER for: "%defaultSaveLocation%"):
set "customSave="
set /p "customSave=Enter path or press ENTER: "
if "!customSave!"=="" (
    set "saveLocation=%defaultSaveLocation%"
) else (
    set "customSave=!customSave:"=!"
    set "saveLocation=!customSave!"
    if not exist "!saveLocation!" mkdir "!saveLocation!" >nul 2>&1
)

:: Custom filename (single URL mode only)
set "outputTemplate=%saveLocation%\%%(title)s.%%(ext)s"
if "!isBatchFile!"=="0" (
    echo.
    set /p "fileName=Enter custom filename (optional, ENTER to use media title): "
    if not "!fileName!"=="" (
        set "fileName=!fileName:"=!"
        set "outputTemplate=%saveLocation%\!fileName!.%%(ext)s"
    )
)

:: Cookie detection
set "cookieArgs="
if exist "%cookies%\chrome" (
    set "cookieArgs=--cookies "%cookies%\chrome""
) else if exist "%cookies%\cookies.txt" (
    set "cookieArgs=--cookies "%cookies%\cookies.txt""
)

:: FFmpeg location argument
set "ffmpegArg="
if not "!ffmpegLoc!"=="" (
    set "ffmpegArg=--ffmpeg-location "!ffmpegLoc!""
)

:: Referer header argument
set "headerArgs="
if not "!refererUrl!"=="" (
    set "headerArgs=--add-header "Referer: !refererUrl!" --add-header "Origin: !refererUrl!" --add-header "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36""
)

cls
echo ========================================================================
echo Starting Audio Download...
echo ========================================================================
echo Save Location : "!saveLocation!"
echo Audio Format  : !audioExt!
if "!isBatchFile!"=="1" (
    echo Batch List    : "!batchFilePath!"
) else (
    echo Target URL    : "!inputUrl!"
)
echo ========================================================================
echo.

if "!isBatchFile!"=="1" (
    "!ytDlpExe!" --batch-file "!batchFilePath!" --newline -i -o "!outputTemplate!" !audioArgs! !metaArgs! !splitArgs! !cookieArgs! !ffmpegArg! --buffer-size 16k --no-warning
) else (
    "!ytDlpExe!" "!inputUrl!" --newline -i -o "!outputTemplate!" !audioArgs! !metaArgs! !splitArgs! !cookieArgs! !headerArgs! !ffmpegArg! --buffer-size 16k --no-warning
)

echo.
echo ========================================================================
echo Download process completed.
echo Files saved to: "!saveLocation!"
echo ========================================================================
echo.
pause
goto main_menu
