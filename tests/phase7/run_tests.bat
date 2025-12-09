@echo off
REM Phase 7 Test Runner for Windows
REM Runs all Phase 7 tests and generates a summary report

echo ==========================================
echo Phase 7 Testing ^& Validation
echo ==========================================
echo.

echo Running WebSocket tests...
go test -v ./tests/phase7 -run TestWebSocket
if %ERRORLEVEL% EQU 0 (
    echo [PASS] WebSocket tests passed
) else (
    echo [FAIL] WebSocket tests failed
)
echo.

echo Running Decision UI tests...
go test -v ./tests/phase7 -run TestDecision
if %ERRORLEVEL% EQU 0 (
    echo [PASS] Decision UI tests passed
) else (
    echo [FAIL] Decision UI tests failed
)
echo.

echo Running API tests...
go test -v ./tests/phase7 -run TestAPI
if %ERRORLEVEL% EQU 0 (
    echo [PASS] API tests passed
) else (
    echo [FAIL] API tests failed
)
echo.

echo Running Explainability tests...
go test -v ./tests/phase7 -run TestExplanation
if %ERRORLEVEL% EQU 0 (
    echo [PASS] Explainability tests passed
) else (
    echo [FAIL] Explainability tests failed
)
echo.

echo ==========================================
echo Test Summary
echo ==========================================
echo.
echo All Phase 7 tests completed.
echo.

pause

