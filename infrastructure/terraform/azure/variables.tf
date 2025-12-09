variable "azure_region" {
  description = "Azure region"
  type        = string
  default     = "eastus"
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

variable "vnet_cidr" {
  description = "CIDR block for Virtual Network"
  type        = string
  default     = "10.2.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.2.1.0/24", "10.2.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.2.11.0/24", "10.2.12.0/24"]
}

variable "agent_instance_type" {
  description = "Azure VM size for agents"
  type        = string
  default     = "Standard_B2s"
}

variable "agent_instance_type_spot" {
  description = "Azure VM size for spot instances"
  type        = string
  default     = "Standard_B2s"
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
  default     = 30
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.28"
}

variable "enable_spot_instances" {
  description = "Enable spot instances"
  type        = bool
  default     = false
}

variable "spot_max_price" {
  description = "Maximum price for spot instances"
  type        = number
  default     = 0.05
}

variable "enable_application_gateway" {
  description = "Enable Application Gateway"
  type        = bool
  default     = false
}

variable "enable_multi_zone" {
  description = "Enable multi-zone deployment"
  type        = bool
  default     = true
}

variable "db_engine_version" {
  description = "Database engine version"
  type        = string
  default     = "12.0"
}

variable "db_instance_class" {
  description = "Azure SQL database SKU"
  type        = string
  default     = "S0"
}

variable "db_allocated_storage" {
  description = "Allocated storage for Azure SQL (GB)"
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "Maximum allocated storage for Azure SQL (GB)"
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

variable "db_backup_retention_period" {
  description = "Backup retention period (days)"
  type        = number
  default     = 7
}

variable "enable_geo_replication" {
  description = "Enable geo-replication for Azure SQL"
  type        = bool
  default     = false
}

variable "enable_failover_group" {
  description = "Enable failover group for Azure SQL"
  type        = bool
  default     = false
}

variable "secondary_azure_region" {
  description = "Secondary Azure region for failover"
  type        = string
  default     = "westus2"
}

