# Docker Build and Push Script for Windows PowerShell
# Builds and pushes Docker images for all agents to container registry

param(
    [string]$Registry = $env:DOCKER_REGISTRY,
    [string]$Prefix = $env:IMAGE_PREFIX,
    [string]$Tag = $env:IMAGE_TAG,
    [Parameter(Mandatory=$false)]
    [ValidateSet("build", "push", "all")]
    [string]$Action = "all"
)

# Set defaults
if ([string]::IsNullOrEmpty($Registry)) { $Registry = "ghcr.io" }
if ([string]::IsNullOrEmpty($Prefix)) { $Prefix = "ai-cloud" }
if ([string]::IsNullOrEmpty($Tag)) { $Tag = "latest" }

# Agents configuration
$agents = @(
    @{Name="self-healing"; Dockerfile="docker/agents/self-healing/Dockerfile"},
    @{Name="scaling"; Dockerfile="docker/agents/scaling/Dockerfile"},
    @{Name="task-solving"; Dockerfile="docker/agents/task-solving/Dockerfile"},
    @{Name="performance-monitoring"; Dockerfile="docker/agents/performance-monitoring/Dockerfile"},
    @{Name="coding"; Dockerfile="docker/agents/coding/Dockerfile"},
    @{Name="security"; Dockerfile="docker/agents/security/Dockerfile"},
    @{Name="optimization"; Dockerfile="docker/agents/optimization/Dockerfile"}
)

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

function Build-Image {
    param(
        [string]$Agent,
        [string]$Dockerfile
    )
    
    $imageName = "${Registry}/${Prefix}-${Agent}:${Tag}"
    
    Write-Info "Building ${Agent} agent..."
    
    if (-not (Test-Path $Dockerfile)) {
        Write-Error "Dockerfile not found: $Dockerfile"
        return $false
    }
    
    docker build -t $imageName -f $Dockerfile .
    
    if ($LASTEXITCODE -eq 0) {
        Write-Info "Successfully built $imageName"
        return $true
    } else {
        Write-Error "Failed to build $imageName"
        return $false
    }
}

function Push-Image {
    param([string]$Agent)
    
    $imageName = "${Registry}/${Prefix}-${Agent}:${Tag}"
    
    Write-Info "Pushing ${Agent} agent to ${Registry}..."
    
    docker push $imageName
    
    if ($LASTEXITCODE -eq 0) {
        Write-Info "Successfully pushed $imageName"
        return $true
    } else {
        Write-Error "Failed to push $imageName"
        return $false
    }
}

function Build-All {
    foreach ($agent in $agents) {
        if (-not (Build-Image -Agent $agent.Name -Dockerfile $agent.Dockerfile)) {
            exit 1
        }
    }
}

function Push-All {
    foreach ($agent in $agents) {
        if (-not (Push-Image -Agent $agent.Name)) {
            exit 1
        }
    }
}

# Main script
Write-Info "Starting Docker build and push process..."
Write-Info "Registry: $Registry"
Write-Info "Prefix: $Prefix"
Write-Info "Tag: $Tag"

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Error "Docker is not running. Please start Docker and try again."
    exit 1
}

# Check if logged in to registry
if ($Registry -ne "docker.io" -and $Registry -ne "ghcr.io") {
    Write-Warn "Make sure you're logged in to $Registry"
    Write-Warn "Run: docker login $Registry"
}

# Execute action
switch ($Action) {
    "build" {
        Build-All
    }
    "push" {
        Push-All
    }
    "all" {
        Build-All
        Push-All
    }
}

Write-Info "Docker build and push process completed successfully!"

