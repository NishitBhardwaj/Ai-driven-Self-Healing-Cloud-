package n8n

import (
	"encoding/json"
	"time"

	"github.com/ai-driven-self-healing-cloud/agents/events"
	"github.com/sirupsen/logrus"
)

// TriggerHandler handles n8n workflow triggers
type TriggerHandler struct {
	logger     *logrus.Logger
	webhook    *WebhookHandler
	messageBus interface{} // Will be typed properly when message bus is available
}

// NewTriggerHandler creates a new TriggerHandler instance
func NewTriggerHandler() *TriggerHandler {
	return &TriggerHandler{
		logger:  logrus.New(),
		webhook: NewWebhookHandler(),
	}
}

// TriggerRequest represents a request to trigger an n8n workflow
type TriggerRequest struct {
	WorkflowID string                 `json:"workflow_id"`
	EventType  string                 `json:"event_type"`
	Data       map[string]interface{} `json:"data"`
	Source     string                 `json:"source"`
}

// TriggerWorkflow triggers an n8n workflow via webhook
func (th *TriggerHandler) TriggerWorkflow(request *TriggerRequest) error {
	th.logger.WithFields(logrus.Fields{
		"workflow_id": request.WorkflowID,
		"event_type":  request.EventType,
	}).Info("Triggering n8n workflow")

	payload := &WebhookPayload{
		EventType:  request.EventType,
		Source:     request.Source,
		Data:       request.Data,
		WorkflowID: request.WorkflowID,
		Timestamp:  time.Now().Unix(),
	}

	response, err := th.webhook.SendWebhook(payload)
	if err != nil {
		return err
	}

	if !response.Success {
		th.logger.WithField("message", response.Message).Warn("n8n workflow returned unsuccessful response")
	}

	// Publish n8n trigger event
	// TODO: Publish to message bus when available

	return nil
}

// HandleCallback processes callback from n8n workflow
func (th *TriggerHandler) HandleCallback(callbackData map[string]interface{}) error {
	th.logger.Info("Processing n8n callback")

	// Extract action from callback
	action, ok := callbackData["action"].(string)
	if !ok {
		th.logger.Warn("No action found in callback")
		return nil
	}

	th.logger.WithField("action", action).Info("Executing action from n8n callback")

	// TODO: Execute action based on callback data
	// This will trigger appropriate agent actions

	return nil
}

