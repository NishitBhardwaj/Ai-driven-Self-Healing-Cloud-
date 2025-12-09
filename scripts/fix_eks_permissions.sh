#!/bin/bash
# Script to fix EKS IAM permissions for the GitHub Actions user
# This script attaches the necessary EKS permissions to the IAM user

set -e

USER_NAME="Nishit_self_ai"
POLICY_ARN="arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"

echo "=========================================="
echo "EKS IAM Permissions Fix Script"
echo "=========================================="
echo ""
echo "This script will attach EKS permissions to IAM user: $USER_NAME"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    echo "   Visit: https://aws.amazon.com/cli/"
    exit 1
fi

# Check if user exists
echo "Checking if IAM user exists..."
if ! aws iam get-user --user-name "$USER_NAME" &> /dev/null; then
    echo "❌ IAM user '$USER_NAME' not found!"
    echo "   Please verify the user name."
    exit 1
fi

echo "✅ IAM user found: $USER_NAME"
echo ""

# Check if policy is already attached
echo "Checking current permissions..."
ATTACHED_POLICIES=$(aws iam list-attached-user-policies --user-name "$USER_NAME" --query 'AttachedPolicies[].PolicyArn' --output text)

if echo "$ATTACHED_POLICIES" | grep -q "$POLICY_ARN"; then
    echo "✅ Policy is already attached!"
    echo "   Policy ARN: $POLICY_ARN"
    exit 0
fi

echo "Policy not attached. Attaching now..."
echo ""

# Attach the policy
echo "Attaching policy: $POLICY_ARN"
if aws iam attach-user-policy --user-name "$USER_NAME" --policy-arn "$POLICY_ARN"; then
    echo ""
    echo "✅ Successfully attached EKS policy!"
    echo ""
    echo "The user '$USER_NAME' now has EKS permissions."
    echo ""
    echo "Next steps:"
    echo "1. Wait 1-2 minutes for permissions to propagate"
    echo "2. Update GitHub secret 'EKS_CLUSTER_NAME' with your actual cluster name"
    echo "3. Re-run the GitHub Actions pipeline"
else
    echo ""
    echo "❌ Failed to attach policy!"
    echo "   Please check your AWS credentials and permissions."
    exit 1
fi

echo ""
echo "=========================================="
echo "Verification"
echo "=========================================="
echo ""
echo "Listing attached policies:"
aws iam list-attached-user-policies --user-name "$USER_NAME" --output table

echo ""
echo "✅ Done!"

