package api

import (
	"net/http"

	"github.com/ai-driven-self-healing-cloud/agents/core"
	"github.com/ai-driven-self-healing-cloud/api/handlers"
	"github.com/gorilla/mux"
	"github.com/sirupsen/logrus"
)

// SetupRoutes sets up all API routes
func SetupRoutes(registry *core.AgentRegistry, logger *logrus.Logger) *mux.Router {
	router := mux.NewRouter()

	// Create handlers
	agentStatusHandler := handlers.NewAgentStatusHandler(registry, logger)
	logsHandler := handlers.NewLogsHandler(logger)
	decisionHistoryHandler := handlers.NewDecisionHistoryHandler(logger)

	// API routes
	api := router.PathPrefix("/api").Subrouter()

	// Agent Status API
	api.HandleFunc("/agents/status", agentStatusHandler.GetAgentStatus).Methods("GET")

	// Logs API
	api.HandleFunc("/agents/logs", logsHandler.GetLogs).Methods("GET")

	// Decision History API
	api.HandleFunc("/agents/decision-history", decisionHistoryHandler.GetDecisionHistory).Methods("GET")

	// Health check
	router.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"status":"ok"}`))
	}).Methods("GET")

	// CORS middleware
	router.Use(corsMiddleware)

	return router
}

// corsMiddleware adds CORS headers to responses
func corsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}

		next.ServeHTTP(w, r)
	})
}

