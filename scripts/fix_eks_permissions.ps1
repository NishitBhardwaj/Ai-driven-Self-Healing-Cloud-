# PowerShell script to fix EKS IAM permissions for the GitHub Actions user
# This script attaches the necessary EKS permissions to the IAM user

$ErrorActionPreference = "Stop"

$UserName = "Nishit_self_ai"
$PolicyArn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "EKS IAM Permissions Fix Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "This script will attach EKS permissions to IAM user: $UserName" -ForegroundColor Yellow
Write-Host ""

# Check if AWS CLI is installed
try {
    $null = Get-Command aws -ErrorAction Stop
} catch {
    Write-Host "❌ AWS CLI is not installed. Please install it first." -ForegroundColor Red
    Write-Host "   Visit: https://aws.amazon.com/cli/" -ForegroundColor Yellow
    exit 1
}

# Check if user exists
Write-Host "Checking if IAM user exists..." -ForegroundColor Yellow
try {
    $null = aws iam get-user --user-name $UserName 2>&1
    Write-Host "✅ IAM user found: $UserName" -ForegroundColor Green
} catch {
    Write-Host "❌ IAM user '$UserName' not found!" -ForegroundColor Red
    Write-Host "   Please verify the user name." -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Check if policy is already attached
Write-Host "Checking current permissions..." -ForegroundColor Yellow
$AttachedPolicies = aws iam list-attached-user-policies --user-name $UserName --query 'AttachedPolicies[].PolicyArn' --output text

if ($AttachedPolicies -match [regex]::Escape($PolicyArn)) {
    Write-Host "✅ Policy is already attached!" -ForegroundColor Green
    Write-Host "   Policy ARN: $PolicyArn" -ForegroundColor Gray
    exit 0
}

Write-Host "Policy not attached. Attaching now..." -ForegroundColor Yellow
Write-Host ""

# Attach the policy
Write-Host "Attaching policy: $PolicyArn" -ForegroundColor Yellow
try {
    aws iam attach-user-policy --user-name $UserName --policy-arn $PolicyArn
    Write-Host ""
    Write-Host "✅ Successfully attached EKS policy!" -ForegroundColor Green
    Write-Host ""
    Write-Host "The user '$UserName' now has EKS permissions." -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Wait 1-2 minutes for permissions to propagate" -ForegroundColor White
    Write-Host "2. Update GitHub secret 'EKS_CLUSTER_NAME' with your actual cluster name" -ForegroundColor White
    Write-Host "3. Re-run the GitHub Actions pipeline" -ForegroundColor White
} catch {
    Write-Host ""
    Write-Host "❌ Failed to attach policy!" -ForegroundColor Red
    Write-Host "   Please check your AWS credentials and permissions." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Verification" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Listing attached policies:" -ForegroundColor Yellow
aws iam list-attached-user-policies --user-name $UserName --output table

Write-Host ""
Write-Host "✅ Done!" -ForegroundColor Green

