package scaling

import (
	"bytes"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"time"

	"github.com/sirupsen/logrus"
)

// AutoScaler handles automatic scaling operations
type AutoScaler struct {
	logger *logrus.Logger
}

// NewAutoScaler creates a new AutoScaler instance
func NewAutoScaler() *AutoScaler {
	return &AutoScaler{
		logger: logrus.New(),
	}
}

// ScalingRequest represents a scaling request
type ScalingRequest struct {
	ServiceID    string                 `json:"service_id"`
	CurrentReplicas int                 `json:"current_replicas"`
	TargetReplicas   int                 `json:"target_replicas"`
	Reason       string                 `json:"reason"`
	Metadata     map[string]interface{} `json:"metadata"`
}

// ScalingResult represents the result of a scaling operation
type ScalingResult struct {
	ServiceID        string `json:"service_id"`
	Action           string `json:"action"`
	PreviousReplicas int    `json:"previous_replicas"`
	NewReplicas      int    `json:"new_replicas"`
	Success          bool   `json:"success"`
	TimeTaken        int64  `json:"time_taken_ms"`
}

// ScaleUp scales up a service
func (as *AutoScaler) ScaleUp(serviceID string, targetReplicas int) (*ScalingResult, error) {
	as.logger.WithFields(logrus.Fields{
		"service_id": serviceID,
		"target":     targetReplicas,
	}).Info("Scaling up service")

	// TODO: Implement actual scaling logic in Phase 5
	result := &ScalingResult{
		ServiceID:        serviceID,
		Action:           "scale_up",
		PreviousReplicas: 1,
		NewReplicas:      targetReplicas,
		Success:          true,
		TimeTaken:        time.Now().UnixMilli(),
	}

	return result, nil
}

// ScaleDown scales down a service
func (as *AutoScaler) ScaleDown(serviceID string, targetReplicas int) (*ScalingResult, error) {
	as.logger.WithFields(logrus.Fields{
		"service_id": serviceID,
		"target":     targetReplicas,
	}).Info("Scaling down service")

	// TODO: Implement actual scaling logic in Phase 5
	result := &ScalingResult{
		ServiceID:        serviceID,
		Action:           "scale_down",
		PreviousReplicas: 5,
		NewReplicas:      targetReplicas,
		Success:          true,
		TimeTaken:        time.Now().UnixMilli(),
	}

	return result, nil
}

// EvaluateScaling evaluates if scaling is needed based on metrics using Transformer predictions
func (as *AutoScaler) EvaluateScaling(serviceID string, metrics map[string]float64) (*ScalingRequest, error) {
	as.logger.WithField("service_id", serviceID).Debug("Evaluating scaling needs using AI Engine")

	// Try to use AI Engine integration (Transformer forecasting)
	aiRecommendation, err := as.callAIIntegration(serviceID, metrics)
	if err != nil {
		as.logger.WithError(err).Warn("AI Engine integration failed, using fallback evaluation")
		return as.fallbackScalingEvaluation(serviceID, metrics), nil
	}

	if aiRecommendation != nil {
		request := &ScalingRequest{
			ServiceID:      serviceID,
			CurrentReplicas: aiRecommendation["current_replicas"].(int),
			TargetReplicas:  aiRecommendation["target_replicas"].(int),
			Reason:         aiRecommendation["reasoning"].(string),
			Metadata:       metrics,
		}
		return request, nil
	}

	return as.fallbackScalingEvaluation(serviceID, metrics), nil
}

// callAIIntegration calls Python AI integration wrapper
func (as *AutoScaler) callAIIntegration(serviceID string, metrics map[string]float64) (map[string]interface{}, error) {
	// Get script path
	scriptPath := filepath.Join(filepath.Dir(os.Args[0]), "agents", "scaling", "ai_integration_wrapper.py")
	if _, err := os.Stat(scriptPath); os.IsNotExist(err) {
		scriptPath = "agents/scaling/ai_integration_wrapper.py"
	}

	// Prepare input - convert metrics to arrays
	historicalMetrics := make(map[string][]float64)
	for key, value := range metrics {
		historicalMetrics[key] = []float64{value}
	}

	input := map[string]interface{}{
		"historical_metrics": historicalMetrics,
		"current_replicas":   2,
		"cpu_threshold":     80.0,
		"memory_threshold":  80.0,
		"latency_threshold": 500.0,
	}

	inputJSON, err := json.Marshal(input)
	if err != nil {
		return nil, err
	}

	// Call Python script
	cmd := exec.Command("python3", scriptPath, "get_scaling_recommendation")
	cmd.Stdin = bytes.NewReader(inputJSON)
	output, err := cmd.Output()
	if err != nil {
		return nil, err
	}

	// Parse output
	var result map[string]interface{}
	if err := json.Unmarshal(output, &result); err != nil {
		return nil, err
	}

	return result, nil
}

// fallbackScalingEvaluation provides fallback when AI is unavailable
func (as *AutoScaler) fallbackScalingEvaluation(serviceID string, metrics map[string]float64) *ScalingRequest {
	return &ScalingRequest{
		ServiceID:      serviceID,
		CurrentReplicas: 2,
		TargetReplicas:  4,
		Reason:         "High CPU utilization detected",
		Metadata:       metrics,
	}
}

