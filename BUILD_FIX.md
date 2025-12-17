# Docker Build Fix - Complete Solution

## Problem
Docker builds were failing with missing Go dependencies and go.sum file errors.

## Solution Applied

### 1. Updated `go.mod` with Missing Dependencies
Added all required dependencies:
- **Prometheus client libraries**: `github.com/prometheus/client_golang`
- **AWS SDK**: `github.com/aws/aws-sdk-go`
- **Kubernetes client libraries**: `k8s.io/api`, `k8s.io/apimachinery`, `k8s.io/client-go`

### 2. Fixed All Dockerfiles
Updated all 7 agent Dockerfiles:
- Changed Go version from `1.24-alpine` to `1.21-alpine` (matching go.mod)
- Added `go mod tidy` before building to ensure all dependencies are resolved
- Fixed build order: copy source code first, then run `go mod tidy && go mod download`

### 3. Created Setup Scripts
- `scripts/setup-go-deps.sh` - Linux/Mac script to generate go.sum
- `scripts/setup-go-deps.ps1` - Windows PowerShell script to generate go.sum

### 4. Updated CI/CD Workflows
- Added Go setup step in `.github/workflows/cd.yml`
- Added go.sum generation step before Docker builds
- Updated `.github/workflows/ci.yml` with same fixes

## How to Fix Locally

### Option 1: Use Setup Script (Recommended)

**Linux/Mac:**
```bash
chmod +x scripts/setup-go-deps.sh
./scripts/setup-go-deps.sh
```

**Windows:**
```powershell
.\scripts\setup-go-deps.ps1
```

### Option 2: Manual Fix

```bash
# Navigate to project root
cd /path/to/Ai-driven-Self-Healing-Cloud-

# Generate go.sum
go mod tidy
go mod download
go mod verify

# Verify go.sum exists
ls -la go.sum
```

### Option 3: Build Docker Images

After generating go.sum, build images:

**Linux/Mac:**
```bash
./docker/build.sh build
```

**Windows:**
```powershell
.\docker\build.ps1 -Action build
```

## Files Changed

1. ✅ `go.mod` - Added all missing dependencies
2. ✅ `docker/agents/self-healing/Dockerfile` - Fixed build process
3. ✅ `docker/agents/scaling/Dockerfile` - Fixed build process
4. ✅ `docker/agents/task-solving/Dockerfile` - Fixed build process
5. ✅ `docker/agents/performance-monitoring/Dockerfile` - Fixed build process
6. ✅ `docker/agents/coding/Dockerfile` - Fixed build process
7. ✅ `docker/agents/security/Dockerfile` - Fixed build process
8. ✅ `docker/agents/optimization/Dockerfile` - Fixed build process
9. ✅ `.github/workflows/cd.yml` - Added go.sum generation
10. ✅ `.github/workflows/ci.yml` - Added go.sum generation
11. ✅ `scripts/setup-go-deps.sh` - New helper script
12. ✅ `scripts/setup-go-deps.ps1` - New helper script

## Next Steps

1. **Generate go.sum locally:**
   ```bash
   ./scripts/setup-go-deps.sh
   ```

2. **Commit the changes:**
   ```bash
   git add go.mod go.sum
   git add docker/agents/*/Dockerfile
   git add .github/workflows/*.yml
   git add scripts/setup-go-deps.*
   git commit -m "Fix: Add missing Go dependencies and update Dockerfiles"
   git push
   ```

3. **Verify build works:**
   ```bash
   docker build -t test-self-healing -f docker/agents/self-healing/Dockerfile .
   ```

## Verification

After applying fixes, verify:

```bash
# Check go.mod has all dependencies
grep -E "(prometheus|aws-sdk|k8s.io)" go.mod

# Check Dockerfile uses correct Go version
grep "FROM golang" docker/agents/*/Dockerfile

# Check Dockerfile runs go mod tidy
grep "go mod tidy" docker/agents/*/Dockerfile
```

## Common Issues

### Issue: "missing go.sum entry"
**Solution:** Run `go mod tidy` to generate go.sum

### Issue: "no required module provides package"
**Solution:** The package needs to be added to go.mod. Run `go get <package>` then `go mod tidy`

### Issue: "golang:1.24-alpine not found"
**Solution:** Changed to `golang:1.21-alpine` to match go.mod version

## Dependencies Added

- `github.com/aws/aws-sdk-go v1.50.0`
- `github.com/prometheus/client_golang v1.19.0`
- `k8s.io/api v0.29.2`
- `k8s.io/apimachinery v0.29.2`
- `k8s.io/client-go v0.29.2`

Plus all transitive dependencies (automatically added by `go mod tidy`)

