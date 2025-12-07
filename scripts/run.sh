#!/bin/bash

# Run script for AI-Driven Self-Healing Cloud Infrastructure System
# This script starts the main server

set -e

echo "Starting AI-Driven Self-Healing Cloud Infrastructure System..."
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

# Run the server
echo "Starting server..."
go run cmd/server/main.go

