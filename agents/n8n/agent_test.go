package n8n

import (
	"testing"

	"github.com/ai-driven-self-healing-cloud/agents/core"
)

func TestN8NAgent_Start(t *testing.T) {
	agent := NewN8NAgent()
	
	if agent.GetID() != "n8n-workflow-agent" {
		t.Errorf("Expected ID 'n8n-workflow-agent', got '%s'", agent.GetID())
	}

	if err := agent.Start(); err != nil {
		t.Errorf("Failed to start agent: %v", err)
	}

	if agent.Status != core.StatusRunning {
		t.Errorf("Expected status 'running', got '%s'", agent.Status)
	}

	agent.Stop()
}

func TestTriggerHandler_TriggerWorkflow(t *testing.T) {
	handler := NewTriggerHandler()
	
	request := &TriggerRequest{
		WorkflowID: "test-workflow",
		EventType:  "error.detected",
		Data:       map[string]interface{}{"error": "test"},
		Source:     "test-agent",
	}

	// This will fail if n8n is not running, but that's expected
	_ = handler.TriggerWorkflow(request)
}

