package main

import (
	"log"
	"net/http"
	"os"

	selfhealing "github.com/ai-driven-self-healing-cloud/agents/self-healing"
)

func main() {
	log.Println("Self-healing agent starting...")

	// Initialize the agent
	agent := selfhealing.NewSelfHealingAgent()
	if err := agent.Start(); err != nil {
		log.Fatalf("Failed to start agent: %v", err)
	}
	log.Println("Self-Healing Agent initialized successfully")

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
