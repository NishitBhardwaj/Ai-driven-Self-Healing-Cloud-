# AWS Infrastructure as Code with Terraform

This directory contains Terraform configurations for deploying the AI-Driven Self-Healing Cloud infrastructure on AWS.

## Overview

The Terraform configuration provisions:
- **VPC** with public and private subnets across multiple availability zones
- **EC2 Auto Scaling Group** for agent instances
- **Application Load Balancer** for high availability
- **RDS PostgreSQL** database with optional read replica
- **S3 buckets** for logs, data, and Terraform state
- **IAM roles and policies** for secure access
- **Security groups** for network security
- **CloudWatch alarms** for auto-scaling

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **Terraform** >= 1.0 installed
3. **AWS CLI** configured with credentials
4. **SSH Key Pair** created in AWS

## Setup

### 1. Configure AWS Credentials

```bash
aws configure
```

Or set environment variables:
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

### 2. Create SSH Key Pair

```bash
aws ec2 create-key-pair --key-name my-key-pair --query 'KeyMaterial' --output text > my-key-pair.pem
chmod 400 my-key-pair.pem
```

### 3. Configure Variables

Copy the example variables file and customize:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your values:
- AWS region
- Key pair name
- Database password
- SSL certificate ARN (if using HTTPS)
- Instance types and scaling parameters

### 4. Initialize Terraform

```bash
terraform init
```

### 5. Review Plan

```bash
terraform plan
```

### 6. Apply Configuration

```bash
terraform apply
```

Type `yes` when prompted to create the resources.

## Infrastructure Components

### VPC and Networking

- **VPC**: 10.0.0.0/16 CIDR block
- **Public Subnets**: 2 subnets across availability zones
- **Private Subnets**: 2 subnets across availability zones
- **Internet Gateway**: For public subnet internet access
- **NAT Gateways**: For private subnet internet access
- **Route Tables**: Separate routing for public and private subnets

### Compute

- **Auto Scaling Group**: Manages agent EC2 instances
- **Launch Template**: Defines instance configuration
- **CloudWatch Alarms**: Trigger auto-scaling based on CPU utilization
- **Security Groups**: Control network access

### Load Balancing

- **Application Load Balancer**: Distributes traffic across instances
- **Target Group**: Health checks and instance registration
- **Listeners**: HTTP (redirects to HTTPS) and HTTPS
- **SSL/TLS**: Certificate-based encryption

### Database

- **RDS PostgreSQL**: Managed database service
- **Multi-AZ**: High availability (optional)
- **Read Replica**: For read scaling (optional)
- **Automated Backups**: Daily backups with configurable retention
- **Encryption**: At-rest encryption enabled

### Storage

- **S3 Bucket (Logs)**: Centralized log storage
- **S3 Bucket (Data)**: Application data storage
- **S3 Bucket (Terraform State)**: State file storage
- **Versioning**: Enabled on all buckets
- **Encryption**: Server-side encryption enabled
- **Lifecycle Policies**: Automatic log cleanup

### Security

- **IAM Roles**: Least privilege access for instances
- **Security Groups**: Network-level firewall rules
- **S3 Public Access Block**: Prevents public access
- **Encryption**: At-rest and in-transit encryption

## Outputs

After applying, Terraform outputs:

- `vpc_id`: VPC ID
- `load_balancer_dns`: DNS name for the load balancer
- `rds_endpoint`: Database connection endpoint
- `s3_logs_bucket`: S3 bucket name for logs
- `s3_data_bucket`: S3 bucket name for data

## Accessing Resources

### Load Balancer

```bash
# Get load balancer DNS
terraform output load_balancer_dns

# Access application
curl http://$(terraform output -raw load_balancer_dns)/health
```

### Database

```bash
# Get database endpoint
terraform output rds_endpoint

# Connect to database
psql -h $(terraform output -raw rds_address) -U admin -d ai_cloud_db
```

### SSH to Instances

```bash
# Get instance IPs (from Auto Scaling Group)
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=ai-self-healing-cloud-agent" \
  --query 'Reservations[*].Instances[*].PublicIpAddress' \
  --output text

# SSH to instance
ssh -i my-key-pair.pem ec2-user@<instance-ip>
```

## Scaling

The Auto Scaling Group automatically scales based on CPU utilization:

- **Scale Up**: When CPU > 80% for 2 evaluation periods (10 minutes)
- **Scale Down**: When CPU < 20% for 2 evaluation periods (10 minutes)
- **Cooldown**: 5 minutes between scaling actions

Manual scaling:

```bash
aws autoscaling set-desired-capacity \
  --auto-scaling-group-name $(terraform output -raw autoscaling_group_name) \
  --desired-capacity 5
```

## Monitoring

### CloudWatch Metrics

- CPU utilization
- Network in/out
- Disk I/O
- Application metrics (custom)

### CloudWatch Logs

- Application logs
- System logs
- Access logs

View logs:

```bash
aws logs tail /aws/ec2/ai-cloud --follow
```

## Cost Optimization

1. **Use Reserved Instances**: For predictable workloads
2. **Spot Instances**: For non-critical workloads
3. **Right-size Instances**: Monitor and adjust instance types
4. **S3 Lifecycle Policies**: Automatically archive old logs
5. **RDS Reserved Instances**: For database cost savings

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

**Warning**: This will delete all resources including databases. Make sure to backup data first.

## Troubleshooting

### Terraform State Lock

If Terraform is stuck:

```bash
# Check for locks
aws dynamodb list-tables

# Force unlock (if needed)
terraform force-unlock <lock-id>
```

### Instance Not Joining Load Balancer

1. Check security group allows traffic from ALB
2. Verify health check path is correct
3. Check instance logs: `ssh ec2-user@<ip> 'sudo tail -f /var/log/cloud-init-output.log'`

### Database Connection Issues

1. Verify security group allows traffic from agent instances
2. Check database is in private subnet
3. Verify credentials in application configuration

## Next Steps

1. **Deploy Application**: Use CI/CD pipeline to deploy application code
2. **Configure Monitoring**: Set up CloudWatch dashboards and alarms
3. **Set Up CI/CD**: Configure GitHub Actions or GitLab CI
4. **Enable HTTPS**: Configure SSL certificate and update listeners
5. **Backup Strategy**: Configure automated backups and disaster recovery

## Security Best Practices

1. **Restrict SSH Access**: Update `allowed_ssh_cidr` to your IP
2. **Use Secrets Manager**: Store database passwords in AWS Secrets Manager
3. **Enable MFA**: Require MFA for AWS console access
4. **Regular Updates**: Keep AMIs and instances updated
5. **Audit Logs**: Enable CloudTrail for API auditing
6. **Network Segmentation**: Use private subnets for sensitive resources
7. **Encryption**: Enable encryption at rest and in transit

## Support

For issues or questions:
- Check Terraform documentation: https://www.terraform.io/docs
- AWS documentation: https://docs.aws.amazon.com
- Project repository: [Your repo URL]

