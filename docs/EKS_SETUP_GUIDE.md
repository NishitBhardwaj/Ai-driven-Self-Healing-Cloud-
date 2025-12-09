# EKS Setup and Troubleshooting Guide

## 🔴 Current Issues

### Issue 1: EKS Cluster Name Secret is Incorrect

**Error**: `cluster/Your EKS cluster name (e.g., )`

**Problem**: The `EKS_CLUSTER_NAME` secret contains placeholder text instead of your actual cluster name.

**Solution**: 
1. Go to GitHub Secrets: `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions`
2. Find `EKS_CLUSTER_NAME` secret
3. Click **Update** (pencil icon)
4. Replace the value with your **actual EKS cluster name** (e.g., `ai-cloud-cluster`, `my-eks-cluster`, etc.)
5. Click **Update secret**

**How to find your EKS cluster name:**
```bash
aws eks list-clusters --region us-east-1
```

### Issue 2: IAM User Lacks EKS Permissions

**Error**: `AccessDeniedException: User is not authorized to perform: eks:DescribeCluster`

**Problem**: The IAM user `Nishit_self_ai` doesn't have permission to access EKS clusters.

**Solution**: Grant EKS permissions to your IAM user.

## 🔧 Step-by-Step: Fix IAM Permissions

### Option 1: Using AWS Console (Easiest)

1. **Go to AWS IAM Console**
   - Navigate to: https://console.aws.amazon.com/iam/
   - Click **Users** → Find `Nishit_self_ai`

2. **Attach EKS Policy**
   - Click on the user `Nishit_self_ai`
   - Click **Add permissions** → **Attach policies directly**
   - Search for and select: **AmazonEKSClusterPolicy**
   - Click **Next** → **Add permissions**

3. **Verify Permissions**
   - The user should now have EKS access

### Option 2: Using AWS CLI

```bash
# Attach the managed EKS policy
aws iam attach-user-policy \
  --user-name Nishit_self_ai \
  --policy-arn arn:aws:iam::aws:policy/AmazonEKSClusterPolicy
```

### Option 3: Create Custom Policy (More Secure)

If you want to limit permissions to specific clusters:

1. **Create Custom Policy**
   - Go to IAM → **Policies** → **Create policy**
   - Click **JSON** tab
   - Paste this policy (replace `YOUR_CLUSTER_NAME`):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "eks:DescribeCluster",
        "eks:ListClusters",
        "eks:AccessKubernetesApi"
      ],
      "Resource": [
        "arn:aws:eks:*:365341398047:cluster/*"
      ]
    }
  ]
}
```

2. **Attach to User**
   - Name the policy (e.g., `EKS-Access-Policy`)
   - Click **Create policy**
   - Go to **Users** → `Nishit_self_ai` → **Add permissions** → **Attach policies directly**
   - Search for your new policy and attach it

## 📋 Complete Setup Checklist

### Step 1: Fix EKS Cluster Name Secret

- [ ] Go to GitHub Secrets
- [ ] Update `EKS_CLUSTER_NAME` with actual cluster name
- [ ] Verify no placeholder text remains

### Step 2: Grant IAM Permissions

- [ ] Go to AWS IAM Console
- [ ] Find user `Nishit_self_ai`
- [ ] Attach `AmazonEKSClusterPolicy` (or custom policy)
- [ ] Verify permissions are attached

### Step 3: Verify EKS Cluster Exists

```bash
# List all EKS clusters in your region
aws eks list-clusters --region us-east-1

# Describe your specific cluster (replace with actual name)
aws eks describe-cluster --name YOUR_CLUSTER_NAME --region us-east-1
```

### Step 4: Test Access

```bash
# Test if you can access the cluster
aws eks update-kubeconfig --name YOUR_CLUSTER_NAME --region us-east-1

# Verify kubectl access
kubectl get nodes
```

## 🚨 If You Don't Have an EKS Cluster Yet

If you don't have an EKS cluster, you need to create one first:

### Option A: Create EKS Cluster via AWS Console

1. Go to: https://console.aws.amazon.com/eks/
2. Click **Create cluster**
3. Configure:
   - **Name**: `ai-cloud-cluster` (or your preferred name)
   - **Kubernetes version**: Latest
   - **Cluster service role**: Create new or use existing
   - **VPC**: Select your VPC
   - **Subnets**: Select subnets
4. Click **Create**

### Option B: Create EKS Cluster via Terraform

We have Terraform configurations in `infrastructure/terraform/aws/` that can create an EKS cluster.

See: `infrastructure/terraform/aws/README.md`

### Option C: Use Existing Kubernetes Cluster

If you have a Kubernetes cluster (not EKS), you'll need to:
1. Update the workflow to use `kubeconfig` secret instead
2. Or modify the workflow to work with your cluster type

## 🔍 Troubleshooting Commands

### Check Current Secrets
```bash
# List all GitHub secrets (requires GitHub CLI)
gh secret list
```

### Test AWS Credentials
```bash
# Test if credentials work
aws sts get-caller-identity

# Should return your user ARN:
# arn:aws:iam::365341398047:user/Nishit_self_ai
```

### Test EKS Access
```bash
# List clusters (tests basic EKS access)
aws eks list-clusters --region us-east-1

# Describe cluster (tests DescribeCluster permission)
aws eks describe-cluster --name YOUR_CLUSTER_NAME --region us-east-1
```

### Check IAM Permissions
```bash
# Check attached policies
aws iam list-attached-user-policies --user-name Nishit_self_ai

# Check inline policies
aws iam list-user-policies --user-name Nishit_self_ai
```

## 📝 Quick Fix Summary

**To fix immediately:**

1. **Update GitHub Secret**:
   - Name: `EKS_CLUSTER_NAME`
   - Value: Your actual cluster name (e.g., `ai-cloud-cluster`)

2. **Grant IAM Permission**:
   - Go to IAM → Users → `Nishit_self_ai`
   - Attach policy: `AmazonEKSClusterPolicy`

3. **Re-run the pipeline**

## ⚠️ Important Notes

- The cluster name must match **exactly** (case-sensitive)
- IAM permission changes may take a few minutes to propagate
- If the cluster doesn't exist, create it first
- Make sure the cluster is in the same region as `AWS_REGION` secret

## 🆘 Still Having Issues?

If problems persist:

1. **Verify cluster exists**:
   ```bash
   aws eks list-clusters --region us-east-1
   ```

2. **Check IAM permissions**:
   ```bash
   aws iam list-attached-user-policies --user-name Nishit_self_ai
   ```

3. **Test manually**:
   ```bash
   # ⚠️ IMPORTANT: Use your actual credentials from GitHub Secrets or AWS IAM
   # NEVER commit actual credentials to code or documentation!
   export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY_ID"
   export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_ACCESS_KEY"
   export AWS_DEFAULT_REGION="us-east-1"
   aws eks update-kubeconfig --name YOUR_CLUSTER_NAME --region us-east-1
   ```

