@echo off
setlocal enabledelayedexpansion

:: Get the directory where this script is located
set "scriptDir=%~dp0"

:: ========================================================================
:: CONFIGURATION SECTION - Customize these settings to your preference
:: ========================================================================

:: Path to ffmpeg.exe (will auto-detect if not found at specified location)
:: You can change this to your ffmpeg installation path if needed
set "ffmpeg=C:\ffmpeg\bin\ffmpeg.exe"

:: Temporary directory for processing (will use system temp if this doesn't exist)
:: You can change this to any directory where you have write permissions
set "tempDir=C:\ffmpeg\temp"

:: Video encoding settings - adjust these based on your needs
:: NOTE: VIDEO_BITRATE and VIDEO_RESOLUTION will be set by user selection at runtime
set "VIDEO_BITRATE=4M"       :: Default if not overridden (e.g., 2M, 4M, 8M)
set "VIDEO_RESOLUTION=1280x720"  :: Default if not overridden (e.g., 1920x1080, 1280x720, 854x480)
set "FRAME_RATE=30"          :: Frames per second (e.g., 24, 30, 60)
set "AUDIO_BITRATE=192k"     :: Audio quality (e.g., 128k, 192k, 256k)

:: ========================================================================
:: END CONFIGURATION SECTION
:: ========================================================================

set "processedTempDir=%tempDir%\processed_inputs"

:: Auto-detect ffmpeg if not found at the configured location
if not exist "%ffmpeg%" (
    echo INFO: ffmpeg not found at "%ffmpeg%"
    echo Attempting to auto-detect ffmpeg...
    
    :: Check if ffmpeg is in PATH
    where ffmpeg >nul 2>&1
    if !errorlevel! equ 0 (
        set "ffmpeg=ffmpeg"
        echo SUCCESS: Found ffmpeg in system PATH
    ) else (
        :: Check common installation locations
        if exist "C:\Program Files\ffmpeg\bin\ffmpeg.exe" (
            set "ffmpeg=C:\Program Files\ffmpeg\bin\ffmpeg.exe"
            echo SUCCESS: Found ffmpeg at C:\Program Files\ffmpeg\bin\ffmpeg.exe
        ) else if exist "%USERPROFILE%\ffmpeg\bin\ffmpeg.exe" (
            set "ffmpeg=%USERPROFILE%\ffmpeg\bin\ffmpeg.exe"
            echo SUCCESS: Found ffmpeg at %USERPROFILE%\ffmpeg\bin\ffmpeg.exe
        ) else (
            echo ERROR: ffmpeg not found!
            echo.
            echo Please install ffmpeg and either:
            echo   1. Add it to your system PATH, or
            echo   2. Update the ffmpeg path in this script's CONFIGURATION SECTION
            echo.
            echo Download ffmpeg from: https://ffmpeg.org/download.html
            pause
            exit /b
        )
    )
)

:: Use system temp directory as fallback if configured temp doesn't exist
if not exist "%tempDir%" (
    set "tempDir=%TEMP%\video_joiner_temp"
    set "processedTempDir=!tempDir!\processed_inputs"
    echo INFO: Using system temp directory: !tempDir!
)

:: Create the temporary directories if they don't exist
if not exist "%tempDir%" mkdir "%tempDir%" >nul 2>&1
if not exist "%processedTempDir%" mkdir "%processedTempDir%" >nul 2>&1
if errorlevel 1 (
    echo FATAL ERROR: Could not create necessary directories.
    echo Please check your permissions for "%tempDir%".
    pause
    exit /b
)

:resolution_menu
cls
echo ================================
echo    FFmpeg Video Joiner v2.1
echo ================================
echo.
echo Select target resolution:
echo   1. 360p  (640x360)
echo   2. 480p  (854x480)
echo   3. 720p  (1280x720)
echo   4. 1080p (1920x1080)
echo   5. Exit
echo.

set "choice="
set /p "choice=Enter your choice (1-5): "

if "%choice%"=="1" (
    set "VIDEO_RESOLUTION=640x360"
    set "VIDEO_BITRATE=1M"
    goto input_loop
) else if "%choice%"=="2" (
    set "VIDEO_RESOLUTION=854x480"
    set "VIDEO_BITRATE=2M"
    goto input_loop
) else if "%choice%"=="3" (
    set "VIDEO_RESOLUTION=1280x720"
    set "VIDEO_BITRATE=4M"
    goto input_loop
) else if "%choice%"=="4" (
    set "VIDEO_RESOLUTION=1920x1080"
    set "VIDEO_BITRATE=8M"
    goto input_loop
) else if "%choice%"=="5" (
    exit /b
) else (
    echo Invalid choice. Please try again.
    timeout /t 2 >nul
    goto resolution_menu
)

:input_loop
cls
echo ================================
echo    FFmpeg Video Joiner v2.1
echo (Standardizes & Joins for Max Compatibility)
echo ================================
echo.

set /p outputName="Enter output file name (without extension): "
if "%outputName%"=="" goto input_loop

:: Define file paths
set "outputFile=%scriptDir%%outputName%.mp4"
set "listfile=%tempDir%\ffmpeg_raw_file_list.txt"
set "processedListfile=%tempDir%\ffmpeg_processed_file_list.txt"

:: Clean up previous temporary list files and processed videos
if exist "%listfile%" del "%listfile%" >nul
if exist "%processedListfile%" del "%processedListfile%" >nul
del /q "%processedTempDir%\*.mp4" >nul 2>&1

echo.
echo Enter video file paths (one per line).
echo Press ENTER on an empty line when done.
echo TIP: You can drag and drop a file into this window to paste its path.
echo.

:: Manual file entry loop for original files
set "fileCount=0"
:file_entry_loop
set "filePath="
set /p "filePath=File path (or ENTER to finish): "
if "!filePath!"=="" (
    if !fileCount! equ 0 (
        echo No files entered. Please enter at least one file.
        goto file_entry_loop
    ) else (
        goto pre_process_files
    )
)

:: Clean and normalize path (strip quotes/spaces, fix slashes & missing drive colons)
call :clean_path "!filePath!"
set "filePath=!cleanPath!"

if not exist "!filePath!" (
    echo File not found: "!filePath!"
    echo Please check the path and try again.
    goto file_entry_loop
)

:: Add the RAW file path to the list for pre-processing.
echo !filePath!>> "%listfile%"
set /a fileCount+=1
echo Added: !filePath!
goto file_entry_loop

:pre_process_files
set "processedFileCount=0"
for /f "usebackq delims=" %%F in ("%listfile%") do (
    set /a processedFileCount+=1
    set "inputFile=%%F"
    
    for %%N in ("!inputFile!") do set "fileName=%%~nN"
    set "processedFile=%processedTempDir%\!processedFileCount!_!fileName!_processed.mp4"

    (
        echo.
        echo ----------------------------------------------------------------------
        echo Processing file !processedFileCount! of %fileCount%: "!fileName!%%~xN"
        echo This step standardizes each video. Please wait...
        echo ----------------------------------------------------------------------
        echo.
    )

    "%ffmpeg%" -i "!inputFile!" -c:v h264_nvenc -preset p5 -b:v %VIDEO_BITRATE% -s %VIDEO_RESOLUTION% -c:a aac -b:a %AUDIO_BITRATE% -r %FRAME_RATE% -fps_mode cfr -pix_fmt yuv420p "!processedFile!" >nul 2>&1

    if errorlevel 1 (
        echo.
        echo ERROR: Pre-processing failed for "!inputFile!".
        pause
        goto input_loop
    )
    
    :: Add the PROCESSED file to the processed list with the correct concat syntax.
    echo file '!processedFile!'>> "%processedListfile%"
)

:process_files
echo.
echo Concatenating all standardized videos...
echo This should be very fast.
echo.

"%ffmpeg%" -f concat -safe 0 -i "%processedListfile%" -c copy "%outputFile%" >nul 2>&1

if errorlevel 1 (
    echo ERROR: Final video joining failed.
    pause
    goto input_loop
)

:: Clean up temporary files
del /q "%listfile%" >nul 2>&1
del /q "%processedListfile%" >nul 2>&1
rmdir /s /q "%processedTempDir%" >nul 2>&1

(
    echo.
    echo SUCCESS! Merge complete.
    echo Output saved to: "%outputFile%"
)
pause
goto input_loop


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