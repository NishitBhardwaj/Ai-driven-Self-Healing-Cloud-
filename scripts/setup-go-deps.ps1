# Setup Go Dependencies Script for Windows PowerShell
# Generates go.sum file and ensures all dependencies are properly resolved

Write-Host "Setting up Go dependencies..." -ForegroundColor Green

# Check if Go is installed
if (-not (Get-Command go -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Go is not installed. Please install Go 1.21 or later." -ForegroundColor Red
    exit 1
}

# Check Go version
$goVersion = (go version).Split(' ')[2]
Write-Host "Go version: $goVersion" -ForegroundColor Cyan

# Navigate to project root
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
Set-Location $projectRoot

Write-Host "Running go mod tidy..." -ForegroundColor Yellow
go mod tidy

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: go mod tidy failed" -ForegroundColor Red
    exit 1
}

Write-Host "Downloading dependencies..." -ForegroundColor Yellow
go mod download

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: go mod download failed" -ForegroundColor Red
    exit 1
}

Write-Host "Verifying dependencies..." -ForegroundColor Yellow
go mod verify

if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: go mod verify found issues" -ForegroundColor Yellow
}

# Check if go.sum exists
if (Test-Path "go.sum") {
    $lineCount = (Get-Content "go.sum" | Measure-Object -Line).Lines
    Write-Host "✓ go.sum file generated successfully" -ForegroundColor Green
    Write-Host "File size: $lineCount lines" -ForegroundColor Cyan
} else {
    Write-Host "Error: go.sum file was not generated" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✓ Go dependencies setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Commit go.mod and go.sum files"
Write-Host "2. Build Docker images: .\docker\build.ps1 -Action build"
Write-Host ""

