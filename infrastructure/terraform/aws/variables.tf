variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "ai-self-healing-cloud"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24"]
}

variable "allowed_ssh_cidr" {
  description = "CIDR block allowed for SSH access"
  type        = string
  default     = "0.0.0.0/0"
}

variable "key_pair_name" {
  description = "Name of the AWS key pair"
  type        = string
}

variable "agent_instance_type" {
  description = "EC2 instance type for agents"
  type        = string
  default     = "t3.medium"
}

variable "min_agent_instances" {
  description = "Minimum number of agent instances"
  type        = number
  default     = 2
}

variable "max_agent_instances" {
  description = "Maximum number of agent instances"
  type        = number
  default     = 10
}

variable "desired_agent_instances" {
  description = "Desired number of agent instances"
  type        = number
  default     = 3
}

variable "enable_deletion_protection" {
  description = "Enable deletion protection for load balancer"
  type        = bool
  default     = true
}

variable "enable_https" {
  description = "Enable HTTPS listener"
  type        = bool
  default     = true
}

variable "certificate_arn" {
  description = "ARN of the SSL certificate"
  type        = string
  default     = ""
}

variable "db_engine" {
  description = "Database engine (postgres, mysql)"
  type        = string
  default     = "postgres"
}

variable "db_engine_version" {
  description = "Database engine version"
  type        = string
  default     = "15.4"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "Allocated storage for RDS (GB)"
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "Maximum allocated storage for RDS (GB)"
  type        = number
  default     = 100
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "ai_cloud_db"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "admin"
}

variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
}

variable "db_backup_retention_period" {
  description = "Backup retention period (days)"
  type        = number
  default     = 7
}

variable "enable_read_replica" {
  description = "Enable RDS read replica"
  type        = bool
  default     = false
}

variable "enable_multi_az" {
  description = "Enable Multi-AZ deployment for RDS"
  type        = bool
  default     = true
}

variable "db_availability_zone" {
  description = "Availability zone for RDS (only used if multi-AZ is disabled)"
  type        = string
  default     = ""
}

variable "alert_email" {
  description = "Email address for high availability alerts"
  type        = string
  default     = ""
}

variable "enable_route53_health_check" {
  description = "Enable Route53 health check for load balancer"
  type        = bool
  default     = false
}

variable "enable_rds_event_subscription" {
  description = "Enable RDS event subscription for failover notifications"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "Log retention period in S3 (days)"
  type        = number
  default     = 90
}

variable "agent_volume_size" {
  description = "EBS volume size for agent instances (GB)"
  type        = number
  default     = 20
}

variable "agent_instance_type_spot" {
  description = "EC2 instance type for spot instances"
  type        = string
  default     = "t3.medium"
}

variable "spot_max_price" {
  description = "Maximum price for spot instances"
  type        = string
  default     = "0.05"
}

variable "enable_nlb" {
  description = "Enable Network Load Balancer"
  type        = bool
  default     = false
}

variable "scaling_alert_email" {
  description = "Email for scaling alerts"
  type        = string
  default     = ""
}

