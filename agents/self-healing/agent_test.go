package selfhealing

import (
	"testing"

	"github.com/ai-driven-self-healing-cloud/agents/core"
)

func TestSelfHealingAgent_Start(t *testing.T) {
	agent := NewSelfHealingAgent()
	
	if agent.GetID() != "self-healing-agent" {
		t.Errorf("Expected ID 'self-healing-agent', got '%s'", agent.GetID())
	}

	if err := agent.Start(); err != nil {
		t.Errorf("Failed to start agent: %v", err)
	}

	if agent.Status != core.StatusRunning {
		t.Errorf("Expected status 'running', got '%s'", agent.Status)
	}

	agent.Stop()
}

func TestSelfHealingAgent_HealthCheck(t *testing.T) {
	agent := NewSelfHealingAgent()
	agent.Start()
	defer agent.Stop()

	health := agent.HealthCheck()
	if !health.Healthy {
		t.Error("Agent should be healthy when running")
	}
}

func TestHealer_Heal(t *testing.T) {
	healer := NewHealer()
	
	request := &HealingRequest{
		ServiceID:   "test-service",
		FailureType: "crash",
		Error:       "Service crashed",
	}

	result, err := healer.Heal(request)
	if err != nil {
		t.Errorf("Failed to heal: %v", err)
	}

	if result.ServiceID != request.ServiceID {
		t.Errorf("Expected service ID '%s', got '%s'", request.ServiceID, result.ServiceID)
	}
}

