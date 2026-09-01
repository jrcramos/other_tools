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

:: Auto-detect ffmpeg (prioritizing portable .\bin\)
if exist "%scriptDir%bin\ffmpeg.exe" (
    set "ffmpeg=%scriptDir%bin\ffmpeg.exe"
) else if exist "%scriptDir%bin\ffmpeg\bin\ffmpeg.exe" (
    set "ffmpeg=%scriptDir%bin\ffmpeg\bin\ffmpeg.exe"
) else if exist "%scriptDir%ffmpeg.exe" (
    set "ffmpeg=%scriptDir%ffmpeg.exe"
) else if exist "C:\ffmpeg\bin\ffmpeg.exe" (
    set "ffmpeg=C:\ffmpeg\bin\ffmpeg.exe"
) else (
    where ffmpeg >nul 2>&1
    if !errorlevel! equ 0 (
        set "ffmpeg=ffmpeg"
    ) else if exist "C:\Program Files\ffmpeg\bin\ffmpeg.exe" (
        set "ffmpeg=C:\Program Files\ffmpeg\bin\ffmpeg.exe"
    ) else if exist "%USERPROFILE%\ffmpeg\bin\ffmpeg.exe" (
        set "ffmpeg=%USERPROFILE%\ffmpeg\bin\ffmpeg.exe"
    ) else (
        echo.
        echo ERROR: ffmpeg.exe not found!
        echo Please install ffmpeg or run update_ffmpeg.bat.
        echo.
        pause
        exit /b
    )
)

