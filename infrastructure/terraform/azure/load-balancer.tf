# Public IP for Load Balancer
resource "azurerm_public_ip" "agents" {
  name                = "${var.project_name}-lb-public-ip"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"

  tags = {
    Environment = var.environment
  }
}

# Load Balancer
resource "azurerm_lb" "agents" {
  name                = "${var.project_name}-lb"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "Standard"

  frontend_ip_configuration {
    name                 = "PublicIPAddress"
    public_ip_address_id = azurerm_public_ip.agents.id
  }

  tags = {
    Environment = var.environment
  }
}

# Backend Address Pool
resource "azurerm_lb_backend_address_pool" "agents" {
  loadbalancer_id = azurerm_lb.agents.id
  name            = "${var.project_name}-backend-pool"
}

# Health Probe
resource "azurerm_lb_probe" "agents" {
  loadbalancer_id     = azurerm_lb.agents.id
  name                = "${var.project_name}-health-probe"
  port                = 8080
  protocol            = "Http"
  request_path        = "/health"
  interval_in_seconds = 30
  number_of_probes    = 3
}

# Load Balancing Rule
resource "azurerm_lb_rule" "agents" {
  loadbalancer_id                = azurerm_lb.agents.id
  name                           = "${var.project_name}-lb-rule"
  protocol                       = "Tcp"
  frontend_port                  = 80
  backend_port                   = 8080
  frontend_ip_configuration_name = "PublicIPAddress"
  backend_address_pool_ids       = [azurerm_lb_backend_address_pool.agents.id]
  probe_id                       = azurerm_lb_probe.agents.id
  idle_timeout_in_minutes        = 4
  load_distribution              = "SourceIP"
  enable_floating_ip             = false
}

# Application Gateway (Alternative to Load Balancer)
resource "azurerm_application_gateway" "agents" {
  count = var.enable_application_gateway ? 1 : 0

  name                = "${var.project_name}-appgw"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  sku {
    name     = "Standard_v2"
    tier     = "Standard_v2"
    capacity = 2
  }

  gateway_ip_configuration {
    name      = "${var.project_name}-ip-config"
    subnet_id = azurerm_subnet.public[0].id
  }

  frontend_port {
    name = "http"
    port = 80
  }

  frontend_port {
    name = "https"
    port = 443
  }

  frontend_ip_configuration {
    name                 = "${var.project_name}-frontend-ip"
    public_ip_address_id = azurerm_public_ip.agents.id
  }

  backend_address_pool {
    name = "${var.project_name}-backend-pool"
  }

  backend_http_settings {
    name                  = "${var.project_name}-http-settings"
    cookie_based_affinity = "Enabled"
    path                  = "/"
    port                  = 8080
    protocol              = "Http"
    request_timeout       = 60
    probe_name            = "${var.project_name}-probe"
  }

  http_listener {
    name                           = "${var.project_name}-listener"
    frontend_ip_configuration_name  = "${var.project_name}-frontend-ip"
    frontend_port_name              = "http"
    protocol                       = "Http"
  }

  request_routing_rule {
    name                       = "${var.project_name}-routing-rule"
    rule_type                  = "Basic"
    http_listener_name         = "${var.project_name}-listener"
    backend_address_pool_name  = "${var.project_name}-backend-pool"
    backend_http_settings_name = "${var.project_name}-http-settings"
  }

  probe {
    name                = "${var.project_name}-probe"
    protocol            = "Http"
    path                = "/health"
    host                = "127.0.0.1"
    interval            = 30
    timeout             = 30
    unhealthy_threshold = 3
  }

  tags = {
    Environment = var.environment
  }
}

