package main

import (
	"log"
	"net/http"
	"os"

	optimization "github.com/ai-driven-self-healing-cloud/agents/optimization"
)

func main() {
	log.Println("Optimization agent starting...")

	// Initialize the agent
	agent := optimization.NewOptimizer()
	log.Println("Optimization Agent initialized successfully")

	// Silence unused variable
	_ = agent

	// Health check endpoint
	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("ok"))
	})

	// Get port from environment or default to 8080
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Println("Listening on :" + port)

	// THIS LINE MUST EXIST - blocks forever
	// If ListenAndServe is missing → your pod WILL crash
	log.Fatal(http.ListenAndServe(":"+port, nil))
}
