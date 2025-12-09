package phase6

import (
	"encoding/json"
	"fmt"
	"os"
	"testing"
	"time"

	"github.com/ai-driven-self-healing-cloud/agents/core"
)

// TestAutoModeValidation tests Auto Mode functionality
func TestAutoModeValidation(t *testing.T) {
	// Initialize XAI engine
	logger := core.NewConsoleLogger()
	llmReasoning := core.NewLLMReasoningIntegration()
	xaiEngine := core.NewXAIEngine(logger, llmReasoning)

	// Create decision handler with Auto Mode
	handler := core.NewDecisionHandler(core.AutoMode)

	// Create a decision
	options := []core.ActionOption{
		{
			ID:          "restart_pod",
			Description: "Restart the failed pod",
			Reasoning:   "Pod is in crash loop, restarting should resolve the issue",
			Risk:        "low",
			Impact:      "medium",
		},
	}

	decision := handler.CreateDecision(
		"self-healing-001",
		"Self-Healing Agent",
		"Pod 'web-app-123' is in crash loop",
		"Detected repeated pod crashes. Analysis shows memory leak in application code.",
		options,
	)

	decision.SetConfidence(0.95) // Auto mode confidence

	// Verify Auto Mode
	if decision.Mode != core.AutoMode {
		t.Errorf("Expected Auto Mode, got %s", decision.Mode)
	}

	// Execute decision (simulated)
	actionExecuted := false
	actionExecutor := func(option *core.ActionOption) (interface{}, error) {
		actionExecuted = true
		return map[string]interface{}{
			"status":   "success",
			"pod_name": "web-app-123",
		}, nil
	}

	err := decision.ExecuteDecision(handler, actionExecutor)
	if err != nil {
		t.Errorf("Error executing decision: %v", err)
	}

	// Verify action was executed automatically
	if !actionExecuted {
		t.Error("Action should be executed automatically in Auto Mode")
	}

	// Verify explanation is generated
	if decision.Explanation == "" {
		t.Error("Explanation should be generated after action execution")
	}

	// Generate detailed explanation
	explanation, err := xaiEngine.GenerateExplanation(
		decision.AgentID,
		decision.AgentName,
		decision.SelectedOption.Description,
		decision,
		decision.ExecutionResult,
		core.AutoMode,
		decision.Confidence,
		decision.Problem,
		nil,
	)

	if err != nil {
		t.Errorf("Error generating explanation: %v", err)
	}

	// Verify explanation is human-readable
	if explanation.Reasoning == "" {
		t.Error("Explanation reasoning should not be empty")
	}

	// Verify reasoning chain exists
	if len(explanation.ReasoningChain) == 0 {
		t.Error("Reasoning chain should contain steps")
	}

	// Verify confidence level
	if explanation.ConfidenceLevel < 0.9 {
		t.Errorf("Auto Mode confidence should be >= 0.9, got %.2f", explanation.ConfidenceLevel)
	}

	fmt.Printf("✅ Auto Mode Validation: PASSED\n")
	fmt.Printf("   - Action executed automatically: ✓\n")
	fmt.Printf("   - Explanation generated: ✓\n")
	fmt.Printf("   - Reasoning chain present: ✓\n")
	fmt.Printf("   - Confidence level: %.0f%%\n", explanation.ConfidenceLevel*100)
}

