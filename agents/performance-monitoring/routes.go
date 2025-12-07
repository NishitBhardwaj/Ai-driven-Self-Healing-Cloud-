package performancemonitoring

import (
	"encoding/json"
	"net/http"
	"time"

	"github.com/gorilla/mux"
	"github.com/sirupsen/logrus"
)

// Routes sets up HTTP routes for the Performance Monitoring Agent
type Routes struct {
	agent  *PerformanceMonitoringAgent
	logger *logrus.Logger
}

// NewRoutes creates a new Routes instance
func NewRoutes(agent *PerformanceMonitoringAgent) *Routes {
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
	router.HandleFunc("/metrics", r.MetricsHandler).Methods("GET")
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
		"message": "Monitoring action will be processed",
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

// MetricsHandler returns collected metrics
func (r *Routes) MetricsHandler(w http.ResponseWriter, req *http.Request) {
	metrics, err := r.agent.analyzer.CollectMetrics("http://localhost:9090")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(metrics)
}

