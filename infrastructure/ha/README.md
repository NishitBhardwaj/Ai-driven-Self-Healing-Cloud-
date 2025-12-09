# High Availability and Failover Configuration

This directory contains configurations for high availability (HA) and failover across AWS, GCP, and Azure.

## Overview

High availability ensures that your system remains operational even when individual components fail. This is achieved through:

- **Multi-Availability Zone (AZ) Deployment**: Resources distributed across multiple availability zones
- **Automatic Failover**: Automatic switching to backup resources when primary fails
- **Load Balancing**: Traffic distributed across multiple instances
- **Database Replication**: Database copies in multiple zones for failover
- **Health Monitoring**: Continuous health checks and automatic recovery

## AWS High Availability

### Multi-AZ Architecture

**Components**:
- **EC2 Auto Scaling Group**: Spans multiple AZs automatically
- **RDS Multi-AZ**: Automatic failover to standby in different AZ
- **Application Load Balancer**: Cross-zone load balancing enabled
- **Route53 Health Checks**: DNS-level failover

**Configuration Files**:
- `terraform/aws/ha-config.tf`: HA-specific configurations
- `terraform/aws/rds.tf`: Multi-AZ RDS configuration
- `terraform/aws/ec2.tf`: Multi-AZ Auto Scaling Group
- `terraform/aws/load_balancer.tf`: Cross-zone load balancing

**Features**:
- ✅ Multi-AZ RDS with automatic failover
- ✅ Auto Scaling Group across multiple AZs
- ✅ Cross-zone load balancing
- ✅ Route53 health checks
- ✅ RDS event subscriptions for failover notifications
- ✅ SNS alerts for HA events

**Deploy**:
```bash
cd infrastructure/terraform/aws
terraform apply
```

### RDS Multi-AZ Failover

**How It Works**:
1. Primary database in one AZ
2. Standby replica in different AZ (synchronous replication)
3. Automatic failover in ~60-120 seconds
4. DNS automatically points to new primary

**Test Failover**:
```bash
# Force failover (for testing)
aws rds reboot-db-instance \
  --db-instance-identifier ai-self-healing-cloud-db \
  --force-failover

# Monitor failover
aws rds describe-db-instances \
  --db-instance-identifier ai-self-healing-cloud-db
```

## GCP High Availability

### Multi-Zone Architecture

**Components**:
- **GKE Regional Cluster**: Spans multiple zones
- **Cloud SQL Regional**: High availability with automatic failover
- **Global Load Balancer**: Multi-region load balancing
- **Cloud SQL Read Replicas**: For read scaling and failover

**Configuration Files**:
- `terraform/gcp/gke.tf`: Multi-zone GKE cluster
- `terraform/gcp/cloud-sql-ha.tf`: High availability Cloud SQL
- `terraform/gcp/load-balancer.tf`: Global load balancer

**Features**:
- ✅ Regional GKE cluster (multi-zone)
- ✅ Cloud SQL with regional availability
- ✅ Automatic failover for Cloud SQL
- ✅ Global load balancer with health checks
- ✅ Read replicas for scaling

**Deploy**:
```bash
cd infrastructure/terraform/gcp
terraform apply
```

### Cloud SQL High Availability

**How It Works**:
1. Primary instance in one zone
2. Standby instance in different zone (synchronous replication)
3. Automatic failover in ~30-60 seconds
4. Connection string automatically points to new primary

**Test Failover**:
```bash
# Force failover (for testing)
gcloud sql instances failover ai-self-healing-cloud-db

# Monitor failover
gcloud sql instances describe ai-self-healing-cloud-db
```

## Azure High Availability

### Multi-AZ Architecture

**Components**:
- **AKS Multi-Zone**: Nodes in multiple zones
- **Azure SQL Zone-Redundant**: Automatic failover
- **Failover Groups**: Cross-region failover
- **Application Gateway**: Multi-zone load balancing

**Configuration Files**:
- `terraform/azure/aks.tf`: Multi-zone AKS cluster
- `terraform/azure/sql-ha.tf`: High availability Azure SQL
- `terraform/azure/load-balancer.tf`: Load balancer configuration

**Features**:
- ✅ AKS nodes in multiple zones (1, 2, 3)
- ✅ Azure SQL zone-redundant
- ✅ Failover groups for cross-region DR
- ✅ Application Gateway with health probes
- ✅ Automatic failover

**Deploy**:
```bash
cd infrastructure/terraform/azure
terraform apply
```

### Azure SQL High Availability

**How It Works**:
1. Primary database with zone-redundant storage
2. Automatic failover within same region
3. Failover groups for cross-region failover
4. Connection string automatically updated

**Test Failover**:
```bash
# Force failover (for testing)
az sql failover-group set-primary \
  --resource-group ai-self-healing-cloud-rg \
  --server ai-self-healing-cloud-sql-server \
  --name ai-self-healing-cloud-failover-group

# Monitor failover
az sql db show \
  --resource-group ai-self-healing-cloud-rg \
  --server ai-self-healing-cloud-sql-server \
  --name ai_cloud_db
```

