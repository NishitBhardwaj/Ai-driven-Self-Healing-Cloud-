package phase6

import (
	"encoding/json"
	"fmt"
	"os"
	"time"

	"github.com/ai-driven-self-healing-cloud/agents/core"
)

// ValidationReport represents the validation test results
type ValidationReport struct {
	Timestamp     time.Time              `json:"timestamp"`
	TestsRun      int                    `json:"tests_run"`
	TestsPassed   int                    `json:"tests_passed"`
	TestsFailed   int                    `json:"tests_failed"`
	TestResults   []TestResult           `json:"test_results"`
	Components    ComponentValidation    `json:"components"`
	Recommendations []string             `json:"recommendations"`
}

// TestResult represents a single test result
type TestResult struct {
	Name        string    `json:"name"`
	Status      string    `json:"status"` // "passed" or "failed"
	Message     string    `json:"message"`
	Duration    time.Duration `json:"duration"`
	Timestamp   time.Time `json:"timestamp"`
}

// ComponentValidation validates each component
type ComponentValidation struct {
	AutoMode           bool     `json:"auto_mode"`
	ManualMode         bool     `json:"manual_mode"`
	Explainability     bool     `json:"explainability"`
	Logging            bool     `json:"logging"`
	UI                 bool     `json:"ui"`
	LLMIntegration     bool     `json:"llm_integration"`
	Issues             []string `json:"issues"`
}

// GenerateValidationReport generates a comprehensive validation report
func GenerateValidationReport() (*ValidationReport, error) {
	report := &ValidationReport{
		Timestamp:     time.Now(),
		TestResults:   []TestResult{},
		Recommendations: []string{},
		Components: ComponentValidation{
			Issues: []string{},
		},
	}

	// Test Auto Mode
	autoModeResult := validateAutoMode()
	report.TestResults = append(report.TestResults, autoModeResult)
	if autoModeResult.Status == "passed" {
		report.Components.AutoMode = true
		report.TestsPassed++
	} else {
		report.Components.Issues = append(report.Components.Issues, "Auto Mode validation failed")
		report.TestsFailed++
	}
	report.TestsRun++

	// Test Manual Mode
	manualModeResult := validateManualMode()
	report.TestResults = append(report.TestResults, manualModeResult)
	if manualModeResult.Status == "passed" {
		report.Components.ManualMode = true
		report.TestsPassed++
	} else {
		report.Components.Issues = append(report.Components.Issues, "Manual Mode validation failed")
		report.TestsFailed++
	}
	report.TestsRun++

	// Test Explainability
	explainabilityResult := validateExplainability()
	report.TestResults = append(report.TestResults, explainabilityResult)
	if explainabilityResult.Status == "passed" {
		report.Components.Explainability = true
		report.TestsPassed++
	} else {
		report.Components.Issues = append(report.Components.Issues, "Explainability validation failed")
		report.TestsFailed++
	}
	report.TestsRun++

	// Test Logging
	loggingResult := validateLogging()
	report.TestResults = append(report.TestResults, loggingResult)
	if loggingResult.Status == "passed" {
		report.Components.Logging = true
		report.TestsPassed++
	} else {
		report.Components.Issues = append(report.Components.Issues, "Logging validation failed")
		report.TestsFailed++
	}
	report.TestsRun++

	// Test UI
	uiResult := validateUI()
	report.TestResults = append(report.TestResults, uiResult)
	if uiResult.Status == "passed" {
		report.Components.UI = true
		report.TestsPassed++
	} else {
		report.Components.Issues = append(report.Components.Issues, "UI validation failed")
		report.TestsFailed++
	}
	report.TestsRun++

	// Test LLM Integration
	llmResult := validateLLMIntegration()
	report.TestResults = append(report.TestResults, llmResult)
	if llmResult.Status == "passed" {
		report.Components.LLMIntegration = true
		report.TestsPassed++
	} else {
		report.Components.Issues = append(report.Components.Issues, "LLM Integration validation failed")
		report.TestsFailed++
	}
	report.TestsRun++

	// Generate recommendations
	report.generateRecommendations()

	return report, nil
}