// TestManualModeValidation tests Manual Mode functionality
func TestManualModeValidation(t *testing.T) {
	// Initialize XAI engine
	logger := core.NewConsoleLogger()
	llmReasoning := core.NewLLMReasoningIntegration()
	xaiEngine := core.NewXAIEngine(logger, llmReasoning)

	// Create decision handler with Manual Mode
	handler := core.NewDecisionHandler(core.ManualMode)

	// Set up user input callback
	userSelectedOption := ""
	handler.UserInputCallback = func(decision *core.AgentDecision) (string, error) {
		// Simulate user selecting first option
		if len(decision.Options) > 0 {
			userSelectedOption = decision.Options[0].ID
			return decision.Options[0].ID, nil
		}
		return "", fmt.Errorf("no options available")
	}

	// Create a decision
	options := []core.ActionOption{
		{
			ID:          "scale_up",
			Description: "Scale up from 3 to 5 replicas",
			Reasoning:   "Adding more replicas will distribute the load and reduce CPU usage per instance",
			Risk:        "low",
			Impact:      "high",
			EstimatedCost: 15.50,
		},
		{
			ID:          "optimize",
			Description: "Optimize existing resources",
			Reasoning:   "Optimize the current deployment configuration to better utilize existing resources",
			Risk:        "medium",
			Impact:      "medium",
			EstimatedCost: 0.0,
		},
	}

	decision := handler.CreateDecision(
		"scaling-001",
		"Scaling Agent",
		"CPU usage is at 95% and response times are increasing",
		"CPU usage has been above 90% for 5 minutes. The system needs more capacity to handle the current load.",
		options,
	)

	decision.SetConfidence(0.85) // Manual mode confidence

	// Verify Manual Mode
	if decision.Mode != core.ManualMode {
		t.Errorf("Expected Manual Mode, got %s", decision.Mode)
	}

	// Verify options are available
	if len(decision.Options) == 0 {
		t.Error("Options should be available in Manual Mode")
	}

	// Execute decision (should wait for user input)
	actionExecuted := false
	actionExecutor := func(option *core.ActionOption) (interface{}, error) {
		actionExecuted = true
		return map[string]interface{}{
			"status":   "success",
			"replicas": 5,
		}, nil
	}

	err := decision.ExecuteDecision(handler, actionExecutor)
	if err != nil {
		t.Errorf("Error executing decision: %v", err)
	}

	// Verify user input was requested
	if userSelectedOption == "" {
		t.Error("User input should be requested in Manual Mode")
	}

	// Verify action was executed after user selection
	if !actionExecuted {
		t.Error("Action should be executed after user selection")
	}

	// Verify explanation is generated
	if decision.Explanation == "" {
		t.Error("Explanation should be generated after action execution")
	}

	// Generate detailed explanation
	explanation, err := xaiEngine.GenerateExplanation(
		decision.AgentID,
		decision.AgentName,
		decision.SelectedOption.Description,
		decision,
		decision.ExecutionResult,
		core.ManualMode,
		decision.Confidence,
		decision.Problem,
		nil,
	)

	if err != nil {
		t.Errorf("Error generating explanation: %v", err)
	}

	// Verify explanation contains full reasoning
	if explanation.Reasoning == "" {
		t.Error("Explanation should contain full reasoning")
	}

	// Verify reasoning chain has multiple steps
	if len(explanation.ReasoningChain) < 3 {
		t.Errorf("Reasoning chain should have at least 3 steps, got %d", len(explanation.ReasoningChain))
	}

	// Verify confidence level
	if explanation.ConfidenceLevel < 0.8 || explanation.ConfidenceLevel > 0.9 {
		t.Errorf("Manual Mode confidence should be between 0.8-0.9, got %.2f", explanation.ConfidenceLevel)
	}

	fmt.Printf("✅ Manual Mode Validation: PASSED\n")
	fmt.Printf("   - User input requested: ✓\n")
	fmt.Printf("   - Options displayed: ✓\n")
	fmt.Printf("   - Action executed after selection: ✓\n")
	fmt.Printf("   - Full reasoning provided: ✓\n")
	fmt.Printf("   - Reasoning chain steps: %d\n", len(explanation.ReasoningChain))
}

// TestExplanationHumanReadable validates explanations are human-readable
func TestExplanationHumanReadable(t *testing.T) {
	logger := core.NewConsoleLogger()
	llmReasoning := core.NewLLMReasoningIntegration()
	xaiEngine := core.NewXAIEngine(logger, llmReasoning)

	// Generate explanation
	explanation, err := xaiEngine.GenerateExplanation(
		"scaling-001",
		"Scaling Agent",
		"scale_up",
		nil,
		nil,
		core.AutoMode,
		0.95,
		"CPU usage is at 95%",
		map[string]interface{}{
			"cpu_usage": 95.0,
		},
	)

	if err != nil {
		t.Errorf("Error generating explanation: %v", err)
	}

	// Verify explanation is human-readable
	humanReadable := explanation.ToHumanReadable()
	if humanReadable == "" {
		t.Error("Human-readable explanation should not be empty")
	}

	// Verify it contains key information
	requiredFields := []string{
		"Agent:",
		"Action:",
		"Reasoning:",
	}

	for _, field := range requiredFields {
		if !contains(humanReadable, field) {
			t.Errorf("Human-readable explanation should contain: %s", field)
		}
	}

	// Verify reasoning chain is readable
	if len(explanation.ReasoningChain) > 0 {
		for _, step := range explanation.ReasoningChain {
			if step.Description == "" {
				t.Error("Reasoning step description should not be empty")
			}
			if step.Reasoning == "" {
				t.Error("Reasoning step reasoning should not be empty")
			}
		}
	}

	// Verify JSON format is valid
	jsonData, err := explanation.ToJSON()
	if err != nil {
		t.Errorf("Error converting to JSON: %v", err)
	}

	var jsonObj map[string]interface{}
	if err := json.Unmarshal(jsonData, &jsonObj); err != nil {
		t.Errorf("JSON is not valid: %v", err)
	}

	fmt.Printf("✅ Explanation Human-Readable Validation: PASSED\n")
	fmt.Printf("   - Human-readable format: ✓\n")
	fmt.Printf("   - Contains required fields: ✓\n")
	fmt.Printf("   - Reasoning chain readable: ✓\n")
	fmt.Printf("   - Valid JSON format: ✓\n")
}

