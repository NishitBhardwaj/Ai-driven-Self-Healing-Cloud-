#!/bin/bash

# Setup Go Dependencies Script
# Generates go.sum file and ensures all dependencies are properly resolved

set -e

echo "Setting up Go dependencies..."

# Check if Go is installed
if ! command -v go &> /dev/null; then
    echo "Error: Go is not installed. Please install Go 1.21 or later."
    exit 1
fi

# Check Go version
GO_VERSION=$(go version | awk '{print $3}' | sed 's/go//')
echo "Go version: $GO_VERSION"

# Navigate to project root
cd "$(dirname "$0")/.."

echo "Running go mod tidy..."
go mod tidy

echo "Downloading dependencies..."
go mod download

echo "Verifying dependencies..."
go mod verify

echo "Generating go.sum..."
# go mod tidy already generates go.sum, but we'll verify it exists
if [ -f "go.sum" ]; then
    echo "✓ go.sum file generated successfully"
    echo "File size: $(wc -l < go.sum) lines"
else
    echo "Warning: go.sum file was not generated"
    exit 1
fi

echo ""
echo "✓ Go dependencies setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Commit go.mod and go.sum files"
echo "2. Build Docker images: ./docker/build.sh build"
echo ""

