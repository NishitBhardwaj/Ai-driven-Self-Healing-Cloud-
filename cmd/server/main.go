package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/ai-driven-self-healing-cloud/agents/core"
	"github.com/ai-driven-self-healing-cloud/api"
	"github.com/ai-driven-self-healing-cloud/config"
	"github.com/gorilla/mux"
	"github.com/sirupsen/logrus"
)

func main() {
	// Initialize logger first (will use default config)
	logger := logrus.New()
	logger.SetFormatter(&logrus.TextFormatter{
		FullTimestamp: true,
		ForceColors:   true,
	})
	logger.SetOutput(os.Stdout)

	// Boot sequence
	logger.Info("")
	logger.Info("╔══════════════════════════════════════════════════════════════╗")
	logger.Info("║   AI-Driven Self-Healing Cloud Infrastructure System        ║")
	logger.Info("║   Phase 1: Core System Boot Layer                           ║")
	logger.Info("╚══════════════════════════════════════════════════════════════╝")
	logger.Info("")

	// Step 1: Load configuration
	logger.WithField("component", "boot").Info("[BOOT] Loading configuration...")
	cfg, err := config.LoadConfig()
	if err != nil {
		logger.WithError(err).Fatal("Failed to load configuration")
		os.Exit(1)
	}
	logger.WithField("component", "boot").Info("[BOOT] Config loaded")

	// Step 2: Validate API keys
	logger.WithField("component", "boot").Info("[BOOT] Validating API keys...")
	if err := cfg.Validate(); err != nil {
		logger.WithError(err).Fatal("API key validation failed")
		os.Exit(1)
	}
	logger.WithField("component", "boot").Info("[BOOT] API keys validated")

	// Step 3: Initialize logger with config
	logger.WithField("component", "boot").Info("[BOOT] Initializing logger...")
	config.InitLogger()
	logger = config.GetLogger()
	logger.WithField("component", "boot").Info("[BOOT] Logger initialized")

	// Step 4: Connect to message bus
	logger.WithField("component", "boot").Info("[BOOT] Connecting to message bus...")
	messageBus, err := config.ConnectMessageBus()
	if err != nil {
		logger.WithError(err).Warn("[BOOT] Message bus connection failed (continuing without it)")
		// Continue without message bus for now
	} else {
		logger.WithField("component", "boot").Info("[BOOT] Connected to message bus")
		defer func() {
			if messageBus != nil {
				messageBus.Disconnect()
			}
		}()
	}

	// Step 5: Initialize agent registry
	logger.WithField("component", "boot").Info("[BOOT] Initializing agent registry...")
	registry := core.GetRegistry()
	logger.WithField("component", "boot").Info("[BOOT] Agent registry initialized")
	logger.WithField("registered_agents", registry.GetAgentCount()).Info("[BOOT] Registered agents: 0")

	// Step 6: Setup API routes
	logger.WithField("component", "boot").Info("[BOOT] Setting up API routes...")
	apiRouter := setupAPIRoutes(registry, logger)
	logger.WithField("component", "boot").Info("[BOOT] API routes initialized")

	// Step 7: Start HTTP server
	logger.WithField("component", "boot").Info("[BOOT] Starting HTTP server...")
	go startHTTPServer(apiRouter, logger)

	// Step 8: Test LLM connectivity
	logger.WithField("component", "boot").Info("[BOOT] Testing LLM connectivity...")
	if err := testLLMConnectivity(cfg, logger); err != nil {
		logger.WithError(err).Warn("[BOOT] LLM connectivity test failed (system will continue)")
	} else {
		logger.WithField("component", "boot").Info("[BOOT] LLM connectivity OK")
	}

	// System ready
	logger.Info("")
	logger.Info("╔══════════════════════════════════════════════════════════════╗")
	logger.Info("║                    [SYSTEM READY]                            ║")
	logger.Info("╚══════════════════════════════════════════════════════════════╝")
	logger.Info("")

	// Wait for interrupt signal
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)

	logger.Info("System is running. Press Ctrl+C to shutdown...")
	<-sigChan

	logger.Info("")
	logger.Info("[SHUTDOWN] Gracefully shutting down...")
	if messageBus != nil {
		messageBus.Disconnect()
	}
	logger.Info("[SHUTDOWN] System stopped")
}

// testLLMConnectivity tests both OpenRouter and Gemini API connectivity
func testLLMConnectivity(cfg *config.Config, logger *logrus.Logger) error {
	// Test OpenRouter
	logger.WithField("component", "boot").Debug("Testing OpenRouter API...")
	if err := quickTestOpenRouter(cfg.OpenRouterAPIKey); err != nil {
		return fmt.Errorf("OpenRouter test failed: %w", err)
	}
	logger.WithField("component", "boot").Info("[BOOT] OpenRouter OK")

	// Test Gemini
	logger.WithField("component", "boot").Debug("Testing Gemini API...")
	if err := quickTestGemini(cfg.GeminiAPIKey); err != nil {
		return fmt.Errorf("Gemini test failed: %w", err)
	}
	logger.WithField("component", "boot").Info("[BOOT] Gemini OK")

	return nil
}

// quickTestOpenRouter performs a quick connectivity test to OpenRouter
func quickTestOpenRouter(apiKey string) error {
	// Simple test - just verify we can make a request
	// We'll use a minimal request to avoid consuming too many tokens
	url := "https://openrouter.ai/api/v1/chat/completions"
	
	reqBody := map[string]interface{}{
		"model": "openai/gpt-3.5-turbo",
		"messages": []map[string]string{
			{"role": "user", "content": "Hi"},
		},
		"max_tokens": 5,
	}

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return err
	}

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return err
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+apiKey)
	req.Header.Set("HTTP-Referer", "https://github.com/ai-driven-self-healing-cloud")

	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("status %d: %s", resp.StatusCode, string(body))
	}

	return nil
}

// quickTestGemini performs a quick connectivity test to Gemini
func quickTestGemini(apiKey string) error {
	url := fmt.Sprintf("https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=%s", apiKey)
	
	reqBody := map[string]interface{}{
		"contents": []map[string]interface{}{
			{
				"parts": []map[string]string{
					{"text": "Hi"},
				},
			},
		},
		"generationConfig": map[string]int{
			"maxOutputTokens": 5,
		},
	}

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return err
	}

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return err
	}

	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("status %d: %s", resp.StatusCode, string(body))
	}

	return nil
}

