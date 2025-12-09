# AKS Cluster
resource "azurerm_kubernetes_cluster" "main" {
  name                = "${var.project_name}-aks"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = "${var.project_name}-aks"
  kubernetes_version  = var.kubernetes_version

  default_node_pool {
    name                = "agentpool"
    node_count          = var.min_agent_instances
    vm_size             = var.agent_instance_type
    os_disk_size_gb     = var.agent_volume_size
    type                = "VirtualMachineScaleSets"
    enable_auto_scaling = true
    min_count           = var.min_agent_instances
    max_count           = var.max_agent_instances
    vnet_subnet_id      = azurerm_subnet.private[0].id
    zones               = [1, 2, 3]  # Multi-AZ deployment
  }

  network_profile {
    network_plugin    = "azure"
    network_policy    = "azure"
    load_balancer_sku = "standard"
    service_cidr      = "10.2.0.0/16"
    dns_service_ip    = "10.2.0.10"
  }

  identity {
    type = "SystemAssigned"
  }

  role_based_access_control_enabled = true

  tags = {
    Environment = var.environment
  }
}

# Additional Node Pool for Spot Instances
resource "azurerm_kubernetes_cluster_node_pool" "agents_spot" {
  count = var.enable_spot_instances ? 1 : 0

  name                  = "agentspot"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.main.id
  vm_size               = var.agent_instance_type_spot
  node_count            = 0
  enable_auto_scaling   = true
  min_count             = 0
  max_count             = var.max_agent_instances
  priority              = "Spot"
  eviction_policy       = "Delete"
  spot_max_price        = var.spot_max_price
  os_type               = "Linux"
  os_disk_size_gb       = var.agent_volume_size

  node_taints = [
    "kubernetes.azure.com/scalesetpriority=spot:NoSchedule"
  ]

  tags = {
    Environment = var.environment
    NodeType    = "spot"
  }
}

