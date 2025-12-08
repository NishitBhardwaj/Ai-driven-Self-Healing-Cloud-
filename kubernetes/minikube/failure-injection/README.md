# Failure Injection - Chaos Engineering

This directory contains scripts for injecting failures into the Kubernetes cluster to test the Self-Healing Agent's capabilities.

## Overview

These scripts simulate various failure scenarios that the Self-Healing Agent should detect and remediate:

- **Pod Failures**: Random pod terminations
- **Resource Pressure**: CPU and memory overload
- **Network Issues**: Latency and connectivity problems
- **Service Failures**: Service unavailability

## Scripts

### 1. kill_random_pod.sh

Randomly kills a pod from a deployment or namespace to test automatic pod recreation.

**Usage:**
```bash
# Kill random pod from namespace
./kill_random_pod.sh

# Kill random pod from specific deployment
DEPLOYMENT=compute-service ./kill_random_pod.sh

# Kill random pod from specific service
SERVICE=storage-service ./kill_random_pod.sh

# Specify namespace
NAMESPACE=self-healing-cloud DEPLOYMENT=logging-service ./kill_random_pod.sh
```

**What it tests:**
- Pod failure detection
- Automatic pod recreation
- Deployment self-healing
- Service availability during pod failures

### 2. overload_cpu.sh

Creates CPU-intensive workloads to test autoscaling and resource management.

**Usage:**
```bash
# Create CPU stress pod (default: 100% CPU for 5 minutes)
./overload_cpu.sh

# Custom duration and CPU load
DURATION=600 CPU_LOAD=200 ./overload_cpu.sh

# Overload specific deployment
DEPLOYMENT=compute-service DURATION=300 ./overload_cpu.sh

# Specify namespace
NAMESPACE=self-healing-cloud ./overload_cpu.sh
```

**Parameters:**
- `DURATION`: Duration in seconds (default: 300)
- `CPU_LOAD`: CPU cores to stress (default: 100)
- `DEPLOYMENT`: Target deployment to overload
- `NAMESPACE`: Target namespace (default: self-healing-cloud)

**What it tests:**
- HPA (Horizontal Pod Autoscaler) response
- CPU resource monitoring
- Autoscaling triggers
- Resource limit enforcement

### 3. inject_network_latency.sh

Injects network latency between services to test resilience to network issues.

**Usage:**
```bash
# Inject latency (requires Chaos Mesh or similar)
./inject_network_latency.sh

# Custom latency and duration
LATENCY=200ms DURATION=600 ./inject_network_latency.sh

# Target specific services
SOURCE_SERVICE=compute-service TARGET_SERVICE=storage-service ./inject_network_latency.sh
```

**Parameters:**
- `LATENCY`: Network latency to inject (default: 100ms)
- `DURATION`: Duration in seconds (default: 300)
- `SOURCE_SERVICE`: Source service for latency injection
- `TARGET_SERVICE`: Target service for latency injection
- `NAMESPACE`: Target namespace (default: self-healing-cloud)

**Requirements:**
- Chaos Mesh (recommended) for proper latency injection
- Or privileged access for iptables manipulation

**What it tests:**
- Network failure detection
- Timeout handling
- Circuit breaker patterns
- Retry mechanisms

### 4. delete_service.sh

Deletes a Kubernetes service to simulate service unavailability.

**Usage:**
```bash
# Delete service (with backup)
SERVICE=compute-service ./delete_service.sh

# Delete without backup
SERVICE=storage-service BACKUP=false ./delete_service.sh

# Auto-restore after duration
SERVICE=logging-service RESTORE_AFTER=60 ./delete_service.sh
```

**Parameters:**
- `SERVICE`: Service name to delete (required)
- `BACKUP`: Whether to backup before deletion (default: true)
- `RESTORE_AFTER`: Seconds to wait before restoring (0 = manual, default: 0)
- `NAMESPACE`: Target namespace (default: self-healing-cloud)

**What it tests:**
- Service failure detection
- DNS resolution failures
- Connection error handling
- Service recreation capabilities

## Prerequisites

### Required Tools

- `kubectl` configured to access your cluster
- `bash` shell
- Kubernetes cluster (Minikube, Kind, or cloud cluster)

### Optional Tools

