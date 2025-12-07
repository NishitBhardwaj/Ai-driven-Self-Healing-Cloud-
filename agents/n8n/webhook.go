package n8n

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/sirupsen/logrus"
)

// WebhookHandler handles n8n webhook interactions
type WebhookHandler struct {
	logger     *logrus.Logger
	webhookURL string
	client     *http.Client
}

// NewWebhookHandler creates a new WebhookHandler instance
func NewWebhookHandler() *WebhookHandler {
	return &WebhookHandler{
		logger:     logrus.New(),
		webhookURL: "http://localhost:5678/webhook", // Default n8n webhook URL
		client: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// WebhookPayload represents the payload sent to n8n
type WebhookPayload struct {
	EventType  string                 `json:"event_type"`
	Source     string                 `json:"source"`
	Data       map[string]interface{} `json:"data"`
	Timestamp  int64                  `json:"timestamp"`
	WorkflowID string                 `json:"workflow_id,omitempty"`
}

// WebhookResponse represents the response from n8n
type WebhookResponse struct {
	Success   bool                   `json:"success"`
	Action    string                 `json:"action,omitempty"`
	Data      map[string]interface{} `json:"data,omitempty"`
	Message   string                 `json:"message,omitempty"`
	Timestamp int64                  `json:"timestamp"`
}

// SendWebhook sends a webhook trigger to n8n
func (wh *WebhookHandler) SendWebhook(payload *WebhookPayload) (*WebhookResponse, error) {
	wh.logger.WithFields(logrus.Fields{
		"event_type": payload.EventType,
		"webhook_url": wh.webhookURL,
	}).Info("Sending webhook to n8n")

	jsonData, err := json.Marshal(payload)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal payload: %w", err)
	}

	req, err := http.NewRequest("POST", wh.webhookURL, bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")

	resp, err := wh.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("webhook request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("webhook returned status %d", resp.StatusCode)
	}

	var response WebhookResponse
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	response.Timestamp = time.Now().Unix()
	return &response, nil
}

// SetWebhookURL sets the n8n webhook URL
func (wh *WebhookHandler) SetWebhookURL(url string) {
	wh.webhookURL = url
}

