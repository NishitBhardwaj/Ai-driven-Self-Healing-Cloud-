# Quick Start: AWS Region Configuration

## 🚀 Quick Setup (2 Minutes)

### Step 1: Set AWS Region in GitHub Secrets

1. Go to: `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions`
2. Click **New repository secret** (or update existing)
3. Add:
   - **Name**: `AWS_REGION`
   - **Value**: Choose one:
     - `ap-south-1` (Asia Pacific Mumbai) 🇮🇳
     - `ca-central-1` (Canada Central) 🇨🇦
     - `us-east-1` (US East - Default)
     - `us-west-2` (US West)
     - `eu-west-1` (Europe Ireland)
     - `eu-central-1` (Europe Frankfurt)
4. Click **Add secret**

### Step 2: Verify Your EKS Cluster

Make sure your EKS cluster exists in the selected region:

```bash
# For ap-south-1 (Mumbai)
aws eks list-clusters --region ap-south-1

# For ca-central-1 (Canada)
aws eks list-clusters --region ca-central-1
```

### Step 3: Deploy!

Push your code or manually trigger the pipeline. The pipeline will automatically use the region from GitHub Secrets.

## 📋 Required Secrets

Make sure these secrets are set in GitHub:

- ✅ `AWS_ACCESS_KEY_ID`
- ✅ `AWS_SECRET_ACCESS_KEY`
- ✅ `AWS_REGION` (e.g., `ap-south-1` or `ca-central-1`)
- ✅ `EKS_CLUSTER_NAME` (your actual cluster name)

## 🎯 Manual Region Selection

You can also override the region when manually triggering:

1. Go to **Actions** → **CD Pipeline**
2. Click **Run workflow**
3. Select:
   - **Environment**: `staging` or `production`
   - **AWS Region**: Choose from dropdown
4. Click **Run workflow**

## ✅ Verification

After deployment, check the pipeline logs for:

```
✅ Using AWS Region: ap-south-1
Configuring kubectl for EKS cluster: YOUR_CLUSTER_NAME
AWS Region: ap-south-1
```

## 🔧 Common Regions

| Region Code | Location | Use Case |
|------------|----------|----------|
| `ap-south-1` | Mumbai, India | India & South Asia |
| `ca-central-1` | Canada | Canada & North America |
| `us-east-1` | Virginia, USA | Default, US East Coast |
| `us-west-2` | Oregon, USA | US West Coast |
| `eu-west-1` | Ireland | Europe |
| `eu-central-1` | Frankfurt | Central Europe |

## 🆘 Troubleshooting

### "Cluster not found in region"
- Verify cluster exists: `aws eks list-clusters --region YOUR_REGION`
- Check `EKS_CLUSTER_NAME` secret matches actual cluster name

### "AWS_REGION not set"
- Add `AWS_REGION` secret in GitHub Settings → Secrets
- Or select region in workflow_dispatch

### Need more help?
See: `docs/AWS_REGION_CONFIGURATION.md` for detailed guide.

