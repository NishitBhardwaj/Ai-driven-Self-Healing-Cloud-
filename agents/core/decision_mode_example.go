package core

import (
	"fmt"
	"time"
)

// ExampleUsage demonstrates how to use the decision mode system
func ExampleUsage() {
	// 1. Create a decision handler with default mode
	handler := NewDecisionHandler(AutoMode)

	// 2. Set up callbacks for user interaction and notifications
	handler.UserInputCallback = func(decision *AgentDecision) (string, error) {
		// In a real implementation, this would prompt the user via UI/API
		fmt.Println("User input requested for decision:", decision.Problem)
		fmt.Println("Options:")
		for i, opt := range decision.Options {
			fmt.Printf("  [%d] %s\n", i+1, opt.Description)
		}
		// Simulate user selecting first option
		return decision.Options[0].ID, nil
	}

	handler.NotificationCallback = func(decision *AgentDecision) error {
		// In a real implementation, this would send notification via email/Slack/etc.
		fmt.Printf("Notification: %s executed action: %s\n", decision.AgentName, decision.SelectedOption.Description)
		return nil
	}

	// 3. Create a decision
	options := []ActionOption{
		{
			ID:          "restart_pod",
			Description: "Restart the failed pod",
			Reasoning:   "Pod is in crash loop, restarting should resolve the issue",
			Risk:        "low",
			Impact:      "medium",
			EstimatedCost: 0.0,
		},
		{
			ID:          "rebuild_deployment",
			Description: "Rebuild the entire deployment",
			Reasoning:   "More thorough fix but takes longer",
			Risk:        "medium",
			Impact:      "high",
			EstimatedCost: 10.0,
		},
	}

	decision := handler.CreateDecision(
		"self-healing-001",
		"Self-Healing Agent",
		"Pod 'web-app-123' is in crash loop",
		"Detected repeated pod crashes. Analysis shows memory leak in application code.",
		options,
	)

	// 4. Set confidence
	decision.SetConfidence(0.85)

	// 5. Define action executor
	actionExecutor := func(option *ActionOption) (interface{}, error) {
		// In a real implementation, this would execute the actual action
		fmt.Printf("Executing action: %s\n", option.Description)
		time.Sleep(100 * time.Millisecond) // Simulate action execution
		return map[string]interface{}{
			"status":    "success",
			"pod_name":  "web-app-123",
			"action":    option.ID,
			"timestamp": time.Now().Format(time.RFC3339),
		}, nil
	}

	// 6. Execute the decision
	err := decision.ExecuteDecision(handler, actionExecutor)
	if err != nil {
		fmt.Printf("Error executing decision: %v\n", err)
		return
	}

	// 7. Generate explanation
	explainEngine := NewExplainabilityEngine()
	explanation := explainEngine.GenerateExplanation(decision, DetailedExplanation)

	// 8. Display explanation
	fmt.Println("\n=== Decision Explanation ===")
	fmt.Println(explanation.ToHumanReadable())

	// 9. Display JSON (for API responses)
	jsonData, _ := explanation.ToJSON()
	fmt.Println("\n=== JSON Format ===")
	fmt.Println(string(jsonData))
}

// ExampleAutoMode demonstrates Auto Mode usage
func ExampleAutoMode() {
	handler := NewDecisionHandler(AutoMode)

	decision := handler.CreateDecision(
		"scaling-001",
		"Scaling Agent",
		"CPU usage is at 95%",
		"CPU usage has been above 90% for 5 minutes. Scaling up will improve performance.",
		[]ActionOption{
			{
				ID:          "scale_up",
				Description: "Scale up from 3 to 5 replicas",
				Reasoning:   "Current load requires more capacity",
				Risk:        "low",
				Impact:      "high",
			},
		},
	)

	decision.SetConfidence(0.9)

	actionExecutor := func(option *ActionOption) (interface{}, error) {
		fmt.Printf("[AUTO] Executing: %s\n", option.Description)
		return map[string]string{"status": "scaled", "replicas": "5"}, nil
	}

	err := decision.ExecuteDecision(handler, actionExecutor)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
	}
}

// ExampleManualMode demonstrates Manual Mode usage
func ExampleManualMode() {
	handler := NewDecisionHandler(ManualMode)

	// Set up user input callback
	handler.UserInputCallback = func(decision *AgentDecision) (string, error) {
		fmt.Println("\n=== Manual Approval Required ===")
		fmt.Printf("Problem: %s\n", decision.Problem)
		fmt.Printf("Reasoning: %s\n\n", decision.Reasoning)
		fmt.Println("Available actions:")
		for i, opt := range decision.Options {
			fmt.Printf("  [%d] %s (Risk: %s, Impact: %s)\n", i+1, opt.Description, opt.Risk, opt.Impact)
		}
		fmt.Print("\nSelect action (1-", len(decision.Options), "): ")

		// In real implementation, read from stdin/API
		// For example, return first option
		return decision.Options[0].ID, nil
	}

	decision := handler.CreateDecision(
		"security-001",
		"Security Agent",
		"Suspicious activity detected",
		"Multiple failed login attempts from unknown IP address",
		[]ActionOption{
			{
				ID:          "block_ip",
				Description: "Block the suspicious IP address",
				Reasoning:   "Prevent further attack attempts",
				Risk:        "low",
				Impact:      "high",
			},
			{
				ID:          "investigate",
				Description: "Investigate further before taking action",
				Reasoning:   "Gather more information before blocking",
				Risk:        "medium",
				Impact:      "low",
			},
		},
	)

	actionExecutor := func(option *ActionOption) (interface{}, error) {
		fmt.Printf("[MANUAL] Executing user-selected action: %s\n", option.Description)
		return map[string]string{"status": "executed"}, nil
	}

	err := decision.ExecuteDecision(handler, actionExecutor)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
	}
}

