package core

import (
	"fmt"
	"time"
)

// ExampleScalingAgentExplanation demonstrates Chain-of-Thought reasoning for Scaling Agent
func ExampleScalingAgentExplanation() *ActionExplanation {
	xaiEngine := NewXAIEngine(GetDefaultLogger(), NewLLMReasoningIntegration())

	// Simulate Scaling Agent detecting CPU overload
	context := map[string]interface{}{
		"cpu_usage":        95.0,
		"historical_trend": "increasing",
		"forecast_horizon": "5 minutes",
		"mode":             "manual",
		"timestamp":        time.Now().Format(time.RFC3339),
	}

	explanation, _ := xaiEngine.GenerateExplanation(
		"scaling-001",
		"Scaling Agent",
		"scale_up",
		map[string]interface{}{
			"current_replicas": 3,
			"target_replicas":  5,
		},
		map[string]interface{}{
			"status":    "scaled",
			"replicas":  5,
			"timestamp": time.Now().Format(time.RFC3339),
		},
		ManualMode,
		0.85, // 85% confidence for manual mode
		"CPU usage is at 95% and response times are increasing",
		context,
	)

	return explanation
}

// ExampleSelfHealingAgentExplanation demonstrates Chain-of-Thought reasoning for Self-Healing Agent
func ExampleSelfHealingAgentExplanation() *ActionExplanation {
	xaiEngine := NewXAIEngine(GetDefaultLogger(), NewLLMReasoningIntegration())

	// Simulate Self-Healing Agent detecting pod crash
	context := map[string]interface{}{
		"pod_name":          "web-app-123",
		"failure_type":      "crash_loop",
		"restart_count":     5,
		"dependency_health": 0.8,
		"mode":              "auto",
		"timestamp":         time.Now().Format(time.RFC3339),
	}

	explanation, _ := xaiEngine.GenerateExplanation(
		"self-healing-001",
		"Self-Healing Agent",
		"restart_pod",
		map[string]interface{}{
			"pod_name": "web-app-123",
		},
		map[string]interface{}{
			"status":    "restarted",
			"pod_name":  "web-app-123",
			"timestamp": time.Now().Format(time.RFC3339),
		},
		AutoMode,
		0.95, // 95% confidence for auto mode
		"Pod 'web-app-123' is in crash loop",
		context,
	)

	return explanation
}

// GenerateScalingAgentCoTReasoning generates the Chain-of-Thought reasoning for Scaling Agent
// This demonstrates the 5-step process mentioned in the requirements
func GenerateScalingAgentCoTReasoning() []ReasoningStep {
	steps := []ReasoningStep{
		{
			StepNumber:  1,
			Description: "CPU Usage Detection",
			Input: map[string]interface{}{
				"cpu_usage": 95.0,
				"threshold": 85.0,
			},
			Output: map[string]interface{}{
				"alert":     true,
				"severity":  "high",
				"exceeded_by": 10.0,
			},
			Reasoning: "CPU usage exceeds 85% threshold. Current usage is 95%, which is 10% above the threshold.",
		},
		{
			StepNumber:  2,
			Description: "Historical Data Analysis",
			Input: map[string]interface{}{
				"time_window": "last 30 minutes",
			},
			Output: map[string]interface{}{
				"trend":           "increasing",
				"average_cpu":    88.0,
				"peak_cpu":        95.0,
				"sustained_period": "10 minutes",
			},
			Reasoning: "Checked historical data for load trends. CPU usage has been consistently above 85% for the past 10 minutes, with an average of 88% and peak of 95%. The trend shows increasing load.",
		},
		{
			StepNumber:  3,
			Description: "Transformer Forecasting",
			Input: map[string]interface{}{
				"forecast_horizon": "5 minutes",
				"current_metrics": map[string]float64{
					"cpu":    95.0,
					"memory": 80.0,
					"latency": 250.0,
				},
			},
			Output: map[string]interface{}{
				"predicted_cpu":    98.0,
				"predicted_latency": 300.0,
				"risk_level":        "high",
			},
			Reasoning: "Used Transformer forecasting model to predict future demand. The model predicts CPU usage will reach 98% within 5 minutes, and latency will increase to 300ms. This indicates a high risk of service degradation.",
		},
		{
			StepNumber:  4,
			Description: "User Confirmation (Manual Mode)",
			Input: map[string]interface{}{
				"mode":           "manual",
				"options":        []string{"scale_up", "optimize"},
				"recommendation": "scale_up",
			},
			Output: map[string]interface{}{
				"user_choice":    "scale_up",
				"user_approved":   true,
				"selected_option": "scale_up",
			},
			Reasoning: "Presented options to user: 'Scale up from 3 to 5 replicas' or 'Optimize existing resources'. User selected 'Scale up' after reviewing the analysis and forecast.",
		},
		{
			StepNumber:  5,
			Description: "Scaling Action Execution",
			Input: map[string]interface{}{
				"action":          "scale_up",
				"current_replicas": 3,
				"target_replicas":  5,
			},
			Output: map[string]interface{}{
				"status":          "success",
				"replicas":        5,
				"execution_time":  "15 seconds",
			},
			Reasoning: "Scaling action executed successfully. Increased replicas from 3 to 5. The system will now distribute the load across more instances, reducing CPU usage per instance.",
		},
		{
			StepNumber:  6,
			Description: "Agent Report",
			Input: map[string]interface{}{
				"action": "scale_up",
			},
			Output: map[string]interface{}{
				"report_generated": true,
				"explanation_sent": true,
			},
			Reasoning: "Generated comprehensive report explaining the scaling decision. The report includes: problem detection (CPU at 95%), historical analysis (sustained high usage), forecast (predicted 98% CPU), user approval, execution (scaled to 5 replicas), and expected outcome (reduced CPU per instance).",
		},
	}

	return steps
}

// PrintScalingAgentExplanation prints a formatted explanation for Scaling Agent
func PrintScalingAgentExplanation() {
	explanation := ExampleScalingAgentExplanation()
	fmt.Println("=== Scaling Agent Explanation ===")
	fmt.Println(explanation.ToHumanReadable())
	fmt.Println("\n=== Chain-of-Thought Reasoning ===")
	for _, step := range explanation.ReasoningChain {
		fmt.Printf("Step %d: %s\n", step.StepNumber, step.Description)
		fmt.Printf("  Input: %v\n", step.Input)
		fmt.Printf("  Output: %v\n", step.Output)
		fmt.Printf("  Reasoning: %s\n\n", step.Reasoning)
	}
}

// PrintSelfHealingAgentExplanation prints a formatted explanation for Self-Healing Agent
func PrintSelfHealingAgentExplanation() {
	explanation := ExampleSelfHealingAgentExplanation()
	fmt.Println("=== Self-Healing Agent Explanation ===")
	fmt.Println(explanation.ToHumanReadable())
	fmt.Println("\n=== Chain-of-Thought Reasoning ===")
	for _, step := range explanation.ReasoningChain {
		fmt.Printf("Step %d: %s\n", step.StepNumber, step.Description)
		fmt.Printf("  Input: %v\n", step.Input)
		fmt.Printf("  Output: %v\n", step.Output)
		fmt.Printf("  Reasoning: %s\n\n", step.Reasoning)
	}
}

