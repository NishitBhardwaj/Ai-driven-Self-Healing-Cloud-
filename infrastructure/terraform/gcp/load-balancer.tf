# Global Load Balancer (HTTP/HTTPS)
resource "google_compute_backend_service" "agents" {
  name                  = "${var.project_name}-backend-service"
  protocol              = "HTTP"
  port_name             = "http"
  timeout_sec           = 30
  enable_cdn            = false
  load_balancing_scheme = "EXTERNAL"

  health_checks = [google_compute_health_check.agents.id]

  backend {
    group = google_container_node_pool.agents.instance_group_urls[0]
    balancing_mode = "UTILIZATION"
    max_utilization = 0.8
    capacity_scaler = 1.0
  }

  session_affinity = "CLIENT_IP"
  affinity_cookie_ttl_sec = 86400

  log_config {
    enable      = true
    sample_rate = 1.0
  }
}

# Health Check
resource "google_compute_health_check" "agents" {
  name               = "${var.project_name}-health-check"
  check_interval_sec = 10
  timeout_sec        = 5
  healthy_threshold = 2
  unhealthy_threshold = 3

  http_health_check {
    request_path = "/health"
    port         = 8080
  }
}

# URL Map
resource "google_compute_url_map" "agents" {
  name            = "${var.project_name}-url-map"
  default_service = google_compute_backend_service.agents.id

  host_rule {
    hosts        = ["api.ai-cloud.example.com"]
    path_matcher = "allpaths"
  }

  path_matcher {
    name            = "allpaths"
    default_service = google_compute_backend_service.agents.id

    path_rule {
      paths   = ["/api/*"]
      service = google_compute_backend_service.agents.id
    }
  }
}

# HTTP Proxy
resource "google_compute_target_http_proxy" "agents" {
  name    = "${var.project_name}-http-proxy"
  url_map = google_compute_url_map.agents.id
}

# HTTPS Proxy
resource "google_compute_target_https_proxy" "agents" {
  count = var.enable_https ? 1 : 0

  name             = "${var.project_name}-https-proxy"
  url_map          = google_compute_url_map.agents.id
  ssl_certificates = [google_compute_managed_ssl_certificate.agents[0].id]
}

# SSL Certificate
resource "google_compute_managed_ssl_certificate" "agents" {
  count = var.enable_https ? 1 : 0

  name = "${var.project_name}-ssl-cert"

  managed {
    domains = ["api.ai-cloud.example.com"]
  }
}

# Global Forwarding Rule (HTTP)
resource "google_compute_global_forwarding_rule" "agents_http" {
  name       = "${var.project_name}-forwarding-rule-http"
  target     = google_compute_target_http_proxy.agents.id
  port_range = "80"
  ip_address = google_compute_global_address.agents.address
}

# Global Forwarding Rule (HTTPS)
resource "google_compute_global_forwarding_rule" "agents_https" {
  count = var.enable_https ? 1 : 0

  name       = "${var.project_name}-forwarding-rule-https"
  target     = google_compute_target_https_proxy.agents[0].id
  port_range = "443"
  ip_address = google_compute_global_address.agents.address
}

# Global IP Address
resource "google_compute_global_address" "agents" {
  name = "${var.project_name}-global-ip"
}

# Regional Load Balancer (Internal)
resource "google_compute_region_backend_service" "agents_internal" {
  name                  = "${var.project_name}-backend-internal"
  region                = var.gcp_region
  protocol              = "HTTP"
  load_balancing_scheme = "INTERNAL"
  health_checks         = [google_compute_health_check.agents.id]

  backend {
    group = google_container_node_pool.agents.instance_group_urls[0]
    balancing_mode = "UTILIZATION"
    max_utilization = 0.8
  }

  session_affinity = "CLIENT_IP"
}

# Internal Forwarding Rule
resource "google_compute_forwarding_rule" "agents_internal" {
  name                  = "${var.project_name}-forwarding-rule-internal"
  region                = var.gcp_region
  load_balancing_scheme = "INTERNAL"
  backend_service       = google_compute_region_backend_service.agents_internal.id
  ports                 = ["8080"]
  network               = google_compute_network.main.name
  subnetwork            = google_compute_subnetwork.private[0].name
}