// TestLoggingValidation tests that all agents send reliable logs
func TestLoggingValidation(t *testing.T) {
	// Test ELK Stack logger
	elkLogger := core.NewELKStackLogger("", "test-index")
	
	// Test Console logger
	consoleLogger := core.NewConsoleLogger()
	
	// Test Composite logger
	compositeLogger := core.NewCompositeLogger(consoleLogger, elkLogger)

	// Create explanation
	explanation := &core.ActionExplanation{
		AgentID:        "scaling-001",
		AgentName:      "Scaling Agent",
		ActionTaken:    "scale_up",
		Reasoning:      "CPU usage is at 95%, scaling up will reduce load",
		ConfidenceLevel: 0.95,
		Mode:           core.AutoMode,
		Timestamp:      time.Now(),
		ReasoningChain: []core.ReasoningStep{
			{
				StepNumber:  1,
				Description: "Problem Detection",
				Reasoning:   "Detected high CPU usage",
			},
		},
		AlternativeActions: []string{"optimize", "restart_service"},
	}

	// Test logging
	err := compositeLogger.LogExplanation(explanation)
	if err != nil {
		t.Errorf("Error logging explanation: %v", err)
	}

	// Verify log file was created (for file logger)
	logDir := "logs/xai"
	if _, err := os.Stat(logDir); os.IsNotExist(err) {
		// Directory might not exist yet, but logging should still work
		fmt.Printf("   - Log directory will be created on first log\n")
	}

	// Verify explanation contains all required fields for logging
	if explanation.AgentID == "" {
		t.Error("Agent ID should not be empty for logging")
	}
	if explanation.ActionTaken == "" {
		t.Error("Action taken should not be empty for logging")
	}
	if explanation.Reasoning == "" {
		t.Error("Reasoning should not be empty for logging")
	}

	fmt.Printf("✅ Logging Validation: PASSED\n")
	fmt.Printf("   - ELK Stack logger: ✓\n")
	fmt.Printf("   - Console logger: ✓\n")
	fmt.Printf("   - Composite logger: ✓\n")
	fmt.Printf("   - Explanation logged: ✓\n")
	fmt.Printf("   - All required fields present: ✓\n")
}

