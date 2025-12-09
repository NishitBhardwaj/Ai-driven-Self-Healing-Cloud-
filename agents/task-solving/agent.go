package tasksolving

import (
	"encoding/json"
	"fmt"
	"time"

	"github.com/ai-driven-self-healing-cloud/agents/core"
	"github.com/ai-driven-self-healing-cloud/agents/events"
	"github.com/ai-driven-self-healing-cloud/config"
	"github.com/sirupsen/logrus"
)

// TaskSolvingAgent handles user tasks and converts them into agent actions
type TaskSolvingAgent struct {
	*core.Agent
	logger     *logrus.Logger
	messageBus config.MessageBus
}

// Task represents a user task
type Task struct {
	ID          string                 `json:"id"`
	Description string                 `json:"description"`
	Priority    string                 `json:"priority"`
	Metadata    map[string]interface{} `json:"metadata"`
}

// TaskResult represents the result of processing a task
type TaskResult struct {
	TaskID    string                 `json:"task_id"`
	Status    string                 `json:"status"`
	Actions   []string               `json:"actions"`
	Reasoning string                 `json:"reasoning"`
	Metadata  map[string]interface{} `json:"metadata"`
}

// NewTaskSolvingAgent creates a new Task-Solving Agent instance
func NewTaskSolvingAgent() *TaskSolvingAgent {
	baseAgent := core.NewAgent(
		"task-solving-agent",
		"Task-Solving Agent",
		"Parses user tasks, converts them into agent actions, and uses LLM to interpret intent",
	)

	return &TaskSolvingAgent{
		Agent:  baseAgent,
		logger: config.GetLogger(),
	}
}

// Init initializes the agent
func (a *TaskSolvingAgent) Init() error {
	a.logger.WithField("agent", a.GetName()).Info("Initializing Task-Solving Agent")
	
	// Get message bus connection
	bus, err := config.ConnectMessageBus()
	if err != nil {
		a.logger.WithError(err).Warn("Message bus not available, continuing without it")
	} else {
		a.messageBus = bus
	}

	return nil
}

// Start begins the agent's operation
func (a *TaskSolvingAgent) Start() error {
	if err := a.Init(); err != nil {
		return err
	}

	a.Status = core.StatusStarting
	a.StartedAt = time.Now()
	a.Error = nil

	// Subscribe to relevant events
	if a.messageBus != nil {
		a.messageBus.Subscribe(events.TASK_CREATED, a.handleTaskEvent)
	}

	a.Status = core.StatusRunning
	a.logger.WithField("agent", a.GetName()).Info("Task-Solving Agent started")
	return nil
}

// Stop gracefully shuts down the agent
func (a *TaskSolvingAgent) Stop() error {
	a.Status = core.StatusStopping
	a.logger.WithField("agent", a.GetName()).Info("Task-Solving Agent stopping")
	a.Status = core.StatusStopped
	a.StoppedAt = time.Now()
	return nil
}

// HandleMessage processes incoming messages
func (a *TaskSolvingAgent) HandleMessage(event interface{}) error {
	a.logger.WithField("agent", a.GetName()).Debug("Received message")
	
	// Parse task from event
	task, ok := event.(*Task)
	if !ok {
		return a.ProcessTask(&Task{
			ID:          "unknown",
			Description: "Unknown task",
			Priority:    "normal",
		})
	}

	return a.ProcessTask(task)
}

// ProcessTask processes a task using LLM to interpret intent
func (a *TaskSolvingAgent) ProcessTask(task *Task) (*TaskResult, error) {
	a.logger.WithField("task_id", task.ID).Info("Processing task")

	// TODO: Call LLM to interpret task intent
	// This is a placeholder for Phase 5
	reasoning := "Task interpreted: " + task.Description
	actions := []string{"action1", "action2"}

	result := &TaskResult{
		TaskID:    task.ID,
		Status:    "processed",
		Actions:   actions,
		Reasoning: reasoning,
		Metadata:  make(map[string]interface{}),
	}

	// Publish task created event
	if a.messageBus != nil {
		eventData, _ := json.Marshal(result)
		a.messageBus.Publish(events.TASK_CREATED, eventData)
	}

	return result, nil
}

// handleTaskEvent handles task events from message bus
func (a *TaskSolvingAgent) handleTaskEvent(data []byte) {
	var task Task
	if err := json.Unmarshal(data, &task); err != nil {
		a.logger.WithError(err).Error("Failed to unmarshal task event")
		return
	}
	
	a.ProcessTask(&task)
}

// ExplainAction provides human-readable explanation for task processing actions
func (a *TaskSolvingAgent) ExplainAction(input interface{}, output interface{}) string {
	var problem, action, reason string
	
	// Parse input to extract task details
	if inputMap, ok := input.(map[string]interface{}); ok {
		if taskType, ok := inputMap["task_type"].(string); ok {
			problem = fmt.Sprintf("a %s task was received", taskType)
		} else if taskDesc, ok := inputMap["description"].(string); ok {
			problem = fmt.Sprintf("task '%s' was received", taskDesc)
		}
	}
	
	// Parse output to extract action
	if outputMap, ok := output.(map[string]interface{}); ok {
		if actionTaken, ok := outputMap["action"].(string); ok {
			action = actionTaken
		} else if steps, ok := outputMap["steps"].([]interface{}); ok && len(steps) > 0 {
			action = fmt.Sprintf("delegated to %d agent(s) for processing", len(steps))
		}
	}
	
	// Default values
	if problem == "" {
		problem = "a user task was received"
	}
	if action == "" {
		action = "processed the task"
	}
	reason = "to fulfill the user's request"
	
	// Format explanation
	explanation := fmt.Sprintf("The agent detected that %s and %s %s.", problem, action, reason)
	
	return explanation
}

