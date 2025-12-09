# Infrastructure as Code - Complete Guide

This directory contains Terraform configurations for deploying the AI-Driven Self-Healing Cloud infrastructure on AWS, GCP, and Azure.

## Overview

Infrastructure as Code (IaC) allows you to manage and provision infrastructure through code, ensuring consistency, repeatability, and version control.

## Cloud Providers

### AWS

**Location**: `terraform/aws/`

**Components**:
- VPC with public/private subnets
- EC2 Auto Scaling Groups
- Application Load Balancer (ALB)
- Network Load Balancer (NLB)
- RDS PostgreSQL
- S3 buckets
- IAM roles and policies
- Enhanced auto-scaling
- CloudWatch alarms

**Quick Start**:
```bash
cd infrastructure/terraform/aws
terraform init
terraform plan
terraform apply
```

**Documentation**: See `terraform/aws/README.md`

### GCP

**Location**: `terraform/gcp/`

**Components**:
- VPC network
- Google Kubernetes Engine (GKE)
- Global Load Balancer
- Regional Load Balancer
- Cloud SQL (optional)
- Cloud Storage (optional)
- Node pools with auto-scaling

**Quick Start**:
```bash
cd infrastructure/terraform/gcp
terraform init
terraform plan
terraform apply
```

### Azure

**Location**: `terraform/azure/`

**Components**:
- Virtual Network
- Azure Kubernetes Service (AKS)
- Application Gateway
- Load Balancer
- Public IP addresses
- Resource groups

**Quick Start**:
```bash
cd infrastructure/terraform/azure
terraform init
terraform plan
terraform apply
```

## CloudFormation (AWS)

**Location**: `cloudformation/aws/`

**Templates**:
- `vpc.yaml`: VPC and networking
- `compute.yaml`: EC2 and Auto Scaling
- `load-balancer.yaml`: Application Load Balancer

**Deploy**:
```bash
aws cloudformation create-stack \
  --stack-name ai-cloud-vpc \
  --template-body file://vpc.yaml
```

## Auto-Scaling

### AWS Auto Scaling

**Features**:
- Target tracking (CPU, request count)
- Step scaling policies
- Predictive scaling
- Mixed instances (on-demand + spot)
- Instance refresh

**Configuration**: `terraform/aws/autoscaling-enhanced.tf`

### Kubernetes HPA

**Features**:
- CPU-based scaling
- Memory-based scaling
- Custom metrics
- Advanced scaling policies

**Configuration**: `kubernetes/autoscaling/hpa-advanced.yaml`

### Cluster Autoscaler

**Features**:
- Node group auto-discovery
- Scale-down optimization
- Spot instance support

**Configuration**: `kubernetes/autoscaling/cluster-autoscaler.yaml`

## Load Balancing

### AWS Load Balancers

**Application Load Balancer (ALB)**:
- HTTP/HTTPS
- Path-based routing
- SSL termination
- Access logs
- Sticky sessions

**Network Load Balancer (NLB)**:
- TCP/UDP
- High performance
- Low latency

**Configuration**: `terraform/aws/load-balancer-enhanced.tf`

### GCP Load Balancers

**Global Load Balancer**:
- HTTP/HTTPS
- Global anycast IP
- CDN integration

**Regional Load Balancer**:
- Internal load balancing
- TCP/UDP

**Configuration**: `terraform/gcp/load-balancer.tf`

### Azure Load Balancers

**Application Gateway**:
- HTTP/HTTPS
- SSL termination
- WAF integration

**Standard Load Balancer**:
- TCP/UDP
- High availability

**Configuration**: `terraform/azure/load-balancer.tf`

### Kubernetes Load Balancing

**Ingress**:
- NGINX Ingress Controller
- Path-based routing
- SSL/TLS

**LoadBalancer Services**:
- Cloud provider integration
- External access

**Configuration**: `kubernetes/load-balancing/`

## Best Practices

1. **Version Control**: Keep all IaC in version control
2. **State Management**: Use remote state backends
3. **Modularity**: Break down into reusable modules
4. **Documentation**: Document all configurations
5. **Testing**: Test in non-production first
6. **Security**: Follow least privilege principle
7. **Cost Optimization**: Use spot instances, right-sizing
8. **Monitoring**: Set up alerts and monitoring

## Comparison

| Feature | AWS | GCP | Azure |
|---------|-----|-----|-------|
| Load Balancer | ALB/NLB | Global LB | App Gateway |
| Auto Scaling | ASG | GKE Autoscaler | VMSS |
| Kubernetes | EKS | GKE | AKS |
| State Backend | S3 | GCS | Blob Storage |
| Cost | Medium | Low | Medium |

## Migration

### AWS to GCP

1. Export Terraform state
2. Update provider configuration
3. Map resources (ALB → Global LB, etc.)
4. Test in staging
5. Migrate production

### GCP to Azure

1. Export Terraform state
2. Update provider configuration
3. Map resources (GKE → AKS, etc.)
4. Test in staging
5. Migrate production

## Troubleshooting

### Terraform State Lock

```bash
# Check for locks
terraform force-unlock <lock-id>
```

### Provider Authentication

**AWS**:
```bash
aws configure
```

**GCP**:
```bash
gcloud auth application-default login
```

**Azure**:
```bash
az login
```

### Common Issues

1. **State Lock**: Use `force-unlock` carefully
2. **Provider Version**: Update provider versions
3. **Resource Conflicts**: Check for existing resources
4. **Permissions**: Verify IAM roles and permissions

## Next Steps

1. **Choose Provider**: Select AWS, GCP, or Azure
2. **Configure Variables**: Update `terraform.tfvars`
3. **Deploy Infrastructure**: Run `terraform apply`
4. **Configure Kubernetes**: Set up kubeconfig
5. **Deploy Application**: Use Helm charts

## Support

For issues:
- Check provider documentation
- Review Terraform logs
- Consult troubleshooting guides
- Contact DevOps team

