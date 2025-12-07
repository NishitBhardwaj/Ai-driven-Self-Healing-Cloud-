package n8n

import (
	"encoding/json"
	"net/http"
	"time"

	"github.com/gorilla/mux"
	"github.com/sirupsen/logrus"
)

// Routes sets up HTTP routes for the n8n Workflow Agent
type Routes struct {
	agent  *N8NAgent
	logger *logrus.Logger
}

// NewRoutes creates a new Routes instance
func NewRoutes(agent *N8NAgent) *Routes {
	return &Routes{
		agent:  agent,
		logger: agent.logger,
	}
}

// RegisterRoutes registers all HTTP routes for the agent
func (r *Routes) RegisterRoutes(router *mux.Router) {
	router.HandleFunc("/health", r.HealthHandler).Methods("GET")
	router.HandleFunc("/action", r.ActionHandler).Methods("POST")
	router.HandleFunc("/status", r.StatusHandler).Methods("GET")
	router.HandleFunc("/webhook", r.WebhookHandler).Methods("POST")
	router.HandleFunc("/trigger", r.TriggerHandler).Methods("POST")
}

// HealthHandler returns the health status of the agent
func (r *Routes) HealthHandler(w http.ResponseWriter, req *http.Request) {
	health := r.agent.HealthCheck()
	
	response := map[string]interface{}{
		"status":    "Agent Ready",
		"healthy":   health.Healthy,
		"agent":     r.agent.GetName(),
		"timestamp": time.Now().Unix(),
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

// ActionHandler handles action requests
func (r *Routes) ActionHandler(w http.ResponseWriter, req *http.Request) {
	var payload map[string]interface{}
	if err := json.NewDecoder(req.Body).Decode(&payload); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	response := map[string]interface{}{
		"status":  "action_received",
		"message": "n8n action will be processed",
		"agent":   r.agent.GetName(),
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

// StatusHandler returns the current status of the agent
func (r *Routes) StatusHandler(w http.ResponseWriter, req *http.Request) {
	status := map[string]interface{}{
		"agent":      r.agent.GetName(),
		"status":     string(r.agent.Status),
		"started_at": r.agent.StartedAt,
		"id":         r.agent.GetID(),
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(status)
}

// WebhookHandler handles incoming webhooks from n8n
func (r *Routes) WebhookHandler(w http.ResponseWriter, req *http.Request) {
	var callbackData map[string]interface{}
	if err := json.NewDecoder(req.Body).Decode(&callbackData); err != nil {
		http.Error(w, "Invalid callback format", http.StatusBadRequest)
		return
	}

	if err := r.agent.trigger.HandleCallback(callbackData); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	response := map[string]interface{}{
		"status":  "callback_processed",
		"message": "n8n callback received and processed",
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

// TriggerHandler handles workflow trigger requests
func (r *Routes) TriggerHandler(w http.ResponseWriter, req *http.Request) {
	var triggerReq TriggerRequest
	if err := json.NewDecoder(req.Body).Decode(&triggerReq); err != nil {
		http.Error(w, "Invalid trigger request format", http.StatusBadRequest)
		return
	}

	if err := r.agent.trigger.TriggerWorkflow(&triggerReq); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	response := map[string]interface{}{
		"status":  "triggered",
		"message": "n8n workflow triggered successfully",
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

