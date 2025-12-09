# Kubernetes RBAC Configuration

This directory contains Role-Based Access Control (RBAC) configurations for securing the Kubernetes deployment.

## Overview

RBAC ensures that:
- **Principle of Least Privilege**: Services only have permissions they need
- **Security**: Prevents unauthorized access to cluster resources
- **Auditability**: All actions are logged and traceable
- **Compliance**: Meets security and compliance requirements

## Components

### 1. Namespaces

**File**: `namespace.yaml`

Creates separate namespaces for different environments:
- `ai-cloud-production`: Production environment
- `ai-cloud-staging`: Staging environment
- `ai-cloud-development`: Development environment

**Apply**:
```bash
kubectl apply -f kubernetes/rbac/namespace.yaml
```

### 2. Service Accounts

**File**: `serviceaccount.yaml`

Creates service accounts for different components:
- `ai-cloud-agents`: For agent pods
- `ai-cloud-monitoring`: For monitoring tools
- `ai-cloud-cicd`: For CI/CD pipelines

**Apply**:
```bash
kubectl apply -f kubernetes/rbac/serviceaccount.yaml
```

### 3. Roles

**File**: `role.yaml`

Defines namespace-scoped permissions:
- **ai-cloud-agents-role**: Limited permissions for agents
  - Read ConfigMaps and Secrets
  - Read pod/service information
  - Create events
- **ai-cloud-monitoring-role**: Read-only access for monitoring
  - Read all resources
  - Read metrics
- **ai-cloud-cicd-role**: Deployment permissions for CI/CD
  - Manage deployments and services
  - Manage ConfigMaps and Secrets
  - Read pod status

**Apply**:
```bash
kubectl apply -f kubernetes/rbac/role.yaml
```

### 4. Role Bindings

**File**: `rolebinding.yaml`

Binds service accounts to roles within the namespace.

**Apply**:
```bash
kubectl apply -f kubernetes/rbac/rolebinding.yaml
```

### 5. Cluster Roles

**File**: `clusterrole.yaml`

Defines cluster-scoped permissions:
- **ai-cloud-cluster-monitoring**: Cluster-wide monitoring
  - Read nodes
  - Read namespaces
  - Read cluster metrics
- **ai-cloud-admin**: Full cluster access (use with caution)

**Apply**:
```bash
kubectl apply -f kubernetes/rbac/clusterrole.yaml
```

### 6. Cluster Role Bindings

**File**: `clusterrolebinding.yaml`

Binds service accounts to cluster roles.

**Apply**:
```bash
kubectl apply -f kubernetes/rbac/clusterrolebinding.yaml
```

## Usage

### Apply All RBAC Configurations

```bash
# Apply in order
kubectl apply -f kubernetes/rbac/namespace.yaml
kubectl apply -f kubernetes/rbac/serviceaccount.yaml
kubectl apply -f kubernetes/rbac/role.yaml
kubectl apply -f kubernetes/rbac/rolebinding.yaml
kubectl apply -f kubernetes/rbac/clusterrole.yaml
kubectl apply -f kubernetes/rbac/clusterrolebinding.yaml
```

### Verify RBAC

**Check Service Accounts**:
```bash
kubectl get serviceaccounts -n ai-cloud-production
```

**Check Roles**:
```bash
kubectl get roles -n ai-cloud-production
kubectl describe role ai-cloud-agents-role -n ai-cloud-production
```

**Check Role Bindings**:
```bash
kubectl get rolebindings -n ai-cloud-production
kubectl describe rolebinding ai-cloud-agents-binding -n ai-cloud-production
```

**Test Permissions**:
```bash
# Test as agent service account
kubectl auth can-i get pods \
  --as=system:serviceaccount:ai-cloud-production:ai-cloud-agents \
  -n ai-cloud-production

# Test as monitoring service account
kubectl auth can-i get nodes \
  --as=system:serviceaccount:ai-cloud-production:ai-cloud-monitoring
```

## Integration with Deployments

Update your Helm chart or deployment to use service accounts:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-cloud-self-healing
spec:
  template:
    spec:
      serviceAccountName: ai-cloud-agents
      containers:
      - name: self-healing
        image: ai-cloud/self-healing:latest
```

## Security Best Practices

1. **Principle of Least Privilege**: Grant minimum required permissions
2. **Namespace Isolation**: Use namespaces to separate environments
3. **Service Accounts**: Use dedicated service accounts for each component
4. **Regular Audits**: Review and audit RBAC configurations regularly
5. **Avoid Cluster Admin**: Don't use cluster-admin unless absolutely necessary
6. **Rotate Credentials**: Regularly rotate service account tokens
7. **Monitor Access**: Monitor and log all RBAC-related activities

## Troubleshooting

### Permission Denied

**Check Service Account**:
```bash
kubectl get pod <pod-name> -n ai-cloud-production -o jsonpath='{.spec.serviceAccountName}'
```

**Check Role Binding**:
```bash
kubectl get rolebinding -n ai-cloud-production
```

**Test Permissions**:
```bash
kubectl auth can-i <verb> <resource> \
  --as=system:serviceaccount:<namespace>:<service-account> \
  -n <namespace>
```

### Service Account Not Found

**Create Service Account**:
```bash
kubectl apply -f kubernetes/rbac/serviceaccount.yaml
```

**Verify**:
```bash
kubectl get serviceaccount -n ai-cloud-production
```

## Next Steps

1. **Apply RBAC**: Apply all RBAC configurations
2. **Update Deployments**: Update deployments to use service accounts
3. **Test Permissions**: Verify permissions work correctly
4. **Monitor**: Set up monitoring for RBAC violations
5. **Audit**: Regularly audit RBAC configurations

