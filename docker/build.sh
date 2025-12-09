#!/bin/bash

# Docker Build and Push Script
# Builds and pushes Docker images for all agents to container registry

set -e

# Configuration
REGISTRY="${DOCKER_REGISTRY:-ghcr.io}"
PREFIX="${IMAGE_PREFIX:-ai-cloud}"
TAG="${IMAGE_TAG:-latest}"
BUILD_ARGS=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to build Docker image
build_image() {
    local agent=$1
    local dockerfile_path=$2
    local image_name="${REGISTRY}/${PREFIX}-${agent}:${TAG}"
    
    print_info "Building ${agent} agent..."
    
    if [ ! -f "$dockerfile_path" ]; then
        print_error "Dockerfile not found: $dockerfile_path"
        return 1
    fi
    
    docker build \
        -t "${image_name}" \
        -f "$dockerfile_path" \
        ${BUILD_ARGS} \
        .
    
    if [ $? -eq 0 ]; then
        print_info "Successfully built ${image_name}"
    else
        print_error "Failed to build ${image_name}"
        return 1
    fi
}

# Function to push Docker image
push_image() {
    local agent=$1
    local image_name="${REGISTRY}/${PREFIX}-${agent}:${TAG}"
    
    print_info "Pushing ${agent} agent to ${REGISTRY}..."
    
    docker push "${image_name}"
    
    if [ $? -eq 0 ]; then
        print_info "Successfully pushed ${image_name}"
    else
        print_error "Failed to push ${image_name}"
        return 1
    fi
}

# Function to build and push all agents
build_all() {
    local agents=(
        "self-healing:docker/agents/self-healing/Dockerfile"
        "scaling:docker/agents/scaling/Dockerfile"
        "task-solving:docker/agents/task-solving/Dockerfile"
        "performance-monitoring:docker/agents/performance-monitoring/Dockerfile"
        "coding:docker/agents/coding/Dockerfile"
        "security:docker/agents/security/Dockerfile"
        "optimization:docker/agents/optimization/Dockerfile"
    )
    
    for agent_config in "${agents[@]}"; do
        IFS=':' read -r agent dockerfile <<< "$agent_config"
        build_image "$agent" "$dockerfile" || exit 1
    done
}

# Function to push all agents
push_all() {
    local agents=(
        "self-healing"
        "scaling"
        "task-solving"
        "performance-monitoring"
        "coding"
        "security"
        "optimization"
    )
    
    for agent in "${agents[@]}"; do
        push_image "$agent" || exit 1
    done
}

# Main script
main() {
    print_info "Starting Docker build and push process..."
    print_info "Registry: ${REGISTRY}"
    print_info "Prefix: ${PREFIX}"
    print_info "Tag: ${TAG}"
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Check if logged in to registry (if not using public registry)
    if [[ "$REGISTRY" != "docker.io" ]] && [[ "$REGISTRY" != "ghcr.io" ]]; then
        print_warn "Make sure you're logged in to ${REGISTRY}"
        print_warn "Run: docker login ${REGISTRY}"
    fi
    
    # Parse command line arguments
    case "${1:-all}" in
        build)
            build_all
            ;;
        push)
            push_all
            ;;
        all)
            build_all
            push_all
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Usage: $0 [build|push|all]"
            exit 1
            ;;
    esac
    
    print_info "Docker build and push process completed successfully!"
}

# Run main function
main "$@"

