param(
    [string]$OutputDir = "$PSScriptRoot/../heic_converter_pro/app/ffmpeg"
)

$FFMPEG_VERSION = "7.1"
$FFMPEG_URL = "https://github.com/GyanD/codexffmpeg/releases/download/$FFMPEG_VERSION/ffmpeg-$FFMPEG_VERSION-full_build.7z"
$TempDir = "$env:TEMP\ffmpeg_download"

Write-Host "Downloading FFmpeg $FFMPEG_VERSION..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path $TempDir | Out-Null
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

curl.exe -L -o "$TempDir\ffmpeg.7z" $FFMPEG_URL
if (-not (Test-Path "$TempDir\ffmpeg.7z")) {
    Write-Error "Failed to download FFmpeg"
    exit 1
}

Write-Host "Extracting..." -ForegroundColor Cyan
7z x "$TempDir\ffmpeg.7z" -o"$TempDir\extracted" -y -bso0 -bsp0
$BinDir = Get-ChildItem "$TempDir\extracted" -Directory | Select-Object -First 1

Copy-Item "$BinDir\bin\ffmpeg.exe" "$OutputDir\ffmpeg.exe" -Force
Copy-Item "$BinDir\bin\ffprobe.exe" "$OutputDir\ffprobe.exe" -Force

Remove-Item -Recurse -Force $TempDir

Write-Host "FFmpeg installed to $OutputDir" -ForegroundColor Green
