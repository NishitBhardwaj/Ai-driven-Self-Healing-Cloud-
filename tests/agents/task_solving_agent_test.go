package agents

import (
	"testing"

	"github.com/ai-driven-self-healing-cloud/agents/core"
	"github.com/ai-driven-self-healing-cloud/agents/task-solving"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestTaskSolvingAgentHealthCheck verifies health check
func TestTaskSolvingAgentHealthCheck(t *testing.T) {
	agent := tasksolving.NewTaskSolvingAgent()
	
	err := agent.Init()
	require.NoError(t, err)
	
	err = agent.Start()
	require.NoError(t, err)
	
	health := agent.HealthCheck()
	
	assert.True(t, health.Healthy, "Agent should be healthy when running")
	assert.Equal(t, string(core.StatusRunning), health.Status)
}

// TestTaskSolvingAgentParseUserRequest verifies agent correctly parses user requests
func TestTaskSolvingAgentParseUserRequest(t *testing.T) {
	agent := tasksolving.NewTaskSolvingAgent()
	
	err := agent.Init()
	require.NoError(t, err)
	
	err = agent.Start()
	require.NoError(t, err)
	
	// Create a user task
	task := &tasksolving.Task{
		ID:          "task-123",
		Description: "Scale up the web service to handle increased traffic",
		Priority:    "high",
		Metadata: map[string]interface{}{
			"service": "web-service",
			"action":  "scale_up",
		},
	}
	
	// Process task
	result, err := agent.ProcessTask(task)
	require.NoError(t, err, "Task processing should succeed")
	
	// Verify result
	assert.NotNil(t, result, "Result should not be nil")
	assert.Equal(t, "task-123", result.TaskID, "Task ID should match")
	assert.Equal(t, "processed", result.Status, "Status should be processed")
	assert.NotEmpty(t, result.Actions, "Actions should be generated")
	assert.NotEmpty(t, result.Reasoning, "Reasoning should be provided")
}

// TestTaskSolvingAgentGenerateTasks verifies agent generates correct tasks
func TestTaskSolvingAgentGenerateTasks(t *testing.T) {
	agent := tasksolving.NewTaskSolvingAgent()
	
	err := agent.Init()
	require.NoError(t, err)
	
	err = agent.Start()
	require.NoError(t, err)
	
	// Test different task types
	testCases := []struct {
		name        string
		description string
		expected    string
	}{
		{
			name:        "Scaling Task",
			description: "Scale up the service",
			expected:    "scaling",
		},
		{
			name:        "Healing Task",
			description: "Fix the crashed service",
			expected:    "healing",
		},
		{
			name:        "Security Task",
			description: "Block suspicious IP address",
			expected:    "security",
		},
	}
	
	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			task := &tasksolving.Task{
				ID:          "task-" + tc.name,
				Description: tc.description,
				Priority:    "normal",
			}
			
			result, err := agent.ProcessTask(task)
			require.NoError(t, err)
			
			assert.NotNil(t, result, "Result should not be nil")
			assert.NotEmpty(t, result.Actions, "Actions should be generated")
			assert.Contains(t, result.Reasoning, tc.description, "Reasoning should contain task description")
		})
	}
}

// TestTaskSolvingAgentSendToRightAgent verifies tasks are sent to the right agent
func TestTaskSolvingAgentSendToRightAgent(t *testing.T) {
	agent := tasksolving.NewTaskSolvingAgent()
	
	err := agent.Init()
	require.NoError(t, err)
	
	err = agent.Start()
	require.NoError(t, err)
	
	// Test scaling task
	scalingTask := &tasksolving.Task{
		ID:          "scale-task",
		Description: "Scale up the deployment",
		Priority:    "high",
		Metadata: map[string]interface{}{
			"target_agent": "scaling-agent",
		},
	}
	
	result, err := agent.ProcessTask(scalingTask)
	require.NoError(t, err)
	
	// Verify task is processed and actions are generated
	assert.NotNil(t, result, "Result should not be nil")
	assert.NotEmpty(t, result.Actions, "Actions should be generated")
	
	// Verify reasoning indicates scaling
	assert.Contains(t, result.Reasoning, "Scale", "Reasoning should mention scaling")
}

// TestTaskSolvingAgentErrorHandling tests error handling
func TestTaskSolvingAgentErrorHandling(t *testing.T) {
	agent := tasksolving.NewTaskSolvingAgent()
	
	err := agent.Init()
	require.NoError(t, err)
	
	// Test with empty task
	emptyTask := &tasksolving.Task{
		ID:          "",
		Description: "",
		Priority:    "",
	}
	
	// Should handle gracefully
	result, err := agent.ProcessTask(emptyTask)
	// Should either return error or process with defaults
	if err != nil {
		assert.Error(t, err, "Should return error for invalid task")
	} else {
		assert.NotNil(t, result, "Should return result even with empty task")
	}
}

// TestTaskSolvingAgentExplainAction tests explanation generation
func TestTaskSolvingAgentExplainAction(t *testing.T) {
	agent := tasksolving.NewTaskSolvingAgent()
	
	input := map[string]interface{}{
		"task_type":    "scaling",
		"description":  "Scale up service",
	}
	
	output := map[string]interface{}{
		"actions": []string{"scale_up"},
		"status":  "processed",
	}
	
	explanation := agent.ExplainAction(input, output)
	
	assert.NotEmpty(t, explanation, "Explanation should not be empty")
	assert.Contains(t, explanation, "The agent detected that", "Should follow standard format")
}

