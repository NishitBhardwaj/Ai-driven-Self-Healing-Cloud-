package tasksolving

import (
	"testing"
	"time"

	"github.com/ai-driven-self-healing-cloud/agents/core"
)

func TestTaskSolvingAgent_Start(t *testing.T) {
	agent := NewTaskSolvingAgent()
	
	if agent.GetID() != "task-solving-agent" {
		t.Errorf("Expected ID 'task-solving-agent', got '%s'", agent.GetID())
	}

	if err := agent.Start(); err != nil {
		t.Errorf("Failed to start agent: %v", err)
	}

	if agent.Status != core.StatusRunning {
		t.Errorf("Expected status 'running', got '%s'", agent.Status)
	}

	// Cleanup
	agent.Stop()
}

func TestTaskSolvingAgent_HealthCheck(t *testing.T) {
	agent := NewTaskSolvingAgent()
	agent.Start()
	defer agent.Stop()

	health := agent.HealthCheck()
	if !health.Healthy {
		t.Error("Agent should be healthy when running")
	}
}

func TestTaskSolvingAgent_ProcessTask(t *testing.T) {
	agent := NewTaskSolvingAgent()
	agent.Start()
	defer agent.Stop()

	task := &Task{
		ID:          "test-task-1",
		Description: "Test task description",
		Priority:    "high",
	}

	result, err := agent.ProcessTask(task)
	if err != nil {
		t.Errorf("Failed to process task: %v", err)
	}

	if result.TaskID != task.ID {
		t.Errorf("Expected task ID '%s', got '%s'", task.ID, result.TaskID)
	}
}

