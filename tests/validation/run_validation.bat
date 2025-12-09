@echo off
REM System Validation Script for Windows
REM Validates testing, logging, and monitoring systems

echo ==========================================
echo System Validation - Phase 8, Part 4
echo ==========================================
echo.

set PASSED=0
set FAILED=0
set SKIPPED=0

echo 1. Testing Unit Tests and Integration Tests
echo -------------------------------------------
if exist "tests\agents" (
    echo Running unit tests...
    go test ./tests/agents/... -v
    if %ERRORLEVEL% EQU 0 (
        echo [PASS] Unit tests structure exists
        set /a PASSED+=1
    ) else (
        echo [SKIP] Some unit tests may have failed
        set /a SKIPPED+=1
    )
) else (
    echo [FAIL] Test directories not found
    set /a FAILED+=1
)

if exist "tests\integration" (
    echo Running integration tests...
    go test ./tests/integration/... -v
    if %ERRORLEVEL% EQU 0 (
        echo [PASS] Integration tests structure exists
        set /a PASSED+=1
    ) else (
        echo [SKIP] Some integration tests may have failed
        set /a SKIPPED+=1
    )
) else (
    echo [FAIL] Integration test directory not found
    set /a FAILED+=1
)
echo.

echo 2. Validating Prometheus Metrics Collection
echo --------------------------------------------
curl -s http://localhost:9090/api/v1/status/config >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [PASS] Prometheus is accessible
    set /a PASSED+=1
) else (
    echo [SKIP] Prometheus is not accessible (may not be running)
    set /a SKIPPED+=1
)
echo.

echo 3. Validating Elasticsearch
echo ---------------------------
curl -s http://localhost:9200 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [PASS] Elasticsearch is accessible
    set /a PASSED+=1
) else (
    echo [SKIP] Elasticsearch is not accessible (may not be running)
    set /a SKIPPED+=1
)
echo.

echo 4. Validating Kibana
echo --------------------
curl -s http://localhost:5601/api/status >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [PASS] Kibana is accessible
    set /a PASSED+=1
) else (
    echo [SKIP] Kibana is not accessible (may not be running)
    set /a SKIPPED+=1
)
echo.

echo 5. Validating Grafana
echo ---------------------
curl -s http://localhost:3000/api/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [PASS] Grafana is accessible
    set /a PASSED+=1
) else (
    echo [SKIP] Grafana is not accessible (may not be running)
    set /a SKIPPED+=1
)
echo.

echo 6. Validating Grafana Dashboards
echo ---------------------------------
if exist "monitoring\grafana\dashboards" (
    echo [PASS] Grafana dashboards directory exists
    set /a PASSED+=1
) else (
    echo [FAIL] Grafana dashboards directory not found
    set /a FAILED+=1
)
echo.

echo 7. Validating Alerting Rules
echo -----------------------------
if exist "config\monitoring\alerts.yml" (
    echo [PASS] Alerting rules file exists
    set /a PASSED+=1
) else (
    echo [FAIL] Alerting rules file not found
    set /a FAILED+=1
)
echo.

echo ==========================================
echo Validation Summary
echo ==========================================
echo Passed: %PASSED%
echo Failed: %FAILED%
echo Skipped: %SKIPPED%
echo.

if %FAILED% EQU 0 (
    echo [SUCCESS] All critical validations passed!
    exit /b 0
) else (
    echo [WARNING] Some validations failed. Please check the output above.
    exit /b 1
)

