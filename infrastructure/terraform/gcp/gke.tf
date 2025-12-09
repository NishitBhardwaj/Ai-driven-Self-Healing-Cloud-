# GKE Cluster with Multi-Zone High Availability
resource "google_container_cluster" "main" {
  name     = "${var.project_name}-gke-cluster"
  location = var.gcp_region  # Regional cluster for multi-zone HA

  # Remove default node pool
  remove_default_node_pool = true
  initial_node_count       = 1

  # Network configuration
  network    = google_compute_network.main.name
  subnetwork = google_compute_subnetwork.private[0].name

  # Enable features
  enable_kubernetes_alpha = false
  enable_legacy_abac      = false

  # Network policy
  network_policy {
    enabled = true
  }

  # Private cluster
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }

  # Master authorized networks
  master_authorized_networks_config {
    cidr_blocks {
      cidr_block   = "0.0.0.0/0"
      display_name = "All"
    }
  }

  # Workload Identity
  workload_identity_config {
    workload_pool = "${var.gcp_project_id}.svc.id.goog"
  }

  # Release channel
  release_channel {
    channel = "REGULAR"
  }

  # Maintenance window
  maintenance_policy {
    daily_maintenance_window {
      start_time = "03:00"
    }
  }

  # Addons
  addons_config {
    http_load_balancing {
      disabled = false
    }
    horizontal_pod_autoscaling {
      disabled = false
    }
    network_policy_config {
      disabled = false
    }
  }

  # Resource usage export
  resource_usage_export_config {
    enable_network_egress_metering = true
    bigquery_destination {
      dataset_id = "gke_usage"
    }
  }

  depends_on = [
    google_project_service.container,
    google_project_service.compute
  ]
}

# Node Pool for Agents (Multi-Zone)
resource "google_container_node_pool" "agents" {
  name       = "${var.project_name}-agents-pool"
  location   = var.gcp_region  # Regional pool spans multiple zones
  cluster    = google_container_cluster.main.name
  node_count = var.min_agent_instances

  autoscaling {
    min_node_count = var.min_agent_instances
    max_node_count = var.max_agent_instances
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  # Multi-zone configuration
  node_locations = var.node_zones  # Spread nodes across zones

  node_config {
    preemptible  = false
    machine_type = var.agent_instance_type
    disk_size_gb = var.agent_volume_size
    disk_type    = "pd-ssd"

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
    ]

    labels = {
      environment = var.environment
      node-type   = "agent"
    }

    tags = ["agent-nodes"]
  }
}

# Node Pool for Spot Instances (Cost Optimization)
resource "google_container_node_pool" "agents_spot" {
  count = var.enable_spot_instances ? 1 : 0

  name       = "${var.project_name}-agents-spot-pool"
  location   = var.gcp_region
  cluster    = google_container_cluster.main.name
  node_count = 0

  autoscaling {
    min_node_count = 0
    max_node_count = var.max_agent_instances
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  node_config {
    preemptible  = true
    machine_type = var.agent_instance_type_spot
    disk_size_gb = var.agent_volume_size
    disk_type    = "pd-standard"

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]

    labels = {
      environment = var.environment
      node-type   = "agent-spot"
    }

    taint {
      key    = "cloud.google.com/gke-preemptible"
      value  = "true"
      effect = "NO_SCHEDULE"
    }
  }
}

