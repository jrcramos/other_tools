@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: Get the directory where this script is located
set "scriptDir=%~dp0"

:: ========================================================================
:: CONFIGURATION SECTION - Customize these settings to your preference
:: ========================================================================
:: Auto-detect persistent download directory
set "defaultSaveLocation=%USERPROFILE%\Videos"
if exist "%scriptDir%config_manager.py" (
    for /f "delims=" %%D in ('python "%scriptDir%config_manager.py" --get-download-dir 2^>nul') do (
        if not "%%D"=="" set "defaultSaveLocation=%%D"
    )
)

:: Auto-detect yt-dlp executable (prioritizing portable .\bin\)
set "ytDlpExe="
if exist "%scriptDir%bin\yt-dlp.exe" (
    set "ytDlpExe=%scriptDir%bin\yt-dlp.exe"
) else if exist "%scriptDir%yt-dlp.exe" (
    set "ytDlpExe=%scriptDir%yt-dlp.exe"
) else (
    where yt-dlp >nul 2>&1
    if !errorlevel! equ 0 (
        set "ytDlpExe=yt-dlp"
    ) else if exist "C:\Users\joao3\Videos\yt-dlp-master\yt-dlp.exe" (
        set "ytDlpExe=C:\Users\joao3\Videos\yt-dlp-master\yt-dlp.exe"
    ) else if exist "%USERPROFILE%\yt-dlp.exe" (
        set "ytDlpExe=%USERPROFILE%\yt-dlp.exe"
    ) else (
        echo.
        echo ERROR: yt-dlp.exe not found!
        echo Please ensure yt-dlp is installed or run update_yt-dlp.bat first.
        echo.
        pause
        exit /b
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

:: Ensure default save directory exists
if not exist "%defaultSaveLocation%" mkdir "%defaultSaveLocation%" >nul 2>&1

:: Check if URL was passed as argument or dragged onto script icon
if not "%~1"=="" (
    set "inputUrl=%~1"
    goto parse_input_target
)

:main_menu
cls
echo ========================================================================
echo          yt-dlp Channel ^& Playlist Archive Downloader v1.0
echo     (Bulk Video/Course Archiver with Indexing, Subtitles ^& Resume)
echo ========================================================================
echo.
echo Tip: Paste a Channel URL, Playlist URL, or piped "URL|Referer".
echo.

set "inputUrl="
set "refererUrl="
set /p "inputUrl=Enter Playlist or Channel URL (0 to exit): "

if "!inputUrl!"=="0" exit /b
if "!inputUrl!"=="" goto main_menu

:parse_input_target
:: Clean quotes
set "inputUrl=!inputUrl:"=!"
set "inputUrl=!inputUrl:'=!"

:: Auto-detect piped URL|Referer format
for /f "tokens=1* delims=|" %%A in ("!inputUrl!") do (
    set "inputUrl=%%A"
    set "refererUrl=%%B"
)

if not "!refererUrl!"=="" (
    echo Auto-detected Referer: !refererUrl!
)

:: Quality & Format Menu
echo.
echo ========================================================================
echo Select Download Mode / Quality:
echo ========================================================================
echo   1. Best Video + Audio (Up to 4K/1080p, Remuxed to MP4) [Default]
echo   2. Maximum 1080p Full HD (Save bandwidth/space, Remuxed to MP4)
echo   3. Maximum 720p HD (Compact size, Remuxed to MP4)
echo   4. Audio Only - MP3 (High Quality ~320k + Cover Art + ID3 Tags)
echo   5. Audio Only - M4A / AAC (Apple/Mobile Optimized)
echo   0. Back to Main Menu
echo.

set "qualityChoice="
set /p "qualityChoice=Select Option (1-5) [Default 1]: "
if "!qualityChoice!"=="" set "qualityChoice=1"
if "!qualityChoice!"=="0" goto main_menu

set "formatArgs=-f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best" --remux-video mp4"
set "isAudioOnly=0"

if "!qualityChoice!"=="1" (
    set "formatArgs=-f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best/b" --remux-video mp4"
) else if "!qualityChoice!"=="2" (
    set "formatArgs=-f "bestvideo[height<=?1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=?1080]+bestaudio/best[height<=?1080]/bestvideo+bestaudio/best/b" --remux-video mp4"
) else if "!qualityChoice!"=="3" (
    set "formatArgs=-f "bestvideo[height<=?720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=?720]+bestaudio/best[height<=?720]/bestvideo+bestaudio/best/b" --remux-video mp4"
) else if "!qualityChoice!"=="4" (
    set "isAudioOnly=1"
    set "formatArgs=--extract-audio --audio-format mp3 --audio-quality 0 --embed-thumbnail --convert-thumbnails jpg"
) else if "!qualityChoice!"=="5" (
    set "isAudioOnly=1"
    set "formatArgs=--extract-audio --audio-format m4a --audio-quality 0 --embed-thumbnail --convert-thumbnails jpg"
)

:: Folder Organization & Naming Template
echo.
echo ========================================================================
echo Folder Organization ^& File Naming:
echo ========================================================================
echo   1. Channel/Playlist Subfolder with Numbered Index [Default / Best for Courses]
echo      Pattern: Channel_or_Playlist / 01 - Video Title.ext
echo   2. Channel Subfolder with Upload Date
echo      Pattern: Channel_Name / [YYYY-MM-DD] Video Title.ext
echo   3. Simple Channel Subfolder
echo      Pattern: Channel_Name / Video Title.ext
echo   4. Flat (Save directly into main directory)
echo.

set "namingChoice="
set /p "namingChoice=Select Naming (1-4) [Default 1]: "
if "!namingChoice!"=="" set "namingChoice=1"

if "!namingChoice!"=="1" (
    set "outTemplate=%%(uploader,playlist_uploader,playlist_title)s/%%(playlist_index&{:02d} - |)s%%(title)s.%%(ext)s"
) else if "!namingChoice!"=="2" (
    set "outTemplate=%%(uploader,playlist_uploader,channel)s/[%%(upload_date)s] %%(title)s.%%(ext)s"
) else if "!namingChoice!"=="3" (
    set "outTemplate=%%(uploader,playlist_uploader,channel)s/%%(title)s.%%(ext)s"
) else (
    set "outTemplate=%%(title)s.%%(ext)s"
)

:: Range & Item Limits
echo.
echo ========================================================================
echo Download Scope / Range:
echo ========================================================================
echo   1. Download All items in Playlist/Channel [Default]
echo   2. Specific Item Range (e.g. items 1 to 20)
echo   3. Latest N items only (e.g. top 10 most recent)
echo.

set "rangeChoice="
set /p "rangeChoice=Select Scope (1-3) [Default 1]: "
if "!rangeChoice!"=="" set "rangeChoice=1"

set "rangeArgs="
if "!rangeChoice!"=="2" (
    set /p "pStart=Enter Start Index [Default 1]: "
    if "!pStart!"=="" set "pStart=1"
    set /p "pEnd=Enter End Index (e.g. 25): "
    if not "!pEnd!"=="" (
        set "rangeArgs=--playlist-start !pStart! --playlist-end !pEnd!"
    ) else (
        set "rangeArgs=--playlist-start !pStart!"
    )
) else if "!rangeChoice!"=="3" (
    set /p "maxItems=Enter number of latest videos to fetch (e.g. 5 or 10): "
    if not "!maxItems!"=="" (
        set "rangeArgs=--max-downloads !maxItems!"
    )
)

:: Subtitle & Metadata Options (for video modes)
set "subArgs="
if "!isAudioOnly!"=="0" (
    echo.
    echo ========================================================================
    echo Subtitles ^& Captions:
    echo ========================================================================
    echo   1. Auto-fetch and embed English/Portuguese/auto-generated subs [Default]
    echo   2. Embed ALL available subtitle tracks
    echo   3. Save external .srt files (Don't embed into video)
    echo   4. Skip subtitles
    echo.
    set "subChoice="
    set /p "subChoice=Select Option (1-4) [Default 1]: "
    if "!subChoice!"=="" set "subChoice=1"
    if "!subChoice!"=="1" set "subArgs=--write-subs --write-auto-subs --sub-langs "en.*,pt.*" --embed-subs"
    if "!subChoice!"=="2" set "subArgs=--all-subs --embed-subs"
    if "!subChoice!"=="3" set "subArgs=--write-subs --write-auto-subs --sub-langs all --convert-subs srt"
    if "!subChoice!"=="4" set "subArgs="
)

:: Archive Sync Tracking
echo.
echo ========================================================================
echo Archive Tracking (Skip already downloaded videos on future runs):
echo ========================================================================
echo   1. Enabled (Save record in download folder to allow easy sync) [Default]
echo   2. Disabled (Re-check everything)
echo.

set "archiveChoice="
set /p "archiveChoice=Select Option (1-2) [Default 1]: "
if "!archiveChoice!"=="" set "archiveChoice=1"

set "archiveArgs="
if "!archiveChoice!"=="1" (
    set "archiveArgs=--download-archive "!defaultSaveLocation!\download_archive.txt""
)

:: Destination Directory
echo.
echo Target Save Directory (Press ENTER for: "%defaultSaveLocation%"):
set "customSave="
set /p "customSave=Enter path or press ENTER: "
if not "!customSave!"=="" (
    set "customSave=!customSave:"=!"
    if not exist "!defaultSaveLocation!" mkdir "!defaultSaveLocation!" >nul 2>&1
    if exist "%scriptDir%config_manager.py" (
        python "%scriptDir%config_manager.py" --set-download-dir "!defaultSaveLocation!" >nul 2>&1
    )
    if "!archiveChoice!"=="1" (
        set "archiveArgs=--download-archive "!defaultSaveLocation!\download_archive.txt""
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
echo Starting Channel / Playlist Download...
echo ========================================================================
echo Target URL     : "!inputUrl!"
echo Save Directory : "!defaultSaveLocation!"
echo Output Format  : Quality Mode !qualityChoice!
if not "!rangeArgs!"=="" echo Scope/Range    : !rangeArgs!
if not "!archiveArgs!"=="" echo Archive File   : "!defaultSaveLocation!\download_archive.txt"
echo ========================================================================
echo.

"!ytDlpExe!" "!inputUrl!" --newline -i -o "!defaultSaveLocation!\!outTemplate!" !formatArgs! !subArgs! !rangeArgs! !archiveArgs! --embed-metadata --embed-chapters !cookieArgs! !headerArgs! !ffmpegArg! --buffer-size 16k --no-warning

echo.
echo ========================================================================
echo Download process completed.
echo Files saved to: "!defaultSaveLocation!"
echo ========================================================================
echo.
pause
goto main_menu
