# Health Check Validation Script for Windows PowerShell
# Validates all agent health endpoints

param(
    [string]$Namespace = "ai-cloud-production",
    [string]$BaseUrl = "http://localhost",
    [int]$Timeout = 10
)

# Agents configuration
$agents = @{
    "self-healing" = 8080
    "scaling" = 8080
    "task-solving" = 8080
    "performance-monitoring" = 8080
    "coding" = 8080
    "security" = 8080
    "optimization" = 8080
}

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Test-Health {
    param(
        [string]$Agent,
        [int]$Port
    )
    
    $url = "${BaseUrl}:${Port}/health"
    Write-Info "Checking health for ${Agent} agent at ${url}..."
    
    try {
        $response = Invoke-WebRequest -Uri $url -TimeoutSec $Timeout -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Info "✓ ${Agent} agent is healthy (HTTP $($response.StatusCode))"
            return $true
        } else {
            Write-Error "✗ ${Agent} agent is unhealthy (HTTP $($response.StatusCode))"
            return $false
        }
    } catch {
        Write-Error "✗ ${Agent} agent is unhealthy: $($_.Exception.Message)"
        return $false
    }
}

function Test-Readiness {
    param(
        [string]$Agent,
        [int]$Port
    )
    
    $url = "${BaseUrl}:${Port}/ready"
    Write-Info "Checking readiness for ${Agent} agent at ${url}..."
    
    try {
        $response = Invoke-WebRequest -Uri $url -TimeoutSec $Timeout -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Info "✓ ${Agent} agent is ready (HTTP $($response.StatusCode))"
            return $true
        } else {
            Write-Warn "✗ ${Agent} agent is not ready (HTTP $($response.StatusCode))"
            return $false
        }
    } catch {
        Write-Warn "✗ ${Agent} agent is not ready: $($_.Exception.Message)"
        return $false
    }
}

function Test-Metrics {
    param(
        [string]$Agent,
        [int]$Port
    )
    
    $metricsPort = $Port + 1
    $url = "${BaseUrl}:${metricsPort}/metrics"
    Write-Info "Checking metrics for ${Agent} agent at ${url}..."
    
    try {
        $response = Invoke-WebRequest -Uri $url -TimeoutSec $Timeout -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Info "✓ ${Agent} agent metrics available (HTTP $($response.StatusCode))"
            return $true
        } else {
            Write-Warn "✗ ${Agent} agent metrics unavailable (HTTP $($response.StatusCode))"
            return $false
        }
    } catch {
        Write-Warn "✗ ${Agent} agent metrics unavailable: $($_.Exception.Message)"
        return $false
    }
}

# Main validation
Write-Info "Starting health check validation..."
Write-Info "Namespace: $Namespace"
Write-Info "Base URL: $BaseUrl"
Write-Info ""

$total = 0
$passed = 0
$failed = 0

foreach ($agent in $agents.Keys) {
    $port = $agents[$agent]
    $total += 3  # health, readiness, metrics
    
    # Health check
    if (Test-Health -Agent $agent -Port $port) {
        $passed++
    } else {
        $failed++
    }
    
    # Readiness check
    if (Test-Readiness -Agent $agent -Port $port) {
        $passed++
    } else {
        $failed++
    }
    
    # Metrics check
    if (Test-Metrics -Agent $agent -Port $port) {
        $passed++
    } else {
        $failed++
    }
    
    Write-Host ""
}

# Summary
Write-Info "Validation Summary:"
Write-Info "  Total checks: $total"
Write-Info "  Passed: $passed"
if ($failed -gt 0) {
    Write-Error "  Failed: $failed"
    exit 1
} else {
    Write-Info "  Failed: $failed"
    Write-Info "All health checks passed! ✓"
    exit 0
}

