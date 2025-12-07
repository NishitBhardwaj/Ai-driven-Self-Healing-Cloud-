@echo off
REM LLM Test script for AI-Driven Self-Healing Cloud Infrastructure System (Windows)
REM This script tests connectivity to OpenRouter and Gemini APIs

echo Testing LLM API Connectivity...
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

REM Run the LLM test
echo Running LLM connectivity tests...
go run agents/llm-test/llm_test.go

