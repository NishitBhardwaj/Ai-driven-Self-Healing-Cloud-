package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	scaling "github.com/ai-driven-self-healing-cloud/agents/scaling"
)

func main() {
	log.Println("Agent booting...")
	log.Println("Scaling Agent Starting...")

	// Initialize the agent
	agent := scaling.NewAutoScaler()
	log.Println("Scaling Agent initialized successfully")

	// Health check endpoint
	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, `{"status":"healthy","agent":"scaling","timestamp":"%s"}`, time.Now().Format(time.RFC3339))
	})

	// Ready check endpoint
	http.HandleFunc("/ready", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, `{"ready":true,"agent":"scaling"}`)
	})

	// Get port from environment or default to 8080
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	// Silence unused variable warning
	_ = agent

	// Start HTTP server in goroutine
	go func() {
		log.Printf("Starting HTTP server on port %s", port)
		if err := http.ListenAndServe(":"+port, nil); err != nil && err != http.ErrServerClosed {
			log.Fatalf("HTTP server failed: %v", err)
		}
	}()

	log.Println("[AGENT READY] Scaling Agent is running")

	// Wait for interrupt signal for graceful shutdown
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)
	
	<-sigChan
	log.Println("Shutting down...")
}
