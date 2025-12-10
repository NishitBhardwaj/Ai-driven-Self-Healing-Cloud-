# CD Pipeline Fixes

## Issue Fixed

**Error**: "Input required and not supplied: aws-region"

## Solution

### 1. Added Default AWS Region
- Added `AWS_REGION` environment variable with default fallback: `${{ secrets.AWS_REGION || 'us-east-1' }}`
- This ensures the pipeline works even if the secret is not set

### 2. Updated Both Jobs
- **Deploy Job**: Now uses `env.AWS_REGION` instead of `secrets.AWS_REGION` directly
- **Rollback Job**: Added `AWS_REGION` environment variable with same fallback

### 3. Improved Rollback Job
- Added checkout step (was missing)
- Added Helm setup (was missing)
- Fixed Helm rollback command syntax
- Made Slack notification optional

## Changes Made

### Environment Variables
```yaml
env:
  AWS_REGION: ${{ secrets.AWS_REGION || 'us-east-1' }}
```

### Deploy Job
- Uses `env.AWS_REGION` for AWS credentials configuration
- Uses `env.AWS_REGION` for EKS kubeconfig

### Rollback Job
- Added environment variables
- Added missing setup steps
- Fixed Helm rollback command
- Made Slack notification optional

## Required GitHub Secrets

To use a custom AWS region, add these secrets in GitHub:

1. **AWS_ACCESS_KEY_ID** - AWS access key
2. **AWS_SECRET_ACCESS_KEY** - AWS secret key
3. **AWS_REGION** (optional) - AWS region (defaults to us-east-1)
4. **EKS_CLUSTER_NAME** - Name of your EKS cluster
5. **SLACK_WEBHOOK_URL** (optional) - Slack webhook for notifications

## Setting Up GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret:
   - Name: `AWS_ACCESS_KEY_ID`
   - Value: Your AWS access key
5. Repeat for other secrets

## Testing the Fix

1. **Commit the changes**:
   ```bash
   git add .github/workflows/cd.yml
   git commit -m "Fix CD pipeline: Add AWS region with default fallback"
   git push origin main
   ```

2. **Monitor the pipeline**:
   - Go to GitHub Actions tab
   - Watch the "Deploy to Kubernetes" job
   - It should now have the AWS region configured

3. **Verify deployment**:
   - Check that the deployment succeeds
   - Verify services are running in Kubernetes

## Default Region

If `AWS_REGION` secret is not set, the pipeline will use **ap-south-1** (Mumbai) as the default region.

To change the default, modify line 23 in `.github/workflows/cd.yml`:
```yaml
AWS_REGION: ${{ secrets.AWS_REGION || 'ap-south-1' }}
```

## Troubleshooting

### Still Getting "aws-region" Error?
- Verify the environment variable is set correctly
- Check that the syntax `${{ env.AWS_REGION }}` is used (not `${{ secrets.AWS_REGION }}`)

### Deployment Fails?
- Check AWS credentials are valid
- Verify EKS cluster name is correct
- Ensure IAM permissions are sufficient

### Rollback Not Working?
- Check that Helm release exists
- Verify namespace is correct
- Check Helm rollback command syntax

