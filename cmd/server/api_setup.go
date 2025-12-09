package main

import (
	"net/http"
	"os"

	"github.com/ai-driven-self-healing-cloud/agents/core"
	"github.com/ai-driven-self-healing-cloud/api"
	"github.com/gorilla/mux"
	"github.com/sirupsen/logrus"
)

// setupAPIRoutes sets up API routes
func setupAPIRoutes(registry *core.AgentRegistry, logger *logrus.Logger) *mux.Router {
	return api.SetupRoutes(registry, logger)
}

// startHTTPServer starts the HTTP server
func startHTTPServer(router *mux.Router, logger *logrus.Logger) {
	port := os.Getenv("HTTP_PORT")
	if port == "" {
		port = "8080"
	}
	
	addr := ":" + port
	logger.WithField("port", port).Info("[HTTP] Starting server on " + addr)
	
	if err := http.ListenAndServe(addr, router); err != nil {
		logger.WithError(err).Fatal("[HTTP] Server failed to start")
	}
}