- **Chaos Mesh**: For advanced network chaos engineering
  ```bash
  # Install Chaos Mesh
  curl -sSL https://mirrors.chaos-mesh.org/latest/install.sh | bash
  ```

- **Stress Tools**: For CPU/memory stress testing
  - Included in scripts via container images
  - Or install on nodes: `apt-get install stress-ng`

## Environment Variables

All scripts support the following environment variables:

- `NAMESPACE`: Kubernetes namespace (default: `self-healing-cloud`)
- `DEPLOYMENT`: Target deployment name
- `SERVICE`: Target service name
- `DURATION`: Duration in seconds for temporary failures
- `BACKUP`: Whether to create backups before destructive operations

## Safety Features

1. **Confirmation Prompts**: Destructive operations require confirmation
2. **Backups**: Services are backed up before deletion
3. **Namespace Isolation**: All operations are scoped to a namespace
4. **Timeout Protection**: Long-running operations have timeouts
5. **Cleanup**: Temporary resources are automatically cleaned up

## Integration with Self-Healing Agent

These scripts are designed to trigger the Self-Healing Agent:

1. **Run a failure injection script**
2. **Agent detects the failure** (via monitoring/metrics)
3. **Agent analyzes the issue** (using AI/ML)
4. **Agent takes remediation action** (scaling, restarting, etc.)
5. **Agent verifies resolution** (health checks)

## Example Workflow

```bash
# 1. Start Minikube cluster
cd ../../
./start_minikube.sh

# 2. Deploy services
kubectl apply -f namespace.yaml
kubectl apply -f deployments/

# 3. Inject failure
cd failure-injection
./kill_random_pod.sh compute-service

# 4. Monitor Self-Healing Agent response
kubectl get pods -n self-healing-cloud -w
kubectl logs -f -l app=self-healing-agent -n self-healing-cloud

# 5. Verify recovery
kubectl get pods -n self-healing-cloud
kubectl get hpa -n self-healing-cloud
```

## Monitoring

After running failure injection scripts, monitor:

```bash
# Pod status
kubectl get pods -n self-healing-cloud -w

# Service status
kubectl get svc -n self-healing-cloud

# HPA status
kubectl get hpa -n self-healing-cloud

# Resource usage
kubectl top pods -n self-healing-cloud
kubectl top nodes

# Events
kubectl get events -n self-healing-cloud --sort-by='.lastTimestamp'

# Agent logs
kubectl logs -f -l app=self-healing-agent -n self-healing-cloud
```

## Cleanup

To clean up resources created by failure injection scripts:

```bash
# Remove stress pods
kubectl delete pods -l app=cpu-stress -n self-healing-cloud
kubectl delete pods -l app=network-latency-injector -n self-healing-cloud

# Remove Chaos Mesh resources
kubectl delete networkchaos -n self-healing-cloud --all

# Remove network policies
kubectl delete networkpolicies -n self-healing-cloud --all
```

## Best Practices

1. **Start Small**: Begin with single pod failures before testing larger disruptions
2. **Monitor First**: Ensure monitoring is working before injecting failures
3. **Test Incrementally**: Test one failure type at a time
4. **Document Results**: Record agent response times and success rates
5. **Automate Testing**: Integrate these scripts into CI/CD pipelines
6. **Use Namespaces**: Isolate test environments from production

## Troubleshooting

### Scripts fail with "command not found"
- Ensure scripts are executable: `chmod +x *.sh`
- Check that `kubectl` is in PATH

### Pods not being killed
- Verify namespace and deployment names
- Check RBAC permissions
- Ensure pods exist: `kubectl get pods -n <namespace>`

### CPU overload not working
- Check if stress container image is available
- Verify resource limits on pods
- Check HPA is configured correctly

### Network latency not working
- Install Chaos Mesh for proper latency injection
- Check network policies aren't blocking traffic
- Verify iptables/tc tools are available

### Service deletion causes permanent loss
- Always use `BACKUP=true` (default)
- Restore from backup: `kubectl apply -f /tmp/<service>-backup-*.yaml`
- Recreate service manually if backup fails

## Related Documentation

- [Minikube Setup](../README.md)
- [Self-Healing Agent](../../agents/self-healing/README.md)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

