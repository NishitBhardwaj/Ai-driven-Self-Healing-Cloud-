package scaling

import (
	"testing"

	"github.com/ai-driven-self-healing-cloud/agents/core"
)

func TestScalingAgent_Start(t *testing.T) {
	agent := NewScalingAgent()
	
	if agent.GetID() != "scaling-agent" {
		t.Errorf("Expected ID 'scaling-agent', got '%s'", agent.GetID())
	}

	if err := agent.Start(); err != nil {
		t.Errorf("Failed to start agent: %v", err)
	}

	if agent.Status != core.StatusRunning {
		t.Errorf("Expected status 'running', got '%s'", agent.Status)
	}

	agent.Stop()
}

func TestAutoScaler_ScaleUp(t *testing.T) {
	scaler := NewAutoScaler()
	
	result, err := scaler.ScaleUp("test-service", 5)
	if err != nil {
		t.Errorf("Failed to scale up: %v", err)
	}

	if result.Action != "scale_up" {
		t.Errorf("Expected action 'scale_up', got '%s'", result.Action)
	}
}

func TestAutoScaler_ScaleDown(t *testing.T) {
	scaler := NewAutoScaler()
	
	result, err := scaler.ScaleDown("test-service", 2)
	if err != nil {
		t.Errorf("Failed to scale down: %v", err)
	}

	if result.Action != "scale_down" {
		t.Errorf("Expected action 'scale_down', got '%s'", result.Action)
	}
}

