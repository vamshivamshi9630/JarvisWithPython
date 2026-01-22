# JARVIS Distribution Builder Script (PowerShell)
# Rebuilds the executable and prepares distribution files
# Usage: powershell -ExecutionPolicy Bypass -File "build_distribution.ps1"

param(
    [switch]$Clean = $false,
    [switch]$SkipBuild = $false
)

# Color functions
function Write-Success { Write-Host "[+] $args" -ForegroundColor Green }
function Write-Info { Write-Host "[*] $args" -ForegroundColor Cyan }
function Write-Warning { Write-Host "[!] $args" -ForegroundColor Yellow }
function Write-Error { Write-Host "[ERROR] $args" -ForegroundColor Red }

# Header
Clear-Host
Write-Host "============================================================================" -ForegroundColor Green
Write-Host "        JARVIS Distribution Builder (PowerShell)" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Green
Write-Host ""

$ScriptDir = Get-Location
Write-Info "Working directory: $ScriptDir"
Write-Host ""

# Check Python
Write-Info "Checking Python installation..."
try {
    $PythonVersion = & python --version 2>&1
    Write-Success "Found: $PythonVersion"
} catch {
    Write-Error "Python not found. Please install Python 3.8+ and add to PATH"
    exit 1
}

# Check PyInstaller
Write-Info "Checking PyInstaller..."
try {
    $null = & python -c "import PyInstaller"
    Write-Success "PyInstaller is installed"
} catch {
    Write-Warning "PyInstaller not found, installing..."
    & python -m pip install pyinstaller --quiet --upgrade
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install PyInstaller"
        exit 1
    }
    Write-Success "PyInstaller installed"
}

# Cleanup if requested
if ($Clean) {
    Write-Warning "Cleaning old build artifacts..."
    Remove-Item -Path "build", "dist\build*" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Success "Cleanup complete"
}

# Create dist directory
if (-not (Test-Path "dist")) {
    New-Item -ItemType Directory -Path "dist" | Out-Null
    Write-Info "Created dist directory"
}

# Build executable
if (-not $SkipBuild) {
    Write-Host ""
    Write-Info "Building JARVIS.exe..."
    Write-Host ""
    
    & python -m PyInstaller --onefile --name JARVIS `
        --distpath ./dist --workpath ./build --specpath ./build -y jarvis.py
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "PyInstaller build failed"
        exit 1
    }
}

# Verify build
Write-Host ""
if (Test-Path "dist\JARVIS.exe") {
    $ExeSize = (Get-Item "dist\JARVIS.exe").Length / 1MB
    Write-Success "JARVIS.exe created successfully ({0:F2} MB)" -f $ExeSize
} else {
    Write-Error "JARVIS.exe not found in dist folder"
    exit 1
}

# List distribution files
Write-Host ""
Write-Host "============================================================================" -ForegroundColor Green
Write-Host "        Distribution Package Ready!" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Green
Write-Host ""

$DistFiles = @(
    @{ Name = "JARVIS.exe"; Path = "dist\JARVIS.exe"; Desc = "Standalone executable" },
    @{ Name = "JARVIS_INSTALLER.bat"; Path = "dist\JARVIS_INSTALLER.bat"; Desc = "Full installer" },
    @{ Name = "run_jarvis.bat"; Path = "dist\run_jarvis.bat"; Desc = "Quick launcher" },
    @{ Name = "run_jarvis.ps1"; Path = "dist\run_jarvis.ps1"; Desc = "PowerShell launcher" }
)

$DistFiles | ForEach-Object {
    if (Test-Path $_.Path) {
        $Size = (Get-Item $_.Path).Length
        if ($Size -gt 1MB) {
            $SizeStr = "{0:F2} MB" -f ($Size / 1MB)
        } else {
            $SizeStr = "{0:F2} KB" -f ($Size / 1KB)
        }
        Write-Host ("  ✓ {0,-30} ({1,10})  - {2}" -f $_.Name, $SizeStr, $_.Desc) -ForegroundColor Green
    } else {
        Write-Host ("  ✗ {0,-30} (MISSING)       - {1}" -f $_.Name, $_.Desc) -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Distribution Methods:" -ForegroundColor Cyan
Write-Host "  1. Send JARVIS.exe + JARVIS_INSTALLER.bat via email/file share"
Write-Host "  2. Create ZIP: Compress-Archive -Path dist -DestinationPath JARVIS.zip"
Write-Host "  3. Copy dist/ folder to USB drive"
Write-Host "  4. Upload to GitHub/OneDrive for public distribution"
Write-Host ""

Write-Host "For complete guide, see: DISTRIBUTION_GUIDE.md" -ForegroundColor Cyan
Write-Host ""
Write-Success "Build complete!"

exit 0
