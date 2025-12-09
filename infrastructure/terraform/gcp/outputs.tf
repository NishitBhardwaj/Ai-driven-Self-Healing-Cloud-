output "gke_cluster_name" {
  description = "GKE cluster name"
  value       = google_container_cluster.main.name
}

output "gke_cluster_endpoint" {
  description = "GKE cluster endpoint"
  value       = google_container_cluster.main.endpoint
}

output "load_balancer_ip" {
  description = "Global load balancer IP address"
  value       = google_compute_global_address.agents.address
}

output "network_name" {
  description = "VPC network name"
  value       = google_compute_network.main.name
}

