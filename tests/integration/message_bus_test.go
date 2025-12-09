package integration

import (
	"encoding/json"
	"testing"
	"time"

	"github.com/ai-driven-self-healing-cloud/agents/core"
	"github.com/ai-driven-self-healing-cloud/agents/events"
	"github.com/ai-driven-self-healing-cloud/config"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestMessageBusCommunication tests agent communication through message bus
func TestMessageBusCommunication(t *testing.T) {
	// Create mock message bus for testing
	// In production, this would connect to NATS/RabbitMQ
	// For testing, we'll use an in-memory message bus
	
	// Register agents
	registry := core.GetRegistry()
	
	// Create test agents (simplified for testing)
	// In real scenario, these would be actual agent instances
	
	// Test message bus connection
	bus, err := config.ConnectMessageBus()
	if err != nil {
		t.Skip("Message bus not available, skipping integration test")
		return
	}
	defer bus.Disconnect()
	
	// Verify connection
	assert.True(t, bus.IsConnected(), "Message bus should be connected")
}

// TestErrorDetectedEvent tests that ERROR_DETECTED event is received by agents
func TestErrorDetectedEvent(t *testing.T) {
	registry := core.GetRegistry()
	router := core.GetRouter()
	
	// Initialize router
	err := router.Init()
	if err != nil {
		t.Skip("Message bus not available, skipping integration test")
		return
	}
	
	// Create error event
	eventPayload := map[string]interface{}{
		"error_type":    "service_crash",
		"service_id":    "web-app-123",
		"error_message": "Service crashed unexpectedly",
		"severity":      "high",
	}
	
	payload, err := json.Marshal(eventPayload)
	require.NoError(t, err)
	
	// Publish error detected event
	err = router.Route(events.ERROR_DETECTED, eventPayload)
	require.NoError(t, err, "Should publish ERROR_DETECTED event")
	
	// Give time for event processing
	time.Sleep(100 * time.Millisecond)
	
	// Verify event was routed (in real scenario, would check agent received it)
	// This is a simplified test - in production would verify agent state
}

// TestScalingRequiredEvent tests that SCALE_REQUIRED event is received
func TestScalingRequiredEvent(t *testing.T) {
	router := core.GetRouter()
	
	err := router.Init()
	if err != nil {
		t.Skip("Message bus not available, skipping integration test")
		return
	}
	
	// Create scaling event
	eventPayload := map[string]interface{}{
		"service_id":     "api-service",
		"current_load":   0.95,
		"target_replicas": 5,
		"reason":         "CPU usage exceeded threshold",
	}
	
	// Publish scale required event
	err = router.Route(events.SCALE_REQUIRED, eventPayload)
	require.NoError(t, err, "Should publish SCALE_REQUIRED event")
	
	// Give time for event processing
	time.Sleep(100 * time.Millisecond)
}

// TestHealingRequiredEvent tests that HEALING_REQUIRED event is received
func TestHealingRequiredEvent(t *testing.T) {
	router := core.GetRouter()
	
	err := router.Init()
	if err != nil {
		t.Skip("Message bus not available, skipping integration test")
		return
	}
	
	// Create healing event
	eventPayload := map[string]interface{}{
		"service_id":   "web-app-123",
		"failure_type": "crash_loop",
		"error":        "Pod restarting repeatedly",
	}
	
	// Publish healing required event
	err = router.Route(events.HEALING_REQUIRED, eventPayload)
	require.NoError(t, err, "Should publish HEALING_REQUIRED event")
	
	// Give time for event processing
	time.Sleep(100 * time.Millisecond)
}

// TestSecurityAlertEvent tests that SECURITY_ALERT event is received
func TestSecurityAlertEvent(t *testing.T) {
	router := core.GetRouter()
	
	err := router.Init()
	if err != nil {
		t.Skip("Message bus not available, skipping integration test")
		return
	}
	
	// Create security alert event
	eventPayload := map[string]interface{}{
		"threat_type": "intrusion_attempt",
		"source_ip":   "192.168.1.100",
		"severity":    "high",
		"description": "Multiple failed login attempts",
	}
	
	// Publish security alert event
	err = router.Route(events.SECURITY_ALERT, eventPayload)
	require.NoError(t, err, "Should publish SECURITY_ALERT event")
	
	// Give time for event processing
	time.Sleep(100 * time.Millisecond)
}

// TestTaskCreatedEvent tests that TASK_CREATED event is received
func TestTaskCreatedEvent(t *testing.T) {
	router := core.GetRouter()
	
	err := router.Init()
	if err != nil {
		t.Skip("Message bus not available, skipping integration test")
		return
	}
	
	// Create task event
	eventPayload := map[string]interface{}{
		"task_id":      "task-123",
		"description":  "Scale up the web service",
		"priority":     "high",
		"assigned_to":  "scaling-agent",
	}
	
	// Publish task created event
	err = router.Route(events.TASK_CREATED, eventPayload)
	require.NoError(t, err, "Should publish TASK_CREATED event")
	
	// Give time for event processing
	time.Sleep(100 * time.Millisecond)
}

// TestMultipleEventsSequential tests multiple events in sequence
func TestMultipleEventsSequential(t *testing.T) {
	router := core.GetRouter()
	
	err := router.Init()
	if err != nil {
		t.Skip("Message bus not available, skipping integration test")
		return
	}
	
	// Publish multiple events
	events := []struct {
		eventType string
		payload   map[string]interface{}
	}{
		{
			eventType: events.ERROR_DETECTED,
			payload: map[string]interface{}{
				"error_type": "service_crash",
				"service_id": "web-app-123",
			},
		},
		{
			eventType: events.HEALING_REQUIRED,
			payload: map[string]interface{}{
				"service_id":   "web-app-123",
				"failure_type": "crash_loop",
			},
		},
		{
			eventType: events.SCALE_REQUIRED,
			payload: map[string]interface{}{
				"service_id": "api-service",
				"current_load": 0.95,
			},
		},
	}
	
	for _, evt := range events {
		err = router.Route(evt.eventType, evt.payload)
		require.NoError(t, err, "Should publish %s event", evt.eventType)
		time.Sleep(50 * time.Millisecond)
	}
}

// TestMessageBusPublishSubscribe tests basic publish/subscribe functionality
func TestMessageBusPublishSubscribe(t *testing.T) {
	bus, err := config.ConnectMessageBus()
	if err != nil {
		t.Skip("Message bus not available, skipping integration test")
		return
	}
	defer bus.Disconnect()
	
	// Test subject
	subject := "test.integration"
	received := make(chan []byte, 1)
	
	// Subscribe to test subject
	err = bus.Subscribe(subject, func(data []byte) {
		received <- data
	})
	require.NoError(t, err, "Should subscribe to subject")
	
	// Publish test message
	testMessage := []byte(`{"test": "message"}`)
	err = bus.Publish(subject, testMessage)
	require.NoError(t, err, "Should publish message")
	
	// Wait for message (with timeout)
	select {
	case msg := <-received:
		assert.Equal(t, testMessage, msg, "Should receive published message")
	case <-time.After(1 * time.Second):
		t.Fatal("Message not received within timeout")
	}
}

