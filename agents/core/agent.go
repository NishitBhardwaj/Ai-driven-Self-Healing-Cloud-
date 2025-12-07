package core

import (
	"time"
)

// AgentStatus represents the current status of an agent
type AgentStatus string

const (
	StatusStopped  AgentStatus = "stopped"
	StatusStarting AgentStatus = "starting"
	StatusRunning  AgentStatus = "running"
	StatusStopping AgentStatus = "stopping"
	StatusError    AgentStatus = "error"
)

// BaseAgent is the foundational agent interface that all agents must implement
type BaseAgent interface {
	// GetID returns the unique identifier for this agent
	GetID() string

	// GetName returns the human-readable name of the agent
	GetName() string

	// GetDescription returns a description of what this agent does
	GetDescription() string

	// Start begins the agent's operation
	Start() error

	// Stop gracefully shuts down the agent
	Stop() error

	// HealthCheck returns the current health status of the agent
	HealthCheck() HealthStatus

	// SendEvent sends an event to other agents or systems
	SendEvent(eventType string, payload interface{}) error

	// ReceiveEvent handles incoming events
	ReceiveEvent(eventType string, payload interface{}) error
}

// Agent is the base implementation of BaseAgent
type Agent struct {
	ID          string
	Name        string
	Description string
	Status      AgentStatus
	StartedAt   time.Time
	StoppedAt   time.Time
	Error       error
}

// GetID returns the agent's unique identifier
func (a *Agent) GetID() string {
	return a.ID
}

// GetName returns the agent's name
func (a *Agent) GetName() string {
	return a.Name
}

// GetDescription returns the agent's description
func (a *Agent) GetDescription() string {
	return a.Description
}

// Start begins the agent's operation (base implementation)
func (a *Agent) Start() error {
	a.Status = StatusStarting
	a.StartedAt = time.Now()
	a.Error = nil
	// Base implementation - agents should override this
	a.Status = StatusRunning
	return nil
}

// Stop gracefully shuts down the agent (base implementation)
func (a *Agent) Stop() error {
	a.Status = StatusStopping
	// Base implementation - agents should override this
	a.Status = StatusStopped
	a.StoppedAt = time.Now()
	return nil
}

// HealthCheck returns the current health status
func (a *Agent) HealthCheck() HealthStatus {
	status := HealthStatus{
		Healthy:   a.Status == StatusRunning,
		Status:    string(a.Status),
		Timestamp: time.Now(),
	}

	if a.Error != nil {
		status.Healthy = false
		status.Message = a.Error.Error()
	}

	return status
}

// SendEvent sends an event (stub - to be implemented by specific agents)
func (a *Agent) SendEvent(eventType string, payload interface{}) error {
	// Base implementation - agents should override this
	return nil
}

// ReceiveEvent handles incoming events (stub - to be implemented by specific agents)
func (a *Agent) ReceiveEvent(eventType string, payload interface{}) error {
	// Base implementation - agents should override this
	return nil
}

// NewAgent creates a new base agent instance
func NewAgent(id, name, description string) *Agent {
	return &Agent{
		ID:          id,
		Name:        name,
		Description: description,
		Status:      StatusStopped,
	}
}

