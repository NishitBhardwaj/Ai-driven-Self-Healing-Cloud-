package events

import "time"

// Message bus topic constants for agent communication
const (
	// Task-Solving Agent events
	TASK_CREATED = "task.created"
	TASK_COMPLETED = "task.completed"
	TASK_FAILED = "task.failed"

	// Error and Code Fix events
	ERROR_DETECTED = "error.detected"
	CODE_FIX_REQUIRED = "code.fix.required"
	CODE_FIX_COMPLETED = "code.fix.completed"

	// Self-Healing Agent events
	HEALING_REQUIRED = "healing.required"
	HEAL_REQUIRED = "heal.required" // Alias for compatibility
	HEALING_STARTED = "healing.started"
	HEALING_COMPLETED = "healing.completed"
	HEALING_FAILED = "healing.failed"

	// Scaling Agent events
	SCALE_REQUIRED = "scale.required"
	SCALE_UP = "scale.up"
	SCALE_DOWN = "scale.down"
	SCALE_COMPLETED = "scale.completed"

	// Performance Monitoring events
	METRICS_COLLECTED = "metrics.collected"
	ANOMALY_DETECTED = "anomaly.detected"
	THRESHOLD_EXCEEDED = "threshold.exceeded"

	// Security Agent events
	SECURITY_ALERT = "security.alert"
	INTRUSION_DETECTED = "intrusion.detected"
	POLICY_VIOLATION = "policy.violation"

	// Optimization Agent events
	OPTIMIZATION_REQUIRED = "optimization.required"
	OPTIMIZATION_COMPLETED = "optimization.completed"
	COST_REDUCTION_OPPORTUNITY = "cost.reduction.opportunity"

	// n8n Workflow Agent events
	N8N_TRIGGER = "n8n.trigger"
	N8N_CALLBACK = "n8n.callback"
	N8N_WORKFLOW_COMPLETED = "n8n.workflow.completed"
)

// Event represents a message bus event
type Event struct {
	Type      string      `json:"type"`
	Source    string      `json:"source"`
	Payload   interface{} `json:"payload"`
	Timestamp int64       `json:"timestamp"`
}

// NewEvent creates a new event instance
func NewEvent(eventType, source string, payload interface{}) *Event {
	return &Event{
		Type:      eventType,
		Source:    source,
		Payload:   payload,
		Timestamp: time.Now().Unix(),
	}
}

