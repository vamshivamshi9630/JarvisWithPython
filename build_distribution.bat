@echo off
REM ============================================================================
REM JARVIS Build Distribution Package Script
REM Rebuilds the executable and prepares distribution files
REM ============================================================================

setlocal enabledelayedexpansion

REM Set colors and clear screen
color 0A
cls

echo.
echo ============================================================================
echo        JARVIS Distribution Builder
echo ============================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ and ensure it's added to PATH
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [+] Found: !PYTHON_VERSION!
echo.

REM Check if PyInstaller is installed
echo [*] Checking PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [!] PyInstaller not found, installing...
    python -m pip install pyinstaller --quiet
    if errorlevel 1 (
        echo [ERROR] Failed to install PyInstaller
        pause
        exit /b 1
    )
    echo [+] PyInstaller installed
) else (
    echo [+] PyInstaller is installed
)

echo.
echo [*] Building JARVIS.exe...
echo.

REM Remove old build artifacts
if exist "build\" (
    echo [*] Cleaning old build directory...
    rmdir /s /q build >nul 2>&1
)

if exist "dist\" (
    REM Keep dist folder but clean build files
    for /d %%d in (dist\build*) do rmdir /s /q "%%d" >nul 2>&1
)

REM Create dist directory if it doesn't exist
if not exist "dist\" (
    mkdir dist
)

REM Build the executable
echo [*] Compiling Python code to executable...
python -m PyInstaller --onefile --name JARVIS --distpath ./dist --workpath ./build --specpath ./build -y jarvis.py

if errorlevel 1 (
    echo [ERROR] PyInstaller build failed!
    pause
    exit /b 1
)

echo.
echo [+] Build completed successfully!
echo.

REM Check if files were created
if exist "dist\JARVIS.exe" (
    for /f %%A in ('dir /b dist\JARVIS.exe ^| find /c ":"') do if not "%%A"=="0" (
        REM Get file size
        for %%F in (dist\JARVIS.exe) do set SIZE=%%~zF
        set /a SIZE_MB=!SIZE! / 1048576
        echo [+] JARVIS.exe created successfully (!SIZE_MB! MB)
    )
) else (
    echo [ERROR] JARVIS.exe was not created in dist folder
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo        Distribution Package Ready!
echo ============================================================================
echo.
echo Location: dist\
echo.
echo Files ready for distribution:
echo  - dist\JARVIS.exe                 (Standalone executable)
echo  - dist\JARVIS_INSTALLER.bat       (Full installer script)
echo  - dist\run_jarvis.bat             (Quick launcher)
echo  - dist\run_jarvis.ps1             (PowerShell launcher)
echo.
echo To share JARVIS with others:
echo  1. Send: JARVIS.exe + JARVIS_INSTALLER.bat
echo  2. Recipients double-click JARVIS_INSTALLER.bat
echo  3. JARVIS launches automatically!
echo.
echo For complete distribution guide, see: DISTRIBUTION_GUIDE.md
echo.

pause
