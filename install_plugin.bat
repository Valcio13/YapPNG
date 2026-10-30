@echo off
setlocal

echo ========================================================
echo Installing PNG Voice Animator into DaVinci Resolve...
echo ========================================================

set "TARGET_DIR_EDIT=%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Edit"
set "TARGET_DIR_UTIL=%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Utility"

if not exist "%TARGET_DIR_EDIT%" mkdir "%TARGET_DIR_EDIT%"
if not exist "%TARGET_DIR_UTIL%" mkdir "%TARGET_DIR_UTIL%"

copy /Y "%~dp0PNG_Voice_Animator.py" "%TARGET_DIR_EDIT%\PNG_Voice_Animator.py" >nul
copy /Y "%~dp0PNG_Voice_Animator.py" "%TARGET_DIR_UTIL%\PNG_Voice_Animator.py" >nul

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] Script installed successfully!
    echo.
    echo In DaVinci Resolve, you can now open it from:
    echo   Workspace ^> Scripts ^> Edit ^> PNG_Voice_Animator
    echo   Workspace ^> Scripts ^> Utility ^> PNG_Voice_Animator
    echo.
) else (
    echo.
    echo [ERROR] Failed to copy files.
)

pause
