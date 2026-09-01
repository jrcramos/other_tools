@echo off
chcp 65001 >nul

:: Get the directory where this script is located
set "scriptDir=%~dp0"

:: Set Python encoding to UTF-8
set "PYTHONIOENCODING=utf-8"

:: ========================================================================
:: CONFIGURATION SECTION - Customize these settings to your preference
:: ========================================================================

:: Path to ffmpeg.exe and ffprobe.exe
set "ffmpeg=C:\ffmpeg\bin\ffmpeg.exe"
set "ffprobe=C:\ffmpeg\bin\ffprobe.exe"

:: Preferred Python executable path
set "python=C:\Users\joao3\AppData\Local\Programs\Python\Python312\python.exe"

:: ========================================================================
:: END CONFIGURATION SECTION
:: ========================================================================

:: Auto-detect ffmpeg & ffprobe (prioritizing portable .\bin\)
if exist "%scriptDir%bin\ffmpeg.exe" (
    set "ffmpeg=%scriptDir%bin\ffmpeg.exe"
    set "ffprobe=%scriptDir%bin\ffprobe.exe"
) else if exist "%scriptDir%bin\ffmpeg\bin\ffmpeg.exe" (
    set "ffmpeg=%scriptDir%bin\ffmpeg\bin\ffmpeg.exe"
    set "ffprobe=%scriptDir%bin\ffmpeg\bin\ffprobe.exe"
) else if exist "%scriptDir%ffmpeg.exe" (
    set "ffmpeg=%scriptDir%ffmpeg.exe"
    set "ffprobe=%scriptDir%ffprobe.exe"
) else if exist "C:\ffmpeg\bin\ffmpeg.exe" (
    set "ffmpeg=C:\ffmpeg\bin\ffmpeg.exe"
    set "ffprobe=C:\ffmpeg\bin\ffprobe.exe"
) else (
    where ffmpeg >nul 2>&1
    if errorlevel 1 (
        if exist "C:\Program Files\ffmpeg\bin\ffmpeg.exe" (
            set "ffmpeg=C:\Program Files\ffmpeg\bin\ffmpeg.exe"
            set "ffprobe=C:\Program Files\ffmpeg\bin\ffprobe.exe"
        ) else if exist "%USERPROFILE%\ffmpeg\bin\ffmpeg.exe" (
            set "ffmpeg=%USERPROFILE%\ffmpeg\bin\ffmpeg.exe"
            set "ffprobe=%USERPROFILE%\ffmpeg\bin\ffprobe.exe"
        ) else (
            echo ERROR: ffmpeg not found!
            echo Please install ffmpeg or run update_ffmpeg.bat.
            pause
            exit /b
        )
    ) else (
        set "ffmpeg=ffmpeg"
        set "ffprobe=ffprobe"
        echo SUCCESS: Found ffmpeg in system PATH
    )
)

:: Auto-detect Python executable
if not exist "%python%" (
    echo INFO: Python not found at "%python%"
    echo Attempting to auto-detect Python...
    
    where python >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Python executable not found!
        echo Please install Python 3.10+ and add it to system PATH.
        pause
        exit /b
    ) else (
        set "python=python"
        echo SUCCESS: Found python in system PATH
    )
)

:: Check if Python script exists
set "pythonScript=%scriptDir%subtitle_generator.py"
if not exist "%pythonScript%" (
    echo ERROR: Required script "subtitle_generator.py" was not found in:
    echo "%scriptDir%"
    pause
    exit /b
)

:main_menu
cls
echo ========================================================================
echo                 Movie ^& Series Subtitle Generator v1.1
echo            (Batch Audio Extractor + AI Whisper Subtitles)
echo ========================================================================
echo.
echo Add video files or a folder to process.
echo You can enter multiple file paths (one per line).
echo Press ENTER on an empty line when done adding files.
echo.
echo TIP: You can drag and drop video files or an entire folder into this window.
echo (Supported: .mp4, .mkv, .avi, .mov, .webm, .m4v, .ts)
echo.

