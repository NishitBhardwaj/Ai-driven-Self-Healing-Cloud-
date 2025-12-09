# High Availability Configuration for AWS

# Ensure Auto Scaling Group spans multiple AZs
resource "aws_autoscaling_group" "agents_ha" {
  name                = "${var.project_name}-agents-asg-ha"
  vpc_zone_identifier = aws_subnet.private[*].id  # Spans all private subnets (multiple AZs)
  target_group_arns   = [aws_lb_target_group.agents.arn]
  health_check_type   = "ELB"
  health_check_grace_period = 300
  min_size           = var.min_agent_instances
  max_size           = var.max_agent_instances
  desired_capacity   = var.desired_agent_instances

  # Ensure instances are distributed across AZs
  availability_zones = data.aws_availability_zones.available.names

  launch_template {
    id      = aws_launch_template.agent.id
    version = "$Latest"
  }

  # Instance refresh for zero-downtime updates
  instance_refresh {
    strategy = "Rolling"
    preferences {
      min_healthy_percentage = 50
      instance_warmup        = 300
    }
  }

  tag {
    key                 = "Name"
    value               = "${var.project_name}-agent-ha"
    propagate_at_launch = true
  }

  tag {
    key                 = "HighAvailability"
    value               = "enabled"
    propagate_at_launch = true
  }
}

# Data source for availability zones
data "aws_availability_zones" "available" {
  state = "available"
}

# CloudWatch Alarm for instance health
resource "aws_cloudwatch_metric_alarm" "instance_health" {
  alarm_name          = "${var.project_name}-instance-health"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "StatusCheckFailed"
  namespace           = "AWS/EC2"
  period              = 60
  statistic           = "Sum"
  threshold           = 1
  alarm_description   = "This metric monitors instance health checks"
  treat_missing_data  = "breaching"

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.agents_ha.name
  }

  alarm_actions = [
    aws_sns_topic.alerts.arn
  ]
}

# SNS Topic for High Availability Alerts
resource "aws_sns_topic" "alerts" {
  name = "${var.project_name}-ha-alerts"

  tags = {
    Name = "${var.project_name}-ha-alerts"
  }
}

# SNS Topic Subscription (Email)
resource "aws_sns_topic_subscription" "email" {
  count = var.alert_email != "" ? 1 : 0

  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# Route53 Health Check for Load Balancer
resource "aws_route53_health_check" "alb" {
  count = var.enable_route53_health_check ? 1 : 0

  fqdn              = aws_lb.main.dns_name
  port              = 80
  type              = "HTTP"
  resource_path     = "/health"
  failure_threshold = 3
  request_interval  = 30

  tags = {
    Name = "${var.project_name}-alb-health-check"
  }
}

# RDS Event Subscription for Failover Notifications
resource "aws_db_event_subscription" "rds_failover" {
  count = var.enable_rds_event_subscription ? 1 : 0

  name      = "${var.project_name}-rds-events"
  sns_topic = aws_sns_topic.alerts.arn

  source_type = "db-instance"
  event_categories = [
    "failover",
    "failure",
    "recovery",
    "maintenance"
  ]

  tags = {
    Name = "${var.project_name}-rds-events"
  }
}