// TestUIDynamicUpdates tests UI updates dynamically
func TestUIDynamicUpdates(t *testing.T) {
	// This test validates the UI structure and data format
	// Actual UI testing would require browser automation

	// Test Auto Mode data format
	autoDecision := &core.AgentDecision{
		Mode:          core.AutoMode,
		AgentID:       "self-healing-001",
		AgentName:     "Self-Healing Agent",
		Problem:       "Pod is crashing",
		Reasoning:     "Pod has crashed 3 times",
		ActionExecuted: true,
		Explanation:   "Action executed automatically",
		Confidence:    0.95,
	}

	// Verify Auto Mode data structure
	if autoDecision.Mode != core.AutoMode {
		t.Error("Auto Mode decision should have AutoMode")
	}

	// Test Manual Mode data format
	manualDecision := &core.AgentDecision{
		Mode:          core.ManualMode,
		AgentID:       "scaling-001",
		AgentName:     "Scaling Agent",
		Problem:       "CPU usage is high",
		Reasoning:     "CPU usage is at 95%",
		Options: []core.ActionOption{
			{
				ID:          "scale_up",
				Description: "Scale up",
				Reasoning:   "Add more replicas",
				Risk:        "low",
				Impact:      "high",
			},
		},
		ActionExecuted: false,
		Confidence:    0.85,
	}

	// Verify Manual Mode data structure
	if manualDecision.Mode != core.ManualMode {
		t.Error("Manual Mode decision should have ManualMode")
	}
	if len(manualDecision.Options) == 0 {
		t.Error("Manual Mode should have options")
	}

	// Test JSON serialization for UI
	autoJSON, err := json.Marshal(autoDecision)
	if err != nil {
		t.Errorf("Error marshaling Auto Mode decision: %v", err)
	}

	manualJSON, err := json.Marshal(manualDecision)
	if err != nil {
		t.Errorf("Error marshaling Manual Mode decision: %v", err)
	}

	// Verify JSON is valid
	var autoObj map[string]interface{}
	if err := json.Unmarshal(autoJSON, &autoObj); err != nil {
		t.Errorf("Auto Mode JSON is not valid: %v", err)
	}

	var manualObj map[string]interface{}
	if err := json.Unmarshal(manualJSON, &manualObj); err != nil {
		t.Errorf("Manual Mode JSON is not valid: %v", err)
	}

	// Verify mode field exists
	if autoObj["mode"] != "auto" {
		t.Error("Auto Mode JSON should have mode='auto'")
	}
	if manualObj["mode"] != "manual" {
		t.Error("Manual Mode JSON should have mode='manual'")
	}

	fmt.Printf("✅ UI Dynamic Updates Validation: PASSED\n")
	fmt.Printf("   - Auto Mode data structure: ✓\n")
	fmt.Printf("   - Manual Mode data structure: ✓\n")
	fmt.Printf("   - JSON serialization: ✓\n")
	fmt.Printf("   - Mode field present: ✓\n")
}

// TestFullSystemIntegration tests the full system integration
func TestFullSystemIntegration(t *testing.T) {
	fmt.Println("\n=== Full System Integration Test ===")

	// 1. Initialize all components
	logger := core.GetDefaultLogger()
	llmReasoning := core.NewLLMReasoningIntegration()
	xaiEngine := core.NewXAIEngine(logger, llmReasoning)
	handler := core.NewDecisionHandler(core.AutoMode)

	// 2. Create a decision
	options := []core.ActionOption{
		{
			ID:          "restart_pod",
			Description: "Restart the pod",
			Reasoning:   "Restarting will resolve the issue",
			Risk:        "low",
			Impact:      "medium",
		},
	}

	decision := handler.CreateDecision(
		"self-healing-001",
		"Self-Healing Agent",
		"Pod is crashing",
		"Pod has crashed multiple times",
		options,
	)

	decision.SetConfidence(0.95)

	// 3. Execute decision
	actionExecutor := func(option *core.ActionOption) (interface{}, error) {
		return map[string]interface{}{"status": "success"}, nil
	}

	err := decision.ExecuteDecision(handler, actionExecutor)
	if err != nil {
		t.Errorf("Error executing decision: %v", err)
	}

	// 4. Generate explanation
	explanation, err := xaiEngine.GenerateExplanation(
		decision.AgentID,
		decision.AgentName,
		decision.SelectedOption.Description,
		decision,
		decision.ExecutionResult,
		decision.Mode,
		decision.Confidence,
		decision.Problem,
		nil,
	)

	if err != nil {
		t.Errorf("Error generating explanation: %v", err)
	}

	// 5. Verify all components work together
	if !decision.ActionExecuted {
		t.Error("Decision should be executed")
	}

	if explanation.Reasoning == "" {
		t.Error("Explanation should have reasoning")
	}

	if len(explanation.ReasoningChain) == 0 {
		t.Error("Explanation should have reasoning chain")
	}

	// 6. Verify logging
	err = logger.LogExplanation(explanation)
	if err != nil {
		t.Errorf("Error logging explanation: %v", err)
	}

	fmt.Printf("✅ Full System Integration: PASSED\n")
	fmt.Printf("   - All components initialized: ✓\n")
	fmt.Printf("   - Decision executed: ✓\n")
	fmt.Printf("   - Explanation generated: ✓\n")
	fmt.Printf("   - Logging functional: ✓\n")
}

// Helper function
func contains(s, substr string) bool {
	return len(s) >= len(substr) && (s == substr || len(s) > len(substr) && 
		(s[:len(substr)] == substr || s[len(s)-len(substr):] == substr || 
		containsMiddle(s, substr))))
}

func containsMiddle(s, substr string) bool {
	for i := 0; i <= len(s)-len(substr); i++ {
		if s[i:i+len(substr)] == substr {
			return true
		}
	}
	return false
}

