@echo off
REM ============================================================================
REM JARVIS AI Assistant - Installer & Launcher
REM This script checks for dependencies, installs them if needed, and runs JARVIS
REM ============================================================================

setlocal enabledelayedexpansion

REM Colors for console output
cls
color 0A
echo.
echo ============================================================================
echo        JARVIS - Personal AI Assistant Installer
echo ============================================================================
echo.

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

REM Check if JARVIS.exe exists
if not exist "%SCRIPT_DIR%\JARVIS.exe" (
    echo [ERROR] JARVIS.exe not found in the same directory!
    echo.
    echo This batch file must be in the same folder as JARVIS.exe
    echo Current location: %SCRIPT_DIR%
    echo.
    pause
    exit /b 1
)

echo [*] JARVIS.exe found at: %SCRIPT_DIR%\JARVIS.exe
echo.

REM Check if Python is installed
echo [*] Checking Python installation...
python --version >nul 2>&1

if errorlevel 1 (
    echo [!] Python is not installed or not in PATH
    echo [!] JARVIS requires Python 3.8 or higher
    echo.
    echo [?] Do you want to:
    echo    1. Download Python from python.org and install it (requires internet)
    echo    2. Continue anyway (may fail)
    echo    3. Exit
    echo.
    set /p choice="Enter your choice (1-3): "
    
    if "%choice%"=="1" (
        echo [+] Opening Python download page...
        start https://www.python.org/downloads/
        echo [!] Please install Python 3.10 or higher, ensure "Add Python to PATH" is checked
        pause
        goto python_check
    ) else if "%choice%"=="2" (
        echo [!] Continuing without Python check...
        goto run_jarvis
    ) else (
        echo [+] Exiting...
        exit /b 0
    )
)

:python_check
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python installation verification failed
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [+] Found: !PYTHON_VERSION!
echo.

REM Create a temporary directory for dependencies if it doesn't exist
set DEPS_DIR=%SCRIPT_DIR%\dependencies
if not exist "%DEPS_DIR%" (
    echo [*] Creating dependencies directory...
    mkdir "%DEPS_DIR%"
)

REM Check and install dependencies
echo [*] Checking required Python packages...
echo.

setlocal enabledelayedexpansion
set PACKAGES=pyyaml psutil speechrecognition sounddevice soundfile requests

for %%p in (%PACKAGES%) do (
    python -c "import %%p" >nul 2>&1
    if errorlevel 1 (
        echo [!] Missing package: %%p
        echo [+] Installing %%p...
        python -m pip install %%p --quiet --upgrade
        if errorlevel 1 (
            echo [ERROR] Failed to install %%p
            echo Please check your internet connection
            pause
            exit /b 1
        )
        echo [+] %%p installed successfully
    ) else (
        echo [OK] %%p is installed
    )
)
endlocal

echo.
echo [+] All dependencies are ready!
echo.

REM Launch JARVIS
:run_jarvis
echo ============================================================================
echo        Launching JARVIS...
echo ============================================================================
echo.

if exist "%SCRIPT_DIR%\JARVIS.exe" (
    start "" "%SCRIPT_DIR%\JARVIS.exe"
    echo [+] JARVIS started successfully!
    echo.
    echo Tips:
    echo - Type 'help' for list of commands
    echo - Type 'pwd' to see current directory
    echo - Type 'ls' to list files
    echo - Type 'open chrome' to open an application
    echo - Type 'what is python' for knowledge queries
    echo.
) else (
    echo [ERROR] JARVIS.exe not found!
    pause
    exit /b 1
)

REM Exit the batch script but let JARVIS run
exit /b 0
