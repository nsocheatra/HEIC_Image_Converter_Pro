# HEIC Image Converter Pro - PowerShell Installer
# Run: powershell -ExecutionPolicy Bypass -File install.ps1

$AppName = "HEIC Image Converter Pro"
$ExeName = "HEIC_Image_Converter_Pro.exe"
$SourcePath = Join-Path $PSScriptRoot "dist" $ExeName
$InstallDir = Join-Path $env:LOCALAPPDATA "Programs\HEIC Image Converter Pro"
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$StartMenuPath = Join-Path ([Environment]::GetFolderPath("StartMenu")) "Programs\HEIC Image Converter Pro"

function Write-Banner {
    Clear-Host
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  HEIC Image Converter Pro - Installer  " -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Test-Admin {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Install-Application {
    Write-Banner
    Write-Host "Installing to: $InstallDir" -ForegroundColor Yellow
    Write-Host ""

    if (-not (Test-Path $SourcePath)) {
        Write-Host "ERROR: $ExeName not found at: $SourcePath" -ForegroundColor Red
        Write-Host "Make sure the executable has been built first." -ForegroundColor Red
        Write-Host ""
        Write-Host "Build it with: pyinstaller ... (see README)" -ForegroundColor Gray
        return $false
    }

    New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
    Copy-Item $SourcePath (Join-Path $InstallDir $ExeName) -Force

    # Copy FFmpeg if available
    $ffmpegSource = Join-Path $PSScriptRoot "ffmpeg"
    if (Test-Path $ffmpegSource) {
        $ffmpegDest = Join-Path $InstallDir "ffmpeg"
        Copy-Item "$ffmpegSource\*" $ffmpegDest -Recurse -Force -ErrorAction SilentlyContinue
    }

    New-Item -ItemType Directory -Force -Path $StartMenuPath | Out-Null
    $shortcutPath = Join-Path $StartMenuPath "$AppName.lnk"
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = Join-Path $InstallDir $ExeName
    $shortcut.WorkingDirectory = $InstallDir
    $shortcut.Description = "Convert HEIC/HEIF images to popular formats"
    $shortcut.Save()

    $desktopShortcut = Join-Path $DesktopPath "$AppName.lnk"
    $shortcut = $shell.CreateShortcut($desktopShortcut)
    $shortcut.TargetPath = Join-Path $InstallDir $ExeName
    $shortcut.WorkingDirectory = $InstallDir
    $shortcut.Description = "Convert HEIC/HEIF images to popular formats"
    $shortcut.Save()

    Write-Host "✓ Installed successfully!" -ForegroundColor Green
    Write-Host "Location: $InstallDir" -ForegroundColor Gray
    Write-Host "Start Menu shortcut created" -ForegroundColor Gray
    Write-Host "Desktop shortcut created" -ForegroundColor Gray
    Write-Host ""

    $launch = Read-Host "Launch $AppName now? (Y/N)"
    if ($launch -eq "Y" -or $launch -eq "y") {
        Start-Process (Join-Path $InstallDir $ExeName)
    }
    return $true
}

function Uninstall-Application {
    Write-Banner
    Write-Host "Uninstalling..." -ForegroundColor Yellow

    if (Test-Path $InstallDir) {
        Remove-Item $InstallDir -Recurse -Force
        Write-Host "✓ Removed program files" -ForegroundColor Green
    }

    if (Test-Path $StartMenuPath) {
        Remove-Item $StartMenuPath -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "✓ Removed Start Menu shortcuts" -ForegroundColor Green
    }

    $desktopShortcut = Join-Path $DesktopPath "$AppName.lnk"
    if (Test-Path $desktopShortcut) {
        Remove-Item $desktopShortcut -Force -ErrorAction SilentlyContinue
        Write-Host "✓ Removed desktop shortcut" -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "Uninstall complete." -ForegroundColor Green
}

# Main
Write-Banner
Write-Host "1. Install" -ForegroundColor White
Write-Host "2. Uninstall" -ForegroundColor White
Write-Host "3. Exit" -ForegroundColor White
Write-Host ""
$choice = Read-Host "Select option (1-3)"

switch ($choice) {
    "1" { Install-Application }
    "2" { Uninstall-Application }
    default { Write-Host "Exiting." }
}

if ($choice -ne "3") {
    Write-Host ""
    Read-Host "Press Enter to exit"
}