set "fileListFile=%TEMP%\sub_gen_batch_%RANDOM%.txt"
if exist "%fileListFile%" del "%fileListFile%" >nul

set "fileCount=0"

:file_entry_loop
set "filePath="
set /p "filePath=Enter file path/folder (or ENTER when done, 0 to exit): "

if "%filePath%"=="0" (
    if exist "%fileListFile%" del "%fileListFile%" >nul
    exit /b
)

if "%filePath%"=="" (
    if %fileCount% equ 0 (
        echo.
        echo No files entered. Please enter at least one file or folder path.
        echo.
        goto file_entry_loop
    ) else (
        goto process_queue
    )
)

:: Strip surrounding quotes from drag-and-drop input
for /f "tokens=*" %%I in ("%filePath%") do set "cleanPath=%%~I"

if not exist "%cleanPath%" (
    echo.
    echo ERROR: File or folder not found: "%cleanPath%"
    echo Please check the path and try again.
    echo.
    goto file_entry_loop
)

:: Add clean path to batch list file
echo %cleanPath%>> "%fileListFile%"

:: Use Python helper to count total valid video files in queue
set "countFile=%TEMP%\sub_gen_cnt_%RANDOM%.txt"
"%python%" "%pythonScript%" --input-file-list "%fileListFile%" --count-input-list > "%countFile%" 2>nul
if exist "%countFile%" (
    set /p fileCount=<"%countFile%"
    del "%countFile%" >nul
)

echo.
echo Total valid video file(s) queued so far: %fileCount%
echo.
goto file_entry_loop

:process_queue
cls
echo ========================================================================
echo                 Batch Processing Queue (%fileCount% video file(s))
echo ========================================================================
echo.
echo Probing audio streams for sample video...
echo.

"%python%" "%pythonScript%" --input-file-list "%fileListFile%" --list-tracks --format text --ffprobe-path "%ffprobe%"
if errorlevel 1 (
    echo Warning: Could not probe audio tracks. Defaulting to track #0 for all files.
    set "selectedTrack=0"
) else (
    echo.
    set "selectedTrack="
    set /p "selectedTrack=Select Audio Track # for batch (press ENTER for Track #0 default): "
    if "%selectedTrack%"=="" set "selectedTrack=0"
)

:source_lang_menu
cls
echo ========================================================================
echo                 Select Spoken Language in Audio Track
echo ========================================================================
echo.
echo   1. Auto-detect Spoken Language (Default)
echo   2. English (en)
echo   3. Portuguese (pt)
echo   4. Spanish (es)
echo   5. French (fr)
echo   6. German (de)
echo   7. Italian (it)
echo   8. Japanese (ja)
echo   9. Chinese (zh)
echo  10. Korean (ko)
echo  11. Russian (ru)
echo  12. Custom Language Code (e.g. nl, tr, pl, sv, ar)
echo.

set "slChoice="
set /p "slChoice=Enter choice (1-12, ENTER for Auto-detect): "

if "%slChoice%"=="" set "sourceLang=auto"
if "%slChoice%"=="1" set "sourceLang=auto"
if "%slChoice%"=="2" set "sourceLang=en"
if "%slChoice%"=="3" set "sourceLang=pt"
if "%slChoice%"=="4" set "sourceLang=es"
if "%slChoice%"=="5" set "sourceLang=fr"
if "%slChoice%"=="6" set "sourceLang=de"
if "%slChoice%"=="7" set "sourceLang=it"
if "%slChoice%"=="8" set "sourceLang=ja"
if "%slChoice%"=="9" set "sourceLang=zh"
if "%slChoice%"=="10" set "sourceLang=ko"
if "%slChoice%"=="11" set "sourceLang=ru"
if "%slChoice%"=="12" (
    set /p "sourceLang=Enter 2-letter language code (e.g. nl): "
    if "%sourceLang%"=="" set "sourceLang=auto"
)

