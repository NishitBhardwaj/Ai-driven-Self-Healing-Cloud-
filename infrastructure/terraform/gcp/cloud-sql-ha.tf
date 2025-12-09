# Cloud SQL High Availability Configuration

# Cloud SQL Instance with High Availability
resource "google_sql_database_instance" "main" {
  name             = "${var.project_name}-db"
  database_version = var.db_engine_version
  region           = var.gcp_region

  settings {
    tier              = var.db_instance_class
    availability_type = var.enable_multi_zone ? "REGIONAL" : "ZONAL"
    
    # High Availability
    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = var.db_backup_retention_count
        retention_unit   = "COUNT"
      }
    }

    # Maintenance window
    maintenance_window {
      day          = 1
      hour         = 4
      update_track = "stable"
    }

    # IP Configuration
    ip_configuration {
      ipv4_enabled                                  = false
      private_network                               = google_compute_network.main.id
      enable_private_path_for_google_cloud_services = true
    }

    # Database flags
    database_flags {
      name  = "max_connections"
      value = "100"
    }

    # Insights
    insights_config {
      query_insights_enabled  = true
      query_string_length     = 1024
      record_application_tags = true
      record_client_address   = true
    }

    # Disk configuration
    disk_type       = "PD_SSD"
    disk_size       = var.db_allocated_storage
    disk_autoresize = true
    disk_autoresize_limit = var.db_max_allocated_storage
  }

  deletion_protection = var.environment == "production"
}

# Cloud SQL Database
resource "google_sql_database" "main" {
  name     = var.db_name
  instance = google_sql_database_instance.main.name
}

# Cloud SQL User
resource "google_sql_user" "main" {
  name     = var.db_username
  instance = google_sql_database_instance.main.name
  password = var.db_password
}

# Cloud SQL Read Replica (for high availability)
resource "google_sql_database_instance" "read_replica" {
  count = var.enable_read_replica ? 1 : 0

  name                 = "${var.project_name}-db-replica"
  master_instance_name = google_sql_database_instance.main.name
  region               = var.gcp_region
  database_version     = var.db_engine_version

  replica_configuration {
    failover_target = true
  }

  settings {
    tier              = var.db_instance_class
    availability_type = "REGIONAL"
    
    disk_type       = "PD_SSD"
    disk_size       = var.db_allocated_storage
    disk_autoresize = true
  }

  deletion_protection = false
}

