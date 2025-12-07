#!/bin/bash

# LLM Test script for AI-Driven Self-Healing Cloud Infrastructure System
# This script tests connectivity to OpenRouter and Gemini APIs

set -e

echo "Testing LLM API Connectivity..."
echo ""

# Check if Go is installed
if ! command -v go &> /dev/null; then
    echo "Error: Go is not installed or not in PATH"
    echo "Please install Go from https://golang.org/dl/"
    exit 1
fi

# Check if dependencies are installed
if [ ! -f "go.sum" ]; then
    echo "Installing dependencies..."
    go mod download
    go mod tidy
fi

# Run the LLM test
echo "Running LLM connectivity tests..."
go run agents/llm-test/llm_test.go

