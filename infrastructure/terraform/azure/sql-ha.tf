# Azure SQL Database High Availability Configuration

# SQL Server
resource "azurerm_mssql_server" "main" {
  name                         = "${var.project_name}-sql-server"
  resource_group_name          = azurerm_resource_group.main.name
  location                     = azurerm_resource_group.main.location
  version                      = "12.0"
  administrator_login          = var.db_username
  administrator_login_password = var.db_password

  # High Availability
  minimum_tls_version = "1.2"

  tags = {
    Environment = var.environment
  }
}

# SQL Database with High Availability
resource "azurerm_mssql_database" "main" {
  name           = var.db_name
  server_id      = azurerm_mssql_server.main.id
  collation      = "SQL_Latin1_General_CP1_CI_AS"
  license_type   = "LicenseIncluded"
  max_size_gb    = var.db_max_allocated_storage
  sku_name       = var.db_instance_class
  zone_redundant = var.enable_multi_zone  # Zone-redundant for HA

  # Backup configuration
  short_term_retention_policy {
    retention_days = var.db_backup_retention_period
  }

  # Long-term retention
  long_term_retention_policy {
    weekly_retention  = "P1W"
    monthly_retention = "P1M"
    yearly_retention  = "P1Y"
    week_of_year      = 1
  }

  # Geo-replication (for disaster recovery)
  geo_backup_enabled = var.enable_geo_replication

  tags = {
    Environment = var.environment
  }
}

# Failover Group (for automatic failover)
resource "azurerm_mssql_failover_group" "main" {
  count = var.enable_failover_group ? 1 : 0

  name      = "${var.project_name}-failover-group"
  server_id = azurerm_mssql_server.main.id
  databases = [azurerm_mssql_database.main.id]

  partner_server {
    id = azurerm_mssql_server.secondary[0].id
  }

  read_write_endpoint_failover_policy {
    mode          = "Automatic"
    grace_minutes = 60
  }

  tags = {
    Environment = var.environment
  }
}

# Secondary SQL Server (for failover)
resource "azurerm_mssql_server" "secondary" {
  count = var.enable_failover_group ? 1 : 0

  name                         = "${var.project_name}-sql-server-secondary"
  resource_group_name          = azurerm_resource_group.main.name
  location                     = var.secondary_azure_region
  version                      = "12.0"
  administrator_login          = var.db_username
  administrator_login_password = var.db_password

  minimum_tls_version = "1.2"

  tags = {
    Environment = var.environment
    Role        = "secondary"
  }
}

