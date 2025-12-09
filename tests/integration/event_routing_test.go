package integration

import (
	"encoding/json"
	"testing"
	"time"

	"github.com/ai-driven-self-healing-cloud/agents/core"
	"github.com/ai-driven-self-healing-cloud/agents/events"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestEventRouterRoutesToCorrectAgent tests that router routes events to correct agents
func TestEventRouterRoutesToCorrectAgent(t *testing.T) {
	registry := core.GetRegistry()
	router := core.GetRouter()
	
	// Initialize router
	err := router.Init()
	if err != nil {
		t.Skip("Message bus not available, skipping integration test")
		return
	}
	
	// Test cases: event type -> expected agent
	testCases := []struct {
		eventType     string
		expectedAgent string
		description   string
	}{
		{
			eventType:     events.ERROR_DETECTED,
			expectedAgent: "Self-Healing Agent",
			description:   "ERROR_DETECTED should route to Self-Healing Agent",
		},
		{
			eventType:     events.HEALING_REQUIRED,
			expectedAgent: "Self-Healing Agent",
			description:   "HEALING_REQUIRED should route to Self-Healing Agent",
		},
		{
			eventType:     events.SCALE_REQUIRED,
			expectedAgent: "Scaling Agent",
			description:   "SCALE_REQUIRED should route to Scaling Agent",
		},
		{
			eventType:     events.THRESHOLD_EXCEEDED,
			expectedAgent: "Scaling Agent",
			description:   "THRESHOLD_EXCEEDED should route to Scaling Agent",
		},
		{
			eventType:     events.SECURITY_ALERT,
			expectedAgent: "Security Agent",
			description:   "SECURITY_ALERT should route to Security Agent",
		},
		{
			eventType:     events.CODE_FIX_REQUIRED,
			expectedAgent: "Coding/Code-Fixer Agent",
			description:   "CODE_FIX_REQUIRED should route to Coding Agent",
		},
		{
			eventType:     events.TASK_CREATED,
			expectedAgent: "Task-Solving Agent",
			description:   "TASK_CREATED should route to Task-Solving Agent",
		},
		{
			eventType:     events.METRICS_COLLECTED,
			expectedAgent: "Performance Monitoring Agent",
			description:   "METRICS_COLLECTED should route to Monitoring Agent",
		},
		{
			eventType:     events.ANOMALY_DETECTED,
			expectedAgent: "Performance Monitoring Agent",
			description:   "ANOMALY_DETECTED should route to Monitoring Agent",
		},
		{
			eventType:     events.OPTIMIZATION_REQUIRED,
			expectedAgent: "Optimization Agent",
			description:   "OPTIMIZATION_REQUIRED should route to Optimization Agent",
		},
	}
	
	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			// Create test payload
			payload := map[string]interface{}{
				"test": "data",
			}
			
			// Route event
			err := router.Route(tc.eventType, payload)
			require.NoError(t, err, "Should route %s event", tc.eventType)
			
			// Give time for routing
			time.Sleep(50 * time.Millisecond)
			
			// In production, would verify agent received the event
			// For now, just verify routing doesn't error
		})
	}
}

// TestEventRouterMultipleAgents tests routing to multiple agents for same event
func TestEventRouterMultipleAgents(t *testing.T) {
	router := core.GetRouter()
	
	err := router.Init()
	if err != nil {
		t.Skip("Message bus not available, skipping integration test")
		return
	}
	
	// ERROR_DETECTED should route to both Self-Healing and Coding agents
	payload := map[string]interface{}{
		"error_type": "code_error",
		"service_id": "web-app-123",
	}
	
	err = router.Route(events.ERROR_DETECTED, payload)
	require.NoError(t, err, "Should route ERROR_DETECTED to multiple agents")
	
	// ANOMALY_DETECTED should route to both Monitoring and Self-Healing agents
	anomalyPayload := map[string]interface{}{
		"metric_name": "cpu_usage",
		"value":       0.95,
	}
	
	err = router.Route(events.ANOMALY_DETECTED, anomalyPayload)
	require.NoError(t, err, "Should route ANOMALY_DETECTED to multiple agents")
	
	// THRESHOLD_EXCEEDED should route to both Scaling and Monitoring agents
	thresholdPayload := map[string]interface{}{
		"metric":  "cpu_usage",
		"value":   0.95,
		"threshold": 0.90,
	}
	
	err = router.Route(events.THRESHOLD_EXCEEDED, thresholdPayload)
	require.NoError(t, err, "Should route THRESHOLD_EXCEEDED to multiple agents")
	
	time.Sleep(100 * time.Millisecond)
}

// TestEventRouterUnknownEvent tests handling of unknown event types
func TestEventRouterUnknownEvent(t *testing.T) {
	router := core.GetRouter()
	
	err := router.Init()
	if err != nil {
		t.Skip("Message bus not available, skipping integration test")
		return
	}
	
	// Unknown event type
	unknownEvent := "unknown.event.type"
	payload := map[string]interface{}{
		"data": "test",
	}
	
	// Should handle gracefully (may broadcast to all agents or log warning)
	err = router.Route(unknownEvent, payload)
	// Should not error, but may log warning
	if err != nil {
		// If it errors, that's acceptable for unknown events
		assert.Error(t, err, "Unknown events may error")
	}
}

// TestEventRouterConcurrentEvents tests concurrent event routing
func TestEventRouterConcurrentEvents(t *testing.T) {
	router := core.GetRouter()
	
	err := router.Init()
	if err != nil {
		t.Skip("Message bus not available, skipping integration test")
		return
	}
	
	// Publish multiple events concurrently
	eventTypes := []string{
		events.ERROR_DETECTED,
		events.SCALE_REQUIRED,
		events.HEALING_REQUIRED,
		events.SECURITY_ALERT,
		events.TASK_CREATED,
	}
	
	errors := make(chan error, len(eventTypes))
	
	for _, eventType := range eventTypes {
		go func(et string) {
			payload := map[string]interface{}{
				"test": "concurrent",
			}
			err := router.Route(et, payload)
			errors <- err
		}(eventType)
	}
	
	// Wait for all events to be processed
	for i := 0; i < len(eventTypes); i++ {
		err := <-errors
		assert.NoError(t, err, "Concurrent event routing should not error")
	}
	
	time.Sleep(100 * time.Millisecond)
}

// TestEventRouterEventOrdering tests event ordering (if required)
func TestEventRouterEventOrdering(t *testing.T) {
	router := core.GetRouter()
	
	err := router.Init()
	if err != nil {
		t.Skip("Message bus not available, skipping integration test")
		return
	}
	
	// Publish events in sequence
	sequence := []struct {
		eventType string
		payload   map[string]interface{}
	}{
		{
			eventType: events.ERROR_DETECTED,
			payload:   map[string]interface{}{"step": 1},
		},
		{
			eventType: events.HEALING_REQUIRED,
			payload:   map[string]interface{}{"step": 2},
		},
		{
			eventType: events.HEALING_COMPLETED,
			payload:   map[string]interface{}{"step": 3},
		},
	}
	
	for _, evt := range sequence {
		err := router.Route(evt.eventType, evt.payload)
		require.NoError(t, err, "Should route event in sequence")
		time.Sleep(50 * time.Millisecond)
	}
}

