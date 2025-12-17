package main

import (
	"log"
	"net/http"
	"os"

	tasksolving "github.com/ai-driven-self-healing-cloud/agents/task-solving"
)

func main() {
	log.Println("Agent booting...")
	log.Println("Task-Solving Agent Starting...")

	// Initialize the agent
	agent := tasksolving.NewTaskSolvingAgent()
	if err := agent.Start(); err != nil {
		log.Fatalf("Failed to start agent: %v", err)
	}
	log.Println("Task-Solving Agent initialized successfully")

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
