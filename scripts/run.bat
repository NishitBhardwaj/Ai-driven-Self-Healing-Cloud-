@echo off
REM Run script for AI-Driven Self-Healing Cloud Infrastructure System (Windows)
REM This script starts the main server

echo Starting AI-Driven Self-Healing Cloud Infrastructure System...
echo.

REM Check if Go is installed
where go >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Go is not installed or not in PATH
    echo Please install Go from https://golang.org/dl/
    exit /b 1
)

REM Check if dependencies are installed
if not exist "go.sum" (
    echo Installing dependencies...
    go mod download
    go mod tidy
)

REM Run the server
echo Starting server...
go run cmd/server/main.go

