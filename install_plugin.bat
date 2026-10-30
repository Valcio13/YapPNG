@echo off
setlocal

echo ========================================================
echo Installing YapPNG into DaVinci Resolve...
echo ========================================================

set "TARGET_DIR_EDIT=%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Edit"
set "TARGET_DIR_UTIL=%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Utility"

if not exist "%TARGET_DIR_EDIT%" mkdir "%TARGET_DIR_EDIT%"
if not exist "%TARGET_DIR_UTIL%" mkdir "%TARGET_DIR_UTIL%"

:: Copy new YapPNG script
copy /Y "%~dp0YapPNG.py" "%TARGET_DIR_EDIT%\YapPNG.py" >nul
copy /Y "%~dp0YapPNG.py" "%TARGET_DIR_UTIL%\YapPNG.py" >nul

:: Clean up old script name if present
if exist "%TARGET_DIR_EDIT%\PNG_Voice_Animator.py" del /F /Q "%TARGET_DIR_EDIT%\PNG_Voice_Animator.py" >nul
if exist "%TARGET_DIR_UTIL%\PNG_Voice_Animator.py" del /F /Q "%TARGET_DIR_UTIL%\PNG_Voice_Animator.py" >nul

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] YapPNG installed successfully!
    echo.
    echo In DaVinci Resolve, you can now launch it from:
    echo   Workspace ^> Scripts ^> Edit ^> YapPNG
    echo   Workspace ^> Scripts ^> Utility ^> YapPNG
    echo.
) else (
    echo.
    echo [ERROR] Failed to install YapPNG.
)

pause
