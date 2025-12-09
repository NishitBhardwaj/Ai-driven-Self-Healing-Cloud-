# Enhanced Auto Scaling Configuration

# Launch Template with Enhanced Configuration
resource "aws_launch_template" "agent_enhanced" {
  name_prefix   = "${var.project_name}-agent-enhanced-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = var.agent_instance_type
  key_name      = var.key_pair_name

  vpc_security_group_ids = [aws_security_group.agents.id]

  iam_instance_profile {
    name = aws_iam_instance_profile.agent.name
  }

  block_device_mappings {
    device_name = "/dev/xvda"
    ebs {
      volume_size           = var.agent_volume_size
      volume_type           = "gp3"
      iops                  = 3000
      throughput            = 125
      encrypted             = true
      delete_on_termination = true
    }
  }

  monitoring {
    enabled = true
  }

  user_data = base64encode(templatefile("${path.module}/templates/agent-userdata.sh", {
    environment = var.environment
  }))

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name                              = "${var.project_name}-agent"
      Type                              = "agent"
      "k8s.io/cluster-autoscaler/enabled" = "true"
      "k8s.io/cluster-autoscaler/${var.project_name}-cluster" = "owned"
    }
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Auto Scaling Group with Enhanced Configuration
resource "aws_autoscaling_group" "agents_enhanced" {
  name                = "${var.project_name}-agents-asg-enhanced"
  vpc_zone_identifier = aws_subnet.private[*].id
  target_group_arns   = [aws_lb_target_group.agents.arn]
  health_check_type   = "ELB"
  health_check_grace_period = 300
  
  min_size         = var.min_agent_instances
  max_size         = var.max_agent_instances
  desired_capacity = var.desired_agent_instances

  launch_template {
    id      = aws_launch_template.agent_enhanced.id
    version = "$Latest"
  }

  # Instance refresh for rolling updates
  instance_refresh {
    strategy = "Rolling"
    preferences {
      min_healthy_percentage = 50
      instance_warmup        = 300
    }
    triggers = ["tag"]
  }

  # Mixed instances for cost optimization
  mixed_instances_policy {
    launch_template {
      launch_template_specification {
        launch_template_id = aws_launch_template.agent_enhanced.id
        version           = "$Latest"
      }
      override {
        instance_type = var.agent_instance_type
      }
      override {
        instance_type = var.agent_instance_type_spot
      }
    }

    instances_distribution {
      on_demand_percentage_above_base_capacity = 20
      spot_instance_pools                      = 2
      spot_max_price                          = var.spot_max_price
    }
  }

  tag {
    key                 = "Name"
    value               = "${var.project_name}-agent"
    propagate_at_launch = true
  }

  tag {
    key                 = "Environment"
    value               = var.environment
    propagate_at_launch = true
  }

  tag {
    key                 = "ManagedBy"
    value               = "Terraform"
    propagate_at_launch = true
  }
}

# Predictive Scaling Policy
resource "aws_autoscaling_policy" "agents_predictive" {
  name                   = "${var.project_name}-agents-predictive-scaling"
  autoscaling_group_name = aws_autoscaling_group.agents_enhanced.name
  policy_type            = "PredictiveScaling"
  predictive_scaling_configuration {
    metric_specification {
      target_value = 70.0
      predefined_metric_pair_specification {
        predefined_metric_type = "ASGCPUUtilization"
        resource_label         = "ai-cloud-agents"
      }
    }
    mode                         = "ForecastAndScale"
    scheduling_buffer_time       = 10
    max_capacity_breach_behavior = "IncreaseMaxCapacity"
    max_capacity_buffer          = 10
  }
}

# Target Tracking Scaling Policy (CPU)
resource "aws_autoscaling_policy" "agents_target_tracking_cpu" {
  name                   = "${var.project_name}-agents-target-tracking-cpu"
  autoscaling_group_name = aws_autoscaling_group.agents_enhanced.name
  policy_type            = "TargetTrackingScaling"
  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value = 70.0
    disable_scale_in = false
  }
}

# Target Tracking Scaling Policy (Request Count)
resource "aws_autoscaling_policy" "agents_target_tracking_request_count" {
  name                   = "${var.project_name}-agents-target-tracking-request-count"
  autoscaling_group_name = aws_autoscaling_group.agents_enhanced.name
  policy_type            = "TargetTrackingScaling"
  target_tracking_configuration {
    customized_metric_specification {
      metric_name = "RequestCountPerTarget"
      namespace   = "AWS/ApplicationELB"
      statistic   = "Average"
      unit        = "Count"
      dimensions {
        name  = "TargetGroup"
        value = aws_lb_target_group.agents.arn_suffix
      }
    }
    target_value = 1000.0
    disable_scale_in = false
  }
}

# Step Scaling Policy for Rapid Scale-Up
resource "aws_autoscaling_policy" "agents_step_scale_up" {
  name                   = "${var.project_name}-agents-step-scale-up"
  autoscaling_group_name = aws_autoscaling_group.agents_enhanced.name
  adjustment_type        = "ChangeInCapacity"
  policy_type            = "StepScaling"
  
  step_adjustment {
    scaling_adjustment          = 2
    metric_interval_lower_bound = 0
    metric_interval_upper_bound = 10
  }
  
  step_adjustment {
    scaling_adjustment          = 4
    metric_interval_lower_bound = 10
    metric_interval_upper_bound = 20
  }
  
  step_adjustment {
    scaling_adjustment          = 8
    metric_interval_lower_bound = 20
  }
}

# CloudWatch Alarms for Enhanced Auto Scaling
resource "aws_cloudwatch_metric_alarm" "agents_cpu_high_enhanced" {
  alarm_name          = "${var.project_name}-agents-cpu-high-enhanced"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 75
  alarm_description   = "This metric monitors agent CPU utilization for enhanced scaling"
  alarm_actions       = [
    aws_autoscaling_policy.agents_step_scale_up.arn,
    aws_sns_topic.scaling_alerts.arn
  ]

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.agents_enhanced.name
  }
}

resource "aws_cloudwatch_metric_alarm" "agents_memory_high" {
  alarm_name          = "${var.project_name}-agents-memory-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "mem_used_percent"
  namespace           = "CWAgent"
  period              = 300
  statistic           = "Average"
  threshold           = 85
  alarm_description   = "This metric monitors agent memory utilization"
  alarm_actions       = [aws_autoscaling_policy.agents_scale_up.arn]

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.agents_enhanced.name
  }
}

resource "aws_cloudwatch_metric_alarm" "agents_request_count_high" {
  alarm_name          = "${var.project_name}-agents-request-count-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "RequestCountPerTarget"
  namespace           = "AWS/ApplicationELB"
  period              = 300
  statistic           = "Sum"
  threshold           = 5000
  alarm_description   = "This metric monitors request count per target"
  alarm_actions       = [aws_autoscaling_policy.agents_scale_up.arn]

  dimensions = {
    TargetGroup = aws_lb_target_group.agents.arn_suffix
  }
}

# SNS Topic for Scaling Alerts
resource "aws_sns_topic" "scaling_alerts" {
  name = "${var.project_name}-scaling-alerts"
  
  tags = {
    Name = "${var.project_name}-scaling-alerts"
  }
}

resource "aws_sns_topic_subscription" "scaling_alerts_email" {
  count = var.scaling_alert_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.scaling_alerts.arn
  protocol  = "email"
  endpoint  = var.scaling_alert_email
}

