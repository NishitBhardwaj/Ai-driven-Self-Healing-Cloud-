@echo off
REM Phase 7 System Consistency Check for Windows

echo ==========================================
echo Phase 7 System Consistency Check
echo ==========================================
echo.

echo Checking Auto Mode execution...
go test -v ./tests/phase7 -run TestAutoModeExecution
if %ERRORLEVEL% EQU 0 (
    echo [PASS] Auto Mode executes automatically
) else (
    echo [FAIL] Auto Mode execution failed
)
echo.

echo Checking Manual Mode user input...
go test -v ./tests/phase7 -run TestManualModeUserInput
if %ERRORLEVEL% EQU 0 (
    echo [PASS] Manual Mode shows options and waits
) else (
    echo [FAIL] Manual Mode user input failed
)
echo.

echo Checking Explainability Layer consistency...
go test -v ./tests/phase7 -run TestExplainabilityConsistency
if %ERRORLEVEL% EQU 0 (
    echo [PASS] Explainability Layer is consistent
) else (
    echo [FAIL] Explainability consistency failed
)
echo.

echo Checking WebSocket real-time updates...
go test -v ./tests/phase7 -run TestWebSocketRealTimeUpdates
if %ERRORLEVEL% EQU 0 (
    echo [PASS] WebSocket pushes real-time updates
) else (
    echo [FAIL] WebSocket updates failed
)
echo.

echo Checking Backend API data...
go test -v ./tests/phase7 -run TestBackendAPIData
if %ERRORLEVEL% EQU 0 (
    echo [PASS] Backend APIs return correct data
) else (
    echo [FAIL] Backend API data failed
)
echo.

echo Checking Dashboard interactivity...
go test -v ./tests/phase7 -run TestDashboardInteractivity
if %ERRORLEVEL% EQU 0 (
    echo [PASS] Dashboard updates dynamically
) else (
    echo [FAIL] Dashboard interactivity failed
)
echo.

echo ==========================================
echo Consistency Check Summary
echo ==========================================
echo.
echo All Phase 7 consistency checks completed.
echo.

pause

