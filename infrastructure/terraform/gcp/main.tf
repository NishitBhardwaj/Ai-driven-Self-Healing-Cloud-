terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  
  backend "gcs" {
    bucket = "ai-cloud-terraform-state"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

# Data sources
data "google_client_config" "default" {}

data "google_compute_zones" "available" {
  region = var.gcp_region
}

# VPC Network
resource "google_compute_network" "main" {
  name                    = "${var.project_name}-vpc"
  auto_create_subnetworks = false
  
  depends_on = [google_project_service.compute]
}

# Public Subnet
resource "google_compute_subnetwork" "public" {
  count = length(var.public_subnet_cidrs)
  
  name          = "${var.project_name}-public-subnet-${count.index + 1}"
  ip_cidr_range = var.public_subnet_cidrs[count.index]
  region        = var.gcp_region
  network       = google_compute_network.main.id
  
  private_ip_google_access = false
}

# Private Subnet
resource "google_compute_subnetwork" "private" {
  count = length(var.private_subnet_cidrs)
  
  name          = "${var.project_name}-private-subnet-${count.index + 1}"
  ip_cidr_range = var.private_subnet_cidrs[count.index]
  region        = var.gcp_region
  network       = google_compute_network.main.id
  
  private_ip_google_access = true
}

# Enable required APIs
resource "google_project_service" "compute" {
  service = "compute.googleapis.com"
}

resource "google_project_service" "container" {
  service = "container.googleapis.com"
}

resource "google_project_service" "sql" {
  service = "sqladmin.googleapis.com"
}

resource "google_project_service" "storage" {
  service = "storage-api.googleapis.com"
}

