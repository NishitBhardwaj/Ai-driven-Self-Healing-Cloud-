# Scripts Directory

This folder contains helper scripts for various automation tasks, maintenance operations, and system management. These scripts help streamline common operations and reduce manual work.

## Overview

Scripts in this directory are organized by functionality:

- **Deployment Scripts**: Automate deployment processes
- **Maintenance Scripts**: System maintenance and cleanup
- **Testing Scripts**: Test automation and validation
- **Monitoring Scripts**: Health checks and status reports
- **Utility Scripts**: Common utility functions

## Script Categories

### Deployment Scripts

- **`deploy.sh`**: Deploy agents to Kubernetes
- **`rollback.sh`**: Rollback to previous deployment
- **`update-config.sh`**: Update agent configurations

### Maintenance Scripts

- **`cleanup-logs.sh`**: Clean up old log files
- **`backup-databases.sh`**: Backup all databases
- **`restore-database.sh`**: Restore database from backup
- **`health-check.sh`**: System health check

### Testing Scripts

- **`run-tests.sh`**: Run all test suites
- **`integration-test.sh`**: Run integration tests
- **`load-test.sh`**: Run load tests

### Monitoring Scripts

- **`check-status.sh`**: Check agent status
- **`collect-metrics.sh`**: Collect system metrics
- **`generate-report.sh`**: Generate monitoring reports

## Usage

### Running Scripts

Most scripts are executable and can be run directly:

```bash
# Make script executable
chmod +x scripts/deploy.sh

# Run script
./scripts/deploy.sh
```

### Script Parameters

Scripts accept parameters for customization:

```bash
# Deploy specific agent
./scripts/deploy.sh --agent self-healing --environment production

# Run tests with coverage
./scripts/run-tests.sh --coverage --verbose
```

## Common Scripts

### Deployment

**`deploy.sh`**: Deploy agents to Kubernetes

```bash
./scripts/deploy.sh --agent self-healing --version 1.2.0 --namespace production
```

**`rollback.sh`**: Rollback deployment

```bash
./scripts/rollback.sh --agent self-healing --version 1.1.0
```

### Maintenance

**`backup-databases.sh`**: Backup all databases

```bash
./scripts/backup-databases.sh --output /backups --compress
```

**`cleanup-logs.sh`**: Clean up old logs

```bash
./scripts/cleanup-logs.sh --days 30 --dry-run
```

### Testing

**`run-tests.sh`**: Run all tests

```bash
./scripts/run-tests.sh --unit --integration --coverage
```

**`load-test.sh`**: Run load tests

```bash
./scripts/load-test.sh --agents 10 --duration 5m --rate 100
```

### Monitoring

**`check-status.sh`**: Check system status

```bash
./scripts/check-status.sh --all-agents --detailed
```

**`collect-metrics.sh`**: Collect metrics

```bash
./scripts/collect-metrics.sh --output metrics.json --duration 1h
```

## Script Development Guidelines

### Best Practices

1. **Error Handling**: Always include error handling
2. **Logging**: Log script execution and errors
3. **Documentation**: Document script purpose and parameters
4. **Idempotency**: Scripts should be idempotent when possible
5. **Dry Run**: Support dry-run mode for destructive operations

### Script Template

```bash
#!/bin/bash

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/../logs/script.log"

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    log "ERROR: $1"
    exit 1
}

# Main function
main() {
    log "Starting script execution"
    # Script logic here
    log "Script execution completed"
}

# Run main function
main "$@"
```

## Environment Variables

Scripts use environment variables for configuration:

```bash
# Set environment variables
export KUBECONFIG=/path/to/kubeconfig
export DOCKER_REGISTRY=your-registry.com
export ENVIRONMENT=production

# Run script
./scripts/deploy.sh
```

## Script Dependencies

Some scripts require additional tools:

- **kubectl**: For Kubernetes operations
- **docker**: For container operations
- **jq**: For JSON processing
- **curl**: For HTTP requests
- **aws-cli**: For AWS operations

Install dependencies:

```bash
# Install jq
brew install jq  # macOS
apt-get install jq  # Ubuntu

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
```

## Testing Scripts

Test scripts before using in production:

```bash
# Test with dry-run
./scripts/deploy.sh --dry-run

# Test with verbose output
./scripts/backup-databases.sh --verbose --test
```

## Troubleshooting

### Script Not Executable

```bash
chmod +x scripts/script-name.sh
```

### Permission Denied

```bash
# Check file permissions
ls -l scripts/script-name.sh

# Fix permissions
chmod 755 scripts/script-name.sh
```

### Script Errors

- Check script logs: `tail -f logs/script.log`
- Run with verbose mode: `./scripts/script-name.sh --verbose`
- Check dependencies: Verify all required tools are installed

## Contributing

When adding new scripts:

1. Follow the script template
2. Add error handling and logging
3. Document script purpose and parameters
4. Test script thoroughly
5. Update this README with script description

## Related Documentation

- Deployment: `/kubernetes/README.md`
- CI/CD: `/ci-cd/README.md`
- Testing: `/tests/README.md`

