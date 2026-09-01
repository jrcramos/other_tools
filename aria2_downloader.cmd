@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ========================================================================
::          aria2 Multi-Connection Turbo Download Accelerator
:: ========================================================================

set "scriptDir=%~dp0"

:: Auto-detect aria2c binary (prioritizing portable .\bin\)
set "aria2Exe="
if exist "%scriptDir%bin\aria2c.exe" (
    set "aria2Exe=%scriptDir%bin\aria2c.exe"
) else if exist "%scriptDir%aria2c.exe" (
    set "aria2Exe=%scriptDir%aria2c.exe"
) else (
    where aria2c >nul 2>&1
    if !errorlevel! equ 0 (
        set "aria2Exe=aria2c"
    ) else (
        echo ========================================================================
        echo  aria2c.exe not found!
        echo ========================================================================
        echo  Downloading and setting up portable aria2c into .\bin\...
        echo.
        python "%scriptDir%update_aria2.py"
        if exist "%scriptDir%bin\aria2c.exe" (
            set "aria2Exe=%scriptDir%bin\aria2c.exe"
        ) else (
            echo [!] Failed to download aria2c. Please run update_aria2.bat manually.
            pause
            exit /b 1
        )
    )
)

:: Get default save location from config_manager
set "defaultSaveLocation=C:\Users\joao3\Downloads"
if exist "%scriptDir%config_manager.py" (
    for /f "delims=" %%D in ('python "%scriptDir%config_manager.py" --get-download-dir 2^>nul') do (
        if not "%%D"=="" set "defaultSaveLocation=%%D"
    )
)

:main_menu
cls
echo ========================================================================
echo        🚀 aria2 Multi-Connection Turbo Download Accelerator v1.0
echo             (Splits files into parallel 16-connection chunks)
echo ========================================================================
echo.
echo Save Directory : %defaultSaveLocation%
echo Engine Binary  : %aria2Exe%
echo.
echo Paste a direct download URL, piped 'URL^|Referer', or drag ^& drop a .txt list:
echo.

set "inputTarget=%~1"
if "!inputTarget!"=="" (
    set /p "inputTarget=Enter URL or .txt path: "
)

if "!inputTarget!"=="" (
    echo [!] No URL provided.
    pause
    goto main_menu
)

:: Remove surrounding quotes
set "inputTarget=!inputTarget:"=!"

:: Check for URL|Referer pipe delimiter
set "targetUrl=!inputTarget!"
set "refererUrl="
for /f "tokens=1,2 delims=|" %%A in ("!inputTarget!") do (
    set "targetUrl=%%A"
    set "refererUrl=%%B"
)

:: Check if input is a .txt batch file
set "isBatch=0"
if exist "!targetUrl!" (
    for %%F in ("!targetUrl!") do (
        if /i "%%~xF"==".txt" set "isBatch=1"
    )
)

:: Speed & Chunks configuration
echo.
echo ========================================================================
echo Select Connection Mode:
echo ========================================================================
echo   1. ⚡ Turbo Mode (16 parallel connections per file, 1MB split) [Default]
echo   2. 🚀 Ultra Turbo (32 parallel connections per file, 512KB split)
echo   3. 🛡️ Balanced (8 parallel connections per file)
echo   4. 🎯 Custom connections
echo.
set "chunkChoice="
set /p "chunkChoice=Select Mode (1-4) [Default 1]: "
if "!chunkChoice!"=="" set "chunkChoice=1"

set "splitArgs=-s 16 -x 16 -k 1M -j 4"
if "!chunkChoice!"=="2" set "splitArgs=-s 32 -x 32 -k 512K -j 8"
if "!chunkChoice!"=="3" set "splitArgs=-s 8 -x 8 -k 2M -j 2"
if "!chunkChoice!"=="4" (
    set /p "customConns=Enter number of connections (e.g. 24): "
    if not "!customConns!"=="" set "splitArgs=-s !customConns! -x !customConns! -k 1M"
)

:: Optional Custom Output Filename (for single files)
set "customOut="
if "!isBatch!"=="0" (
    echo.
    set /p "customOut=Custom output filename (press ENTER to auto-detect from server): "
)

:: Save directory selection
echo.
echo Target Save Directory (Press ENTER for: "%defaultSaveLocation%"):
set "customSave="
set /p "customSave=Enter path or press ENTER: "
if not "!customSave!"=="" (
    set "customSave=!customSave:"=!"
    set "defaultSaveLocation=!customSave!"
    if not exist "!defaultSaveLocation!" mkdir "!defaultSaveLocation!" >nul 2>&1
    if exist "%scriptDir%config_manager.py" (
        python "%scriptDir%config_manager.py" --set-download-dir "!defaultSaveLocation!" >nul 2>&1
    )
)

:: Build aria2c command arguments
set "extraHeaders="
if not "!refererUrl!"=="" (
    set extraHeaders=--referer="!refererUrl!" --header="Origin: !refererUrl!"
)

set "outArg="
if not "!customOut!"=="" (
    set outArg=--out="!customOut!"
)

echo.
echo ========================================================================
echo Starting Turbo Download...
echo ========================================================================
echo.

if "!isBatch!"=="1" (
    "%aria2Exe%" -i "!targetUrl!" -d "!defaultSaveLocation!" -c !splitArgs! --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36" --summary-interval=2 --file-allocation=falloc --console-log-level=warn
) else (
    "%aria2Exe%" "!targetUrl!" -d "!defaultSaveLocation!" !outArg! -c !splitArgs! !extraHeaders! --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36" --summary-interval=2 --file-allocation=falloc --console-log-level=warn
)

echo.
echo ========================================================================
echo [✓] Download Finished! Files saved to: %defaultSaveLocation%
echo ========================================================================
echo.
pause