## Kubernetes High Availability

### Multi-Node Deployment

**Components**:
- **Pod Disruption Budgets**: Minimum pods available during updates
- **Pod Anti-Affinity**: Pods distributed across nodes/zones
- **Health Checks**: Liveness and readiness probes
- **Rolling Updates**: Zero-downtime deployments

**Configuration Files**:
- `kubernetes/ha/pod-disruption-budget.yaml`: PDB configurations
- `kubernetes/ha/anti-affinity.yaml`: Anti-affinity rules

**Features**:
- ✅ Pods distributed across nodes
- ✅ Pods distributed across zones
- ✅ Minimum pod availability during disruptions
- ✅ Automatic pod rescheduling on failure

**Apply**:
```bash
kubectl apply -f kubernetes/ha/pod-disruption-budget.yaml
kubectl apply -f kubernetes/ha/anti-affinity.yaml
```

## Failover Scenarios

### 1. Instance Failure

**AWS**:
- Auto Scaling Group launches new instance
- Load balancer routes traffic to healthy instances
- RDS Multi-AZ fails over if database instance fails

**GCP**:
- GKE reschedules pods on healthy nodes
- Cloud SQL automatically fails over to standby
- Load balancer routes to healthy instances

**Azure**:
- AKS reschedules pods on healthy nodes
- Azure SQL fails over to standby
- Application Gateway routes to healthy instances

### 2. Availability Zone Failure

**AWS**:
- Auto Scaling Group launches instances in other AZs
- RDS fails over to standby in different AZ
- Load balancer routes to instances in healthy AZs

**GCP**:
- GKE reschedules pods in other zones
- Cloud SQL fails over to standby in different zone
- Load balancer routes to instances in healthy zones

**Azure**:
- AKS reschedules pods in other zones
- Azure SQL fails over to standby in different zone
- Application Gateway routes to instances in healthy zones

### 3. Database Failure

**All Providers**:
- Automatic failover to standby database
- Connection string automatically updated
- Application reconnects automatically
- Data loss: Minimal (synchronous replication)

## Monitoring High Availability

### AWS

```bash
# Check RDS Multi-AZ status
aws rds describe-db-instances \
  --db-instance-identifier ai-self-healing-cloud-db \
  --query 'DBInstances[0].MultiAZ'

# Check Auto Scaling Group health
aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names ai-self-healing-cloud-agents-asg-ha

# Check load balancer health
aws elbv2 describe-target-health \
  --target-group-arn <target-group-arn>
```

### GCP

```bash
# Check Cloud SQL HA status
gcloud sql instances describe ai-self-healing-cloud-db \
  --format="value(settings.availabilityType)"

# Check GKE node distribution
kubectl get nodes -o wide

# Check load balancer health
gcloud compute backend-services get-health <backend-service>
```

### Azure

```bash
# Check Azure SQL HA status
az sql db show \
  --resource-group ai-self-healing-cloud-rg \
  --server ai-self-healing-cloud-sql-server \
  --name ai_cloud_db \
  --query "zoneRedundant"

# Check AKS node distribution
kubectl get nodes -o wide

# Check Application Gateway health
az network application-gateway show-backend-health \
  --resource-group ai-self-healing-cloud-rg \
  --name ai-self-healing-cloud-appgw
```

## Best Practices

1. **Always Use Multi-AZ**: Deploy resources across multiple availability zones
2. **Enable Automatic Failover**: Configure automatic failover for databases
3. **Monitor Health**: Set up health checks and alerts
4. **Test Failover**: Regularly test failover scenarios
5. **Document Runbooks**: Create runbooks for failover procedures
6. **Set Appropriate Timeouts**: Configure connection timeouts for failover
7. **Use Health Checks**: Implement health checks for all services
8. **Plan for RTO/RPO**: Define Recovery Time Objective and Recovery Point Objective

## Recovery Time Objectives (RTO)

- **AWS RDS Multi-AZ**: 60-120 seconds
- **GCP Cloud SQL Regional**: 30-60 seconds
- **Azure SQL Zone-Redundant**: 30-60 seconds
- **Kubernetes Pod Rescheduling**: 10-30 seconds
- **Load Balancer Health Check**: 5-10 seconds

## Recovery Point Objectives (RPO)

- **Synchronous Replication**: 0 data loss
- **Asynchronous Replication**: Minimal data loss (seconds)
- **Backup Restore**: Up to backup interval (typically 1 hour)

## Next Steps

1. **Enable Multi-AZ**: Deploy resources across multiple zones
2. **Configure Failover**: Set up automatic failover
3. **Test Failover**: Regularly test failover scenarios
4. **Monitor**: Set up monitoring and alerts
5. **Document**: Create runbooks and procedures

