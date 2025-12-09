# AWS CloudFormation Templates

This directory contains CloudFormation templates for deploying the AI-Driven Self-Healing Cloud infrastructure on AWS.

## Overview

CloudFormation templates provide an alternative to Terraform for infrastructure provisioning. These templates are organized into separate stacks for modularity.

## Templates

### 1. VPC Stack (`vpc.yaml`)

Creates the networking foundation:
- VPC with DNS support
- Public and private subnets (2 each)
- Internet Gateway
- NAT Gateways (one per AZ)
- Route tables and associations

**Deploy:**
```bash
aws cloudformation create-stack \
  --stack-name ai-cloud-vpc \
  --template-body file://vpc.yaml \
  --parameters ParameterKey=ProjectName,ParameterValue=ai-self-healing-cloud \
               ParameterKey=Environment,ParameterValue=production
```

### 2. Additional Stacks (To be created)

- **compute.yaml**: EC2 instances, Auto Scaling Groups
- **load-balancer.yaml**: Application Load Balancer
- **database.yaml**: RDS instances
- **storage.yaml**: S3 buckets
- **security.yaml**: IAM roles and security groups

## Prerequisites

1. AWS CLI configured
2. Appropriate IAM permissions
3. AWS account with sufficient limits

## Deployment Order

1. **VPC Stack**: Networking foundation
2. **Security Stack**: IAM roles and security groups
3. **Storage Stack**: S3 buckets
4. **Database Stack**: RDS instances
5. **Compute Stack**: EC2 and Auto Scaling
6. **Load Balancer Stack**: ALB configuration

## Advantages of CloudFormation

- Native AWS integration
- Stack dependencies and rollback
- Change sets for preview
- Stack policies for protection
- Integration with AWS services

## Comparison: Terraform vs CloudFormation

| Feature | Terraform | CloudFormation |
|---------|-----------|----------------|
| Multi-cloud | ✅ Yes | ❌ AWS only |
| State Management | External | Native |
| Rollback | Manual | Automatic |
| Change Preview | Plan | Change Sets |
| Learning Curve | Moderate | Moderate |

## Next Steps

1. Complete remaining CloudFormation templates
2. Create deployment scripts
3. Set up stack dependencies
4. Configure stack policies

