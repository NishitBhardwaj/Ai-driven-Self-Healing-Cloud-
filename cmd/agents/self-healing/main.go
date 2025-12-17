package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	selfhealing "github.com/ai-driven-self-healing-cloud/agents/self-healing"
)

func main() {
	log.Println("Agent booting...")
	log.Println("Self-Healing Agent Starting...")

	// Initialize the agent
	agent := selfhealing.NewSelfHealingAgent()
	if err := agent.Start(); err != nil {
		log.Fatalf("Failed to start agent: %v", err)
	}
	log.Println("Self-Healing Agent initialized successfully")

	// Health check endpoint
	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, `{"status":"healthy","agent":"self-healing","timestamp":"%s"}`, time.Now().Format(time.RFC3339))
	})

	// Ready check endpoint
	http.HandleFunc("/ready", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, `{"ready":true,"agent":"self-healing"}`)
	})

	// Get port from environment or default to 8080
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	// Start HTTP server in goroutine
	go func() {
		log.Printf("Starting HTTP server on port %s", port)
		if err := http.ListenAndServe(":"+port, nil); err != nil && err != http.ErrServerClosed {
			log.Fatalf("HTTP server failed: %v", err)
		}
	}()

	log.Println("[AGENT READY] Self-Healing Agent is running")

	// Wait for interrupt signal for graceful shutdown
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)
	
	<-sigChan
	log.Println("Shutting down...")
	agent.Stop()
}
