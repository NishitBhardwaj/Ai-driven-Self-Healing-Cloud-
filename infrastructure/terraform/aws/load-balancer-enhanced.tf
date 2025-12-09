# Enhanced Load Balancer Configuration

# Application Load Balancer with Enhanced Features
resource "aws_lb" "main_enhanced" {
  name               = "${var.project_name}-alb-enhanced"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = var.enable_deletion_protection
  enable_http2              = true
  enable_cross_zone_load_balancing = true
  enable_tls_version_and_cipher_suite_headers = true
  enable_xff_client_port    = true
  enable_waf_fail_open      = true

  # Access logs
  access_logs {
    bucket  = aws_s3_bucket.logs.id
    prefix  = "alb-access-logs"
    enabled = true
  }

  tags = {
    Name = "${var.project_name}-alb-enhanced"
  }
}

# Enhanced Target Group with Sticky Sessions
resource "aws_lb_target_group" "agents_enhanced" {
  name     = "${var.project_name}-agents-tg-enhanced"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  # Health check configuration
  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    path                = "/health"
    protocol            = "HTTP"
    matcher             = "200"
    port                = "traffic-port"
  }

  # Sticky sessions
  stickiness {
    enabled         = true
    type            = "lb_cookie"
    cookie_duration = 86400
    cookie_name     = "ai-cloud-session"
  }

  # Deregistration delay
  deregistration_delay = 30

  # Connection draining
  connection_termination = true

  # Preserve client IP
  preserve_client_ip = false

  tags = {
    Name = "${var.project_name}-agents-tg-enhanced"
  }
}

# Target Group for Metrics (separate from main traffic)
resource "aws_lb_target_group" "agents_metrics" {
  name     = "${var.project_name}-agents-metrics-tg"
  port     = 8081
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    path                = "/metrics"
    protocol            = "HTTP"
    matcher             = "200"
  }

  tags = {
    Name = "${var.project_name}-agents-metrics-tg"
  }
}

# Enhanced ALB Listener with Rules
resource "aws_lb_listener" "https_enhanced" {
  count = var.enable_https ? 1 : 0

  load_balancer_arn = aws_lb.main_enhanced.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.agents_enhanced.arn
  }
}

# Listener Rule for API endpoints
resource "aws_lb_listener_rule" "api" {
  count = var.enable_https ? 1 : 0

  listener_arn = aws_lb_listener.https_enhanced[0].arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.agents_enhanced.arn
  }

  condition {
    path_pattern {
      values = ["/api/*"]
    }
  }
}

# Listener Rule for Health Checks
resource "aws_lb_listener_rule" "health" {
  count = var.enable_https ? 1 : 0

  listener_arn = aws_lb_listener.https_enhanced[0].arn
  priority     = 1

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.agents_enhanced.arn
  }

  condition {
    path_pattern {
      values = ["/health"]
    }
  }
}

# Listener Rule for Metrics (internal only)
resource "aws_lb_listener_rule" "metrics" {
  count = var.enable_https ? 1 : 0

  listener_arn = aws_lb_listener.https_enhanced[0].arn
  priority     = 2

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.agents_metrics.arn
  }

  condition {
    path_pattern {
      values = ["/metrics"]
    }
  }

  condition {
    source_ip {
      values = [var.vpc_cidr]
    }
  }
}

# Network Load Balancer for High Performance
resource "aws_lb" "nlb" {
  count = var.enable_nlb ? 1 : 0

  name               = "${var.project_name}-nlb"
  internal           = false
  load_balancer_type = "network"
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = var.enable_deletion_protection
  enable_cross_zone_load_balancing = true

  tags = {
    Name = "${var.project_name}-nlb"
  }
}

# NLB Target Group
resource "aws_lb_target_group" "agents_nlb" {
  count = var.enable_nlb ? 1 : 0

  name     = "${var.project_name}-agents-nlb-tg"
  port     = 8080
  protocol = "TCP"
  vpc_id   = aws_vpc.main.id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 10
    interval            = 30
    protocol            = "TCP"
  }

  deregistration_delay = 30

  tags = {
    Name = "${var.project_name}-agents-nlb-tg"
  }
}

# NLB Listener
resource "aws_lb_listener" "nlb" {
  count = var.enable_nlb ? 1 : 0

  load_balancer_arn = aws_lb.nlb[0].arn
  port              = "80"
  protocol          = "TCP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.agents_nlb[0].arn
  }
}

