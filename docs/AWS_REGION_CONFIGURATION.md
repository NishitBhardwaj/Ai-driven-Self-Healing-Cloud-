# AWS Region Configuration Guide

## Overview

This guide explains how to configure and use different AWS regions in the CI/CD pipeline. The pipeline supports multiple AWS regions including:

- **us-east-1** (US East - N. Virginia) - Default
- **us-west-2** (US West - Oregon)
- **ap-south-1** (Asia Pacific - Mumbai) 🇮🇳
- **ca-central-1** (Canada - Central) 🇨🇦
- **eu-west-1** (Europe - Ireland)
- **eu-central-1** (Europe - Frankfurt)

## Configuration Methods

### Method 1: GitHub Secrets (Recommended)

Set the AWS region as a GitHub Secret for automatic use:

1. Go to: `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions`
2. Click **New repository secret**
3. Add:
   - **Name**: `AWS_REGION`
   - **Value**: Your preferred region (e.g., `ap-south-1` or `ca-central-1`)
4. Click **Add secret**

**Priority**: This is the default method and will be used unless overridden by workflow_dispatch.

### Method 2: Workflow Dispatch Input (Manual Override)

When manually triggering the pipeline, you can override the region:

1. Go to **Actions** tab in GitHub
2. Select **CD Pipeline** workflow
3. Click **Run workflow**
4. Select:
   - **Environment**: `staging` or `production`
   - **AWS Region**: Choose from dropdown (or leave empty to use secret)
5. Click **Run workflow**

**Priority**: Workflow dispatch input overrides GitHub Secrets.

### Method 3: Default Fallback

If neither secret nor input is provided, the pipeline defaults to `us-east-1`.

## Region Selection Priority

The pipeline uses the following priority order:

1. **Workflow Dispatch Input** (if provided)
2. **GitHub Secret** (`AWS_REGION`)
3. **Default** (`us-east-1`)

## Setting Up Multiple Regions

### Scenario 1: Single Region (Most Common)

If you only use one region (e.g., `ap-south-1`):

1. Set `AWS_REGION` secret to `ap-south-1`
2. Ensure your EKS cluster is in `ap-south-1`
3. All deployments will use this region

### Scenario 2: Multiple Regions (Staging & Production)

If you use different regions for staging and production:

#### Option A: Environment-Specific Secrets

Use GitHub Environments with different secrets:

1. Go to **Settings** → **Environments**
2. Create `staging` environment
   - Add secret: `AWS_REGION` = `ap-south-1`
3. Create `production` environment
   - Add secret: `AWS_REGION` = `ca-central-1`

#### Option B: Workflow Dispatch

Manually select the region when triggering:
- Staging deployments: Select `ap-south-1`
- Production deployments: Select `ca-central-1`

## Region-Specific Configuration

### Asia Pacific Mumbai (ap-south-1)

**Use Cases**:
- Serving users in India and South Asia
- Lower latency for Indian users
- Compliance with data residency requirements

**Setup**:
```bash
# Set in GitHub Secrets
AWS_REGION=ap-south-1

# Verify EKS cluster exists
aws eks list-clusters --region ap-south-1
```

### Canada Central (ca-central-1)

**Use Cases**:
- Serving users in Canada
- Compliance with Canadian data residency laws
- Lower latency for Canadian users

**Setup**:
```bash
# Set in GitHub Secrets
AWS_REGION=ca-central-1

# Verify EKS cluster exists
aws eks list-clusters --region ca-central-1
```

## Verification Steps

### 1. Verify Region Configuration

Check that the region is set correctly in the pipeline:

```yaml
# In workflow logs, you should see:
✅ Using AWS Region: ap-south-1
```

### 2. Verify EKS Cluster in Region

```bash
# List clusters in your region
aws eks list-clusters --region ap-south-1

# Describe your cluster
aws eks describe-cluster \
  --name YOUR_CLUSTER_NAME \
  --region ap-south-1
```

### 3. Verify kubectl Configuration

After deployment, verify kubectl is configured for the correct region:

```bash
kubectl config current-context
# Should show: arn:aws:eks:ap-south-1:ACCOUNT:cluster/CLUSTER_NAME
```

## Common Issues and Solutions

### Issue 1: "Cluster not found in region"

**Problem**: EKS cluster doesn't exist in the specified region.

**Solution**:
1. Verify cluster exists: `aws eks list-clusters --region YOUR_REGION`
2. Create cluster in the region if it doesn't exist
3. Update `EKS_CLUSTER_NAME` secret if cluster name differs

### Issue 2: "AccessDeniedException" in different region

**Problem**: IAM user doesn't have permissions in the new region.

**Solution**:
1. EKS permissions are global, but verify IAM user has access
2. Check IAM policies: `aws iam list-attached-user-policies --user-name YOUR_USER`
3. Ensure `AmazonEKSClusterPolicy` is attached

### Issue 3: Region mismatch between services

**Problem**: EKS cluster in one region, but S3/RDS in another.

**Solution**:
- Ensure all AWS services are in the same region for best performance
- Or configure cross-region access (more complex)

## Best Practices

1. **Use GitHub Secrets** for default region configuration
2. **Use Workflow Dispatch** for temporary region changes
3. **Keep services in the same region** for better performance
4. **Document region choices** in your infrastructure docs
5. **Test deployments** in staging before production
6. **Monitor costs** - some regions are more expensive than others

## Cost Considerations

Different regions have different pricing:

- **us-east-1**: Generally cheapest
- **ap-south-1**: Competitive pricing for Asia
- **ca-central-1**: Slightly higher than US regions
- **eu-west-1**: Competitive for Europe

Check AWS pricing calculator: https://calculator.aws/

## Security Considerations

1. **Data Residency**: Some regions required for compliance
2. **Cross-Region Access**: Minimize cross-region data transfer
3. **IAM Permissions**: Ensure consistent permissions across regions
4. **Encryption**: Enable encryption at rest in all regions

## Example Configurations

### Example 1: India-Based Deployment

```yaml
# GitHub Secret
AWS_REGION=ap-south-1

# EKS Cluster
EKS_CLUSTER_NAME=ai-cloud-mumbai-cluster

# All services in ap-south-1
```

### Example 2: Canada-Based Deployment

```yaml
# GitHub Secret
AWS_REGION=ca-central-1

# EKS Cluster
EKS_CLUSTER_NAME=ai-cloud-canada-cluster

# All services in ca-central-1
```

### Example 3: Multi-Region Setup

```yaml
# Staging Environment
AWS_REGION=ap-south-1
EKS_CLUSTER_NAME=ai-cloud-staging

# Production Environment
AWS_REGION=ca-central-1
EKS_CLUSTER_NAME=ai-cloud-production
```

## Troubleshooting

### Check Current Region

```bash
# In pipeline logs, look for:
echo "✅ Using AWS Region: ${{ env.AWS_REGION }}"
```

### Verify Region in AWS CLI

```bash
aws configure get region
```

### Test Region Access

```bash
# Test EKS access in region
aws eks list-clusters --region ap-south-1

# Test S3 access in region
aws s3 ls --region ap-south-1
```

## Additional Resources

- [AWS Regions and Endpoints](https://docs.aws.amazon.com/general/latest/gr/rande.html)
- [EKS Regions](https://docs.aws.amazon.com/eks/latest/userguide/regions.html)
- [AWS Pricing by Region](https://aws.amazon.com/pricing/)

---

**Need Help?** See `docs/EKS_SETUP_GUIDE.md` for EKS-specific setup.

