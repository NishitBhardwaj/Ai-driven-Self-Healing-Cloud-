package core

import (
	"fmt"
)

// ExampleExplanations demonstrates the explainability format for different agents
// These examples show how explanations appear in the UI

// ExampleSelfHealingExplanation demonstrates Self-Healing Agent explanation
func ExampleSelfHealingExplanation() {
	input := map[string]interface{}{
		"service_id":   "web-app-123",
		"failure_type": "crash_loop",
		"error":        "Pod restarting repeatedly",
	}
	
	output := map[string]interface{}{
		"action":  "restart_pod",
		"success": true,
	}
	
	agent := &SelfHealingAgentExample{}
	explanation := agent.ExplainAction(input, output)
	
	fmt.Println("Message: Action automatically executed.")
	fmt.Printf("Explanation: %s\n", explanation)
	// Output:
	// Message: Action automatically executed.
	// Explanation: The agent detected that service 'web-app-123' experienced crash_loop failure (Pod restarting repeatedly) and restarted the service to restore service availability.
}

// ExampleScalingExplanation demonstrates Scaling Agent explanation
func ExampleScalingExplanation() {
	input := map[string]interface{}{
		"cpu_usage": 0.95,
		"replicas":  3,
	}
	
	output := map[string]interface{}{
		"action":   "scale_up",
		"replicas": 5,
	}
	
	agent := &ScalingAgentExample{}
	explanation := agent.ExplainAction(input, output)
	
	fmt.Println("Message: Action automatically executed.")
	fmt.Printf("Explanation: %s\n", explanation)
	// Output:
	// Message: Action automatically executed.
	// Explanation: The agent detected that CPU usage exceeded 90% (current: 95.0%) and scaled up from 3 to 5 replicas to prevent service degradation and ensure optimal performance.
}

// ExampleSecurityExplanation demonstrates Security Agent explanation
func ExampleSecurityExplanation() {
	input := []map[string]interface{}{
		{
			"source_ip": "192.168.1.100",
			"action":    "failed_login",
			"count":     10,
		},
	}
	
	output := map[string]interface{}{
		"action":     "block_ip",
		"blocked_ip": "192.168.1.100",
		"severity":   "high",
	}
	
	agent := &SecurityAgentExample{}
	explanation := agent.ExplainAction(input, output)
	
	fmt.Println("Message: Action automatically executed.")
	fmt.Printf("Explanation: %s\n", explanation)
	// Output:
	// Message: Action automatically executed.
	// Explanation: The agent detected that multiple failed login attempts were detected and blocked IP address 192.168.1.100 to prevent a critical security breach.
}

// ExampleMonitoringExplanation demonstrates Performance Monitoring Agent explanation
func ExampleMonitoringExplanation() {
	input := map[string]interface{}{
		"metrics": []string{"cpu", "memory", "latency"},
	}
	
	output := map[string]interface{}{
		"anomalies":           []string{"high_cpu", "high_latency"},
		"threshold_violations": []string{"cpu > 90%"},
		"action":              "alert",
	}
	
	agent := &MonitoringAgentExample{}
	explanation := agent.ExplainAction(input, output)
	
	fmt.Println("Message: Action automatically executed.")
	fmt.Printf("Explanation: %s\n", explanation)
	// Output:
	// Message: Action automatically executed.
	// Explanation: The agent detected that 2 anomaly(ies) in system metrics and 1 threshold violation(s) and analyzed the metrics to identify performance bottlenecks and ensure system health.
}

// Mock agent examples for demonstration
type SelfHealingAgentExample struct{}
type ScalingAgentExample struct{}
type SecurityAgentExample struct{}
type MonitoringAgentExample struct{}

func (a *SelfHealingAgentExample) ExplainAction(input interface{}, output interface{}) string {
	return FormatExplanation(
		"service 'web-app-123' experienced crash_loop failure",
		"restarted the service",
		"restore service availability",
	)
}

func (a *ScalingAgentExample) ExplainAction(input interface{}, output interface{}) string {
	return FormatExplanation(
		"CPU usage exceeded 90% (current: 95.0%)",
		"scaled up from 3 to 5 replicas",
		"prevent service degradation and ensure optimal performance",
	)
}

func (a *SecurityAgentExample) ExplainAction(input interface{}, output interface{}) string {
	return FormatExplanation(
		"multiple failed login attempts were detected",
		"blocked IP address 192.168.1.100",
		"prevent a critical security breach",
	)
}

func (a *MonitoringAgentExample) ExplainAction(input interface{}, output interface{}) string {
	return FormatExplanation(
		"2 anomaly(ies) in system metrics and 1 threshold violation(s)",
		"analyzed the metrics",
		"identify performance bottlenecks and ensure system health",
	)
}