:target_lang_menu
cls
echo ========================================================================
echo                 Select Target Subtitle Language
echo ========================================================================
echo.
echo   1. Same as Spoken Audio / Transcribe (Default)
echo   2. English (en)
echo   3. Portuguese (pt)
echo   4. Spanish (es)
echo   5. French (fr)
echo   6. German (de)
echo   7. Italian (it)
echo   8. Japanese (ja)
echo   9. Chinese (zh)
echo  10. Korean (ko)
echo  11. Russian (ru)
echo  12. Custom Language Code (e.g. nl, tr, pl, sv, ar)
echo.

set "tlChoice="
set /p "tlChoice=Enter choice (1-12, ENTER for Same as Audio): "

if "%tlChoice%"=="" set "targetLang=auto"
if "%tlChoice%"=="1" set "targetLang=auto"
if "%tlChoice%"=="2" set "targetLang=en"
if "%tlChoice%"=="3" set "targetLang=pt"
if "%tlChoice%"=="4" set "targetLang=es"
if "%tlChoice%"=="5" set "targetLang=fr"
if "%tlChoice%"=="6" set "targetLang=de"
if "%tlChoice%"=="7" set "targetLang=it"
if "%tlChoice%"=="8" set "targetLang=ja"
if "%tlChoice%"=="9" set "targetLang=zh"
if "%tlChoice%"=="10" set "targetLang=ko"
if "%tlChoice%"=="11" set "targetLang=ru"
if "%tlChoice%"=="12" (
    set /p "targetLang=Enter 2-letter language code (e.g. pt): "
    if "%targetLang%"=="" set "targetLang=auto"
)

:model_menu
cls
echo ========================================================================
echo                 Select Whisper AI Model Quality
echo ========================================================================
echo.
echo   1. Base   - Fast ^& Lightweight (~74MB RAM) [Default]
echo   2. Small  - Recommended Balance (~244MB RAM, Higher Accuracy)
echo   3. Medium - High Accuracy (~769MB RAM)
echo   4. Large  - Maximum Accuracy (~1.5GB RAM, Best for foreign/accents)
echo   5. Tiny   - Super Fast (~39MB RAM)
echo   6. Turbo  - Fast Large-v3 Turbo
echo.

set "mChoice="
set /p "mChoice=Enter choice (1-6, ENTER for Base): "

if "%mChoice%"=="" set "whisperModel=base"
if "%mChoice%"=="1" set "whisperModel=base"
if "%mChoice%"=="2" set "whisperModel=small"
if "%mChoice%"=="3" set "whisperModel=medium"
if "%mChoice%"=="4" set "whisperModel=large-v3"
if "%mChoice%"=="5" set "whisperModel=tiny"
if "%mChoice%"=="6" set "whisperModel=turbo"

cls
echo ========================================================================
echo             Starting Batch Subtitle Generation (%fileCount% files)
echo ========================================================================
echo Selected Audio Track: #%selectedTrack%
echo Spoken Audio Lang:   %sourceLang%
echo Target Subtitle:     %targetLang%
echo Whisper Model:       %whisperModel%
echo ========================================================================
echo.
echo Pre-loading AI Model and processing all videos sequentially...
echo.

"%python%" "%pythonScript%" --input-file-list "%fileListFile%" --track %selectedTrack% --source-lang "%sourceLang%" --target-lang "%targetLang%" --model "%whisperModel%" --ffmpeg-path "%ffmpeg%" --ffprobe-path "%ffprobe%"

if exist "%fileListFile%" del "%fileListFile%" >nul

if errorlevel 1 (
    echo.
    echo ERROR: Batch processing encountered an issue.
    pause
    goto main_menu
)

echo.
echo ========================================================================
echo SUCCESS! Batch processing completed for all %fileCount% videos.
echo ========================================================================
echo.
pause
goto main_menu