// validateAutoMode validates Auto Mode functionality
func validateAutoMode() TestResult {
	start := time.Now()
	
	handler := core.NewDecisionHandler(core.AutoMode)
	decision := handler.CreateDecision(
		"test-agent",
		"Test Agent",
		"Test problem",
		"Test reasoning",
		[]core.ActionOption{
			{ID: "test_action", Description: "Test Action", Reasoning: "Test", Risk: "low", Impact: "medium"},
		},
	)

	passed := decision.Mode == core.AutoMode
	duration := time.Since(start)

	return TestResult{
		Name:      "Auto Mode Validation",
		Status:    getStatus(passed),
		Message:   getMessage(passed, "Auto Mode correctly configured"),
		Duration:  duration,
		Timestamp: time.Now(),
	}
}

// validateManualMode validates Manual Mode functionality
func validateManualMode() TestResult {
	start := time.Now()
	
	handler := core.NewDecisionHandler(core.ManualMode)
	decision := handler.CreateDecision(
		"test-agent",
		"Test Agent",
		"Test problem",
		"Test reasoning",
		[]core.ActionOption{
			{ID: "test_action", Description: "Test Action", Reasoning: "Test", Risk: "low", Impact: "medium"},
		},
	)

	passed := decision.Mode == core.ManualMode && len(decision.Options) > 0
	duration := time.Since(start)

	return TestResult{
		Name:      "Manual Mode Validation",
		Status:    getStatus(passed),
		Message:   getMessage(passed, "Manual Mode correctly configured with options"),
		Duration:  duration,
		Timestamp: time.Now(),
	}
}

// validateExplainability validates explainability functionality
func validateExplainability() TestResult {
	start := time.Now()
	
	logger := core.NewConsoleLogger()
	llmReasoning := core.NewLLMReasoningIntegration()
	xaiEngine := core.NewXAIEngine(logger, llmReasoning)

	explanation, err := xaiEngine.GenerateExplanation(
		"test-agent",
		"Test Agent",
		"test_action",
		nil,
		nil,
		core.AutoMode,
		0.95,
		"Test problem",
		nil,
	)

	passed := err == nil && explanation != nil && explanation.Reasoning != "" && len(explanation.ReasoningChain) > 0
	duration := time.Since(start)

	return TestResult{
		Name:      "Explainability Validation",
		Status:    getStatus(passed),
		Message:   getMessage(passed, "Explainability generates human-readable explanations with reasoning chain"),
		Duration:  duration,
		Timestamp: time.Now(),
	}
}

// validateLogging validates logging functionality
func validateLogging() TestResult {
	start := time.Now()
	
	logger := core.GetDefaultLogger()
	explanation := &core.ActionExplanation{
		AgentID:        "test-agent",
		AgentName:      "Test Agent",
		ActionTaken:    "test_action",
		Reasoning:      "Test reasoning",
		ConfidenceLevel: 0.95,
		Mode:           core.AutoMode,
		Timestamp:      time.Now(),
	}

	err := logger.LogExplanation(explanation)
	passed := err == nil
	duration := time.Since(start)

	return TestResult{
		Name:      "Logging Validation",
		Status:    getStatus(passed),
		Message:   getMessage(passed, "Logging successfully records explanations"),
		Duration:  duration,
		Timestamp: time.Now(),
	}
}

// validateUI validates UI components
func validateUI() TestResult {
	start := time.Now()
	
	// Check if UI files exist
	files := []string{
		"ui/decision-ui/index.html",
		"ui/decision-ui/decision-ui.js",
		"ui/decision-ui/decision-api.js",
		"ui/decision-ui/styles.css",
	}

	allExist := true
	for _, file := range files {
		if _, err := os.Stat(file); os.IsNotExist(err) {
			allExist = false
			break
		}
	}

	passed := allExist
	duration := time.Since(start)

	return TestResult{
		Name:      "UI Validation",
		Status:    getStatus(passed),
		Message:   getMessage(passed, "All UI files exist and are accessible"),
		Duration:  duration,
		Timestamp: time.Now(),
	}
}

