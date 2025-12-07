package tasksolving

import (
	"encoding/json"
	"net/http"
	"time"

	"github.com/ai-driven-self-healing-cloud/agents/core"
	"github.com/gorilla/mux"
	"github.com/sirupsen/logrus"
)

// Routes sets up HTTP routes for the Task-Solving Agent
type Routes struct {
	agent  *TaskSolvingAgent
	logger *logrus.Logger
}

// NewRoutes creates a new Routes instance
func NewRoutes(agent *TaskSolvingAgent) *Routes {
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
	router.HandleFunc("/task", r.TaskHandler).Methods("POST")
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
		"message": "Action will be processed",
		"agent":   r.agent.GetName(),
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

// StatusHandler returns the current status of the agent
func (r *Routes) StatusHandler(w http.ResponseWriter, req *http.Request) {
	status := map[string]interface{}{
		"agent":     r.agent.GetName(),
		"status":    string(r.agent.Status),
		"started_at": r.agent.StartedAt,
		"id":        r.agent.GetID(),
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(status)
}

// TaskHandler handles task creation requests
func (r *Routes) TaskHandler(w http.ResponseWriter, req *http.Request) {
	var task Task
	if err := json.NewDecoder(req.Body).Decode(&task); err != nil {
		http.Error(w, "Invalid task format", http.StatusBadRequest)
		return
	}

	// Process the task
	result, err := r.agent.ProcessTask(&task)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(result)
}