:: Auto-detect ffprobe (prioritizing portable .\bin\)
if exist "%scriptDir%bin\ffprobe.exe" (
    set "ffprobe=%scriptDir%bin\ffprobe.exe"
) else if exist "%scriptDir%bin\ffmpeg\bin\ffprobe.exe" (
    set "ffprobe=%scriptDir%bin\ffmpeg\bin\ffprobe.exe"
) else if exist "%scriptDir%ffprobe.exe" (
    set "ffprobe=%scriptDir%ffprobe.exe"
) else if exist "C:\ffmpeg\bin\ffprobe.exe" (
    set "ffprobe=C:\ffmpeg\bin\ffprobe.exe"
) else (
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

:: Check if file(s) or folder was passed as argument or dragged onto script icon
if not "%~1"=="" (
    set "fileListFile=%TEMP%\vid2gif_batch_%RANDOM%.txt"
    if exist "!fileListFile!" del "!fileListFile!" >nul
    set "fileCount=0"
    for %%A in (%*) do (
        set "argPath=%%~A"
        call :clean_path "!argPath!"
        set "argPath=!cleanPath!"
        if exist "!argPath!\*" (
            call :scan_folder_videos "!argPath!"
        ) else if exist "!argPath!" (
            echo !argPath!>> "!fileListFile!"
            set /a fileCount+=1
        )
    )
    if !fileCount! gtr 0 goto options_menu
)

:main_menu
cls
echo ========================================================================
echo               FFmpeg Video to GIF ^& Animated WebP Maker v1.0
echo             (High-Quality 2-Pass Palettegen, Trimming, Scaling)
echo ========================================================================
echo.
echo Drag and drop video file(s) or a folder into this window:
echo You can enter multiple file paths (one per line).
echo Press ENTER on an empty line when done adding files (0 to exit).
echo.

set "fileListFile=%TEMP%\vid2gif_batch_%RANDOM%.txt"
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

:: Clean and normalize path
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
echo Queued Files: !fileCount! video file(s)
echo ========================================================================
echo.
echo Select Output Animation Format:
echo   1. High-Quality GIF (.gif) - Two-Pass Palettegen [Default]
echo   2. Animated WebP (.webp)   - High Fidelity, 60-80%% Smaller than GIF
echo   3. Both (Generate both .gif and .webp)
echo   0. Cancel and Return to Main Menu
echo.

set "formatChoice="
set /p "formatChoice=Select Format (1-3) [Default 1]: "
if "!formatChoice!"=="" set "formatChoice=1"
if "!formatChoice!"=="0" (
    if exist "%fileListFile%" del "%fileListFile%" >nul
    goto main_menu
)

set "wantGif=0"
set "wantWebp=0"
if "!formatChoice!"=="1" set "wantGif=1"
if "!formatChoice!"=="2" set "wantWebp=1"
if "!formatChoice!"=="3" (
    set "wantGif=1"
    set "wantWebp=1"
)

:: Time Trimming Options
echo.
echo ========================================================================
echo Time Range / Trimming:
echo ========================================================================
echo Enter Start Time (HH:MM:SS, MM:SS, or seconds e.g. 00:01:20 or 15).
echo Press ENTER for start from beginning (00:00:00).
echo.
set "startTime="
set /p "startTime=Start Time [Default 00:00:00]: "
if "!startTime!"=="" set "startTime=00:00:00"

echo.
echo Enter Duration to capture (in seconds or MM:SS, e.g. 5, 10, 00:15).
echo Press ENTER to convert until the end of the video.
echo.
set "duration="
set /p "duration=Duration [Default: Full Video]: "

:: Resolution / Scaling Options
echo.
echo ========================================================================
echo Target Resolution / Width (Aspect Ratio Preserved):
echo ========================================================================
echo   1. 480px width (Standard / Discord / Web) [Default]
echo   2. 720px width (High Definition)
echo   3. 360px width (Compact / Lightweight)
echo   4. 240px width (Low bandwidth / Tiny)
echo   5. Original Video Resolution
echo   6. Custom Width
echo.

set "resChoice="
set /p "resChoice=Select Resolution (1-6) [Default 1]: "
if "!resChoice!"=="" set "resChoice=1"

set "targetScale=scale=480:-1:flags=lanczos"
if "!resChoice!"=="1" set "targetScale=scale=480:-1:flags=lanczos"
if "!resChoice!"=="2" set "targetScale=scale=720:-1:flags=lanczos"
if "!resChoice!"=="3" set "targetScale=scale=360:-1:flags=lanczos"
if "!resChoice!"=="4" set "targetScale=scale=240:-1:flags=lanczos"
if "!resChoice!"=="5" set "targetScale="
if "!resChoice!"=="6" (
    set /p "customWidth=Enter target width in pixels (e.g. 600): "
    if not "!customWidth!"=="" (
        set "targetScale=scale=!customWidth!:-1:flags=lanczos"
    ) else (
        set "targetScale=scale=480:-1:flags=lanczos"
    )
)

:: Frame Rate (FPS)
echo.
echo ========================================================================
echo Frame Rate (FPS):
echo ========================================================================
echo   1. 15 FPS (Smooth ^& Balanced file size) [Default]
echo   2. 24 FPS (Very Smooth Animation)
echo   3. 30 FPS (Fluid / High Motion)
echo   4. 10 FPS (Compact / Lightweight)
echo   5. Keep Original FPS
echo.

set "fpsChoice="
set /p "fpsChoice=Select FPS (1-5) [Default 1]: "
if "!fpsChoice!"=="" set "fpsChoice=1"

set "targetFps=15"
if "!fpsChoice!"=="1" set "targetFps=15"
if "!fpsChoice!"=="2" set "targetFps=24"
if "!fpsChoice!"=="3" set "targetFps=30"
if "!fpsChoice!"=="4" set "targetFps=10"
if "!fpsChoice!"=="5" set "targetFps="

:: Dithering mode for GIF
set "ditherOpt=bayer:bayer_scale=5"
if "!wantGif!"=="1" (
    echo.
    echo ========================================================================
    echo GIF Dithering / Optimization Profile:
    echo ========================================================================
    echo   1. Bayer Dithering (Smooth gradients, prevents banding) [Default]
    echo   2. Floyd-Steinberg (High detail, slightly larger size)
    echo   3. Sierra2_4a (Clean details, medium compression)
    echo   4. None (Flat colors, smallest file size)
    echo.
    set "ditherChoice="
    set /p "ditherChoice=Select Dithering (1-4) [Default 1]: "
    if "!ditherChoice!"=="" set "ditherChoice=1"
    if "!ditherChoice!"=="1" set "ditherOpt=bayer:bayer_scale=5"
    if "!ditherChoice!"=="2" set "ditherOpt=floyd_steinberg"
    if "!ditherChoice!"=="3" set "ditherOpt=sierra2_4a"
    if "!ditherChoice!"=="4" set "ditherOpt=none"
)

:: Build filter strings
set "filterBase="
if not "!targetFps!"=="" (
    set "filterBase=fps=!targetFps!"
)
if not "!targetScale!"=="" (
    if "!filterBase!"=="" (
        set "filterBase=!targetScale!"
    ) else (
        set "filterBase=!filterBase!,!targetScale!"
    )
)

:: Time args
set "timeArgs="
if not "!startTime!"=="00:00:00" (
    set "timeArgs=-ss !startTime!"
)
if not "!duration!"=="" (
    set "timeArgs=!timeArgs! -t !duration!"
)

cls
echo ========================================================================
echo Starting Animation Processing...
echo ========================================================================
echo Queued Files   : !fileCount!
echo Generating GIF : !wantGif!
echo Generating WebP: !wantWebp!
echo Filter Pipeline: !filterBase!
echo Time Range     : Start=!startTime!, Duration=!duration!
echo ========================================================================
echo.

set "processedCount=0"
set "successCount=0"

for /f "usebackq delims=" %%F in ("!fileListFile!") do (
    set "currentFile=%%F"
    set /a processedCount+=1
    
    for %%A in ("!currentFile!") do (
        set "fileDir=%%~dpA"
        set "fileName=%%~nA"
        set "fileExt=%%~xA"
    )
    
    echo ------------------------------------------------------------------------
    echo [!processedCount!/!fileCount!] Processing: "!fileName!!fileExt!"
    echo ------------------------------------------------------------------------
    
    set "outGif=!fileDir!!fileName!.gif"
    set "outWebp=!fileDir!!fileName!.webp"
    
    :: Convert to GIF
    if "!wantGif!"=="1" (
        echo   - Generating Palette ^& Rendering GIF: "!fileName!.gif"...
        
        if "!filterBase!"=="" (
            set "gifFilter=split[s0][s1];[s0]palettegen=stats_mode=diff[p];[s1][p]paletteuse=dither=!ditherOpt!"
        ) else (
            set "gifFilter=!filterBase!,split[s0][s1];[s0]palettegen=stats_mode=diff[p];[s1][p]paletteuse=dither=!ditherOpt!"
        )
        
        "%ffmpeg%" -hide_banner -v error -stats !timeArgs! -i "!currentFile!" -filter_complex "!gifFilter!" -loop 0 -y "!outGif!"
        
        if !errorlevel! equ 0 (
            for %%G in ("!outGif!") do (
                set "gifSize=%%~zG"
                call :format_size !gifSize!
                echo     + GIF Success: "!fileName!.gif" (!formattedSize!)
            )
        ) else (
            echo     x ERROR: Failed to render GIF.
        )
    )
    
    :: Convert to Animated WebP
    if "!wantWebp!"=="1" (
        echo   - Rendering Animated WebP: "!fileName!.webp"...
        
        if "!filterBase!"=="" (
            "%ffmpeg%" -hide_banner -v error -stats !timeArgs! -i "!currentFile!" -vcodec libwebp -lossless 0 -compression_level 4 -q:v 75 -loop 0 -an -y "!outWebp!"
        ) else (
            "%ffmpeg%" -hide_banner -v error -stats !timeArgs! -i "!currentFile!" -vcodec libwebp -filter:v "!filterBase!" -lossless 0 -compression_level 4 -q:v 75 -loop 0 -an -y "!outWebp!"
        )
        
        if !errorlevel! equ 0 (
            for %%W in ("!outWebp!") do (
                set "webpSize=%%~zW"
                call :format_size !webpSize!
                echo     + WebP Success: "!fileName!.webp" (!formattedSize!)
            )
        ) else (
            echo     x ERROR: Failed to render WebP.
        )
    )
    
    set /a successCount+=1
    echo.
)

if exist "%fileListFile%" del "%fileListFile%" >nul

echo ========================================================================
echo COMPLETED: Processed !successCount! / !fileCount! file(s).
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
for /r "%~1" %%V in (*.mp4 *.mkv *.avi *.mov *.webm *.m4v *.ts *.flv *.wmv) do (
    echo %%V>> "%fileListFile%"
    set /a fileCount+=1
    echo   + Added: %%~nxV
)
goto :eof


:format_size
set "bytes=%~1"
if not defined bytes (
    set "formattedSize=0 B"
    goto :eof
)
if !bytes! lss 1024 (
    set "formattedSize=!bytes! B"
) else if !bytes! lss 1048576 (
    set /a "kb=!bytes! / 1024"
    set "formattedSize=!kb! KB"
) else (
    set /a "mb=!bytes! / 1048576"
    set "formattedSize=!mb! MB"
)
goto :eof
