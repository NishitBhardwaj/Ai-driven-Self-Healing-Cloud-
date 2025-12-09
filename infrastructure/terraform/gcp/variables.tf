variable "gcp_project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "gcp_region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "ai-self-healing-cloud"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.1.0.0/24", "10.1.1.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.1.10.0/24", "10.1.11.0/24"]
}

variable "agent_instance_type" {
  description = "GCE instance type for agents"
  type        = string
  default     = "e2-medium"
}

variable "agent_instance_type_spot" {
  description = "GCE instance type for spot instances"
  type        = string
  default     = "e2-medium"
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

variable "agent_volume_size" {
  description = "Disk size for agent instances (GB)"
  type        = number
  default     = 20
}

variable "enable_spot_instances" {
  description = "Enable spot/preemptible instances"
  type        = bool
  default     = false
}

variable "enable_https" {
  description = "Enable HTTPS"
  type        = bool
  default     = true
}

variable "node_zones" {
  description = "List of zones for node distribution"
  type        = list(string)
  default     = ["us-central1-a", "us-central1-b", "us-central1-c"]
}

variable "enable_multi_zone" {
  description = "Enable multi-zone deployment for Cloud SQL"
  type        = bool
  default     = true
}

variable "db_engine_version" {
  description = "Database engine version"
  type        = string
  default     = "POSTGRES_15"
}

variable "db_instance_class" {
  description = "Cloud SQL instance tier"
  type        = string
  default     = "db-f1-micro"
}

variable "db_allocated_storage" {
  description = "Allocated storage for Cloud SQL (GB)"
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "Maximum allocated storage for Cloud SQL (GB)"
  type        = number
  default     = 100
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "ai_cloud_db"
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "admin"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "db_backup_retention_count" {
  description = "Number of backups to retain"
  type        = number
  default     = 7
}

variable "enable_read_replica" {
  description = "Enable Cloud SQL read replica"
  type        = bool
  default     = false
}

