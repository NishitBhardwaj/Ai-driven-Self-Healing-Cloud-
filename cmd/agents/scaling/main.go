package main

import (
	"log"
	"net/http"
	"os"

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
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("ok"))
	})

	// Get port from environment or default to 8080
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	// Silence unused variable warning
	_ = agent

	log.Println("Listening on :" + port)

	// THIS LINE MUST EXIST - blocks forever
	// If ListenAndServe is missing → your pod WILL crash
	log.Fatal(http.ListenAndServe(":"+port, nil))
}
