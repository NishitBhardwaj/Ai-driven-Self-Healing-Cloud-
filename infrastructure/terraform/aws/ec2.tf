# Security Group for Agent Instances
resource "aws_security_group" "agents" {
  name        = "${var.project_name}-agents-sg"
  description = "Security group for AI agent instances"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  ingress {
    description = "Agent API Ports"
    from_port   = 8080
    to_port     = 8087
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-agents-sg"
  }
}

# Launch Template for Agent Instances
resource "aws_launch_template" "agent" {
  name_prefix   = "${var.project_name}-agent-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = var.agent_instance_type
  key_name      = var.key_pair_name

  vpc_security_group_ids = [aws_security_group.agents.id]

  iam_instance_profile {
    name = aws_iam_instance_profile.agent.name
  }

  user_data = base64encode(templatefile("${path.module}/templates/agent-userdata.sh", {
    environment = var.environment
  }))

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "${var.project_name}-agent"
      Type = "agent"
    }
  }
}

# Auto Scaling Group for Agents
resource "aws_autoscaling_group" "agents" {
  name                = "${var.project_name}-agents-asg"
  vpc_zone_identifier = aws_subnet.private[*].id
  target_group_arns   = [aws_lb_target_group.agents.arn]
  health_check_type   = "ELB"
  health_check_grace_period = 300
  min_size           = var.min_agent_instances
  max_size           = var.max_agent_instances
  desired_capacity   = var.desired_agent_instances

  launch_template {
    id      = aws_launch_template.agent.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "${var.project_name}-agent"
    propagate_at_launch = true
  }
}

# Auto Scaling Policy
resource "aws_autoscaling_policy" "agents_scale_up" {
  name                   = "${var.project_name}-agents-scale-up"
  scaling_adjustment     = 1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.agents.name
}

resource "aws_autoscaling_policy" "agents_scale_down" {
  name                   = "${var.project_name}-agents-scale-down"
  scaling_adjustment     = -1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.agents.name
}

# CloudWatch Alarms for Auto Scaling
resource "aws_cloudwatch_metric_alarm" "agents_cpu_high" {
  alarm_name          = "${var.project_name}-agents-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "This metric monitors agent CPU utilization"
  alarm_actions       = [aws_autoscaling_policy.agents_scale_up.arn]

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.agents.name
  }
}

resource "aws_cloudwatch_metric_alarm" "agents_cpu_low" {
  alarm_name          = "${var.project_name}-agents-cpu-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 20
  alarm_description   = "This metric monitors agent CPU utilization"
  alarm_actions       = [aws_autoscaling_policy.agents_scale_down.arn]

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.agents.name
  }
}