// validateLLMIntegration validates LLM integration
func validateLLMIntegration() TestResult {
	start := time.Now()
	
	llmReasoning := core.NewLLMReasoningIntegration()
	reasoningChain, err := llmReasoning.GenerateChainOfThought(
		"test-agent",
		"test_action",
		"Test problem",
		nil,
	)

	passed := err == nil && len(reasoningChain) > 0
	duration := time.Since(start)

	return TestResult{
		Name:      "LLM Integration Validation",
		Status:    getStatus(passed),
		Message:   getMessage(passed, "LLM integration generates reasoning chains"),
		Duration:  duration,
		Timestamp: time.Now(),
	}
}

// generateRecommendations generates recommendations based on validation results
func (r *ValidationReport) generateRecommendations() {
	if !r.Components.AutoMode {
		r.Recommendations = append(r.Recommendations, "Review Auto Mode implementation")
	}
	if !r.Components.ManualMode {
		r.Recommendations = append(r.Recommendations, "Review Manual Mode implementation")
	}
	if !r.Components.Explainability {
		r.Recommendations = append(r.Recommendations, "Ensure all agents implement ExplainAction method")
	}
	if !r.Components.Logging {
		r.Recommendations = append(r.Recommendations, "Set up ELK Stack or verify file logging")
	}
	if !r.Components.UI {
		r.Recommendations = append(r.Recommendations, "Verify UI files are in correct location")
	}
	if !r.Components.LLMIntegration {
		r.Recommendations = append(r.Recommendations, "Verify LLM service is accessible")
	}

	if len(r.Recommendations) == 0 {
		r.Recommendations = append(r.Recommendations, "All components validated successfully!")
	}
}

// Helper functions
func getStatus(passed bool) string {
	if passed {
		return "passed"
	}
	return "failed"
}

func getMessage(passed bool, successMsg string) string {
	if passed {
		return successMsg
	}
	return "Validation failed"
}

// ToJSON converts report to JSON
func (r *ValidationReport) ToJSON() ([]byte, error) {
	return json.MarshalIndent(r, "", "  ")
}

// ToHumanReadable converts report to human-readable text
func (r *ValidationReport) ToHumanReadable() string {
	text := "========================================\n"
	text += "Phase 6 Validation Report\n"
	text += "========================================\n\n"
	text += fmt.Sprintf("Timestamp: %s\n", r.Timestamp.Format(time.RFC3339))
	text += fmt.Sprintf("Tests Run: %d\n", r.TestsRun)
	text += fmt.Sprintf("Tests Passed: %d\n", r.TestsPassed)
	text += fmt.Sprintf("Tests Failed: %d\n\n", r.TestsFailed)

	text += "Component Validation:\n"
	text += fmt.Sprintf("  Auto Mode: %v\n", r.Components.AutoMode)
	text += fmt.Sprintf("  Manual Mode: %v\n", r.Components.ManualMode)
	text += fmt.Sprintf("  Explainability: %v\n", r.Components.Explainability)
	text += fmt.Sprintf("  Logging: %v\n", r.Components.Logging)
	text += fmt.Sprintf("  UI: %v\n", r.Components.UI)
	text += fmt.Sprintf("  LLM Integration: %v\n\n", r.Components.LLMIntegration)

	text += "Test Results:\n"
	for _, result := range r.TestResults {
		status := "✓"
		if result.Status == "failed" {
			status = "✗"
		}
		text += fmt.Sprintf("  %s %s: %s (Duration: %v)\n", status, result.Name, result.Message, result.Duration)
	}

	if len(r.Components.Issues) > 0 {
		text += "\nIssues Found:\n"
		for _, issue := range r.Components.Issues {
			text += fmt.Sprintf("  - %s\n", issue)
		}
	}

	if len(r.Recommendations) > 0 {
		text += "\nRecommendations:\n"
		for _, rec := range r.Recommendations {
			text += fmt.Sprintf("  - %s\n", rec)
		}
	}

	return text
}

// SaveReport saves the report to a file
func (r *ValidationReport) SaveReport(filename string) error {
	jsonData, err := r.ToJSON()
	if err != nil {
		return err
	}

	return os.WriteFile(filename, jsonData, 0644)
}

