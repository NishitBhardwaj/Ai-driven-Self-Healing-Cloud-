package config

import (
	"fmt"
	"os"
	"strings"

	"github.com/joho/godotenv"
)

// Config holds all system configuration
type Config struct {
	OpenRouterAPIKey string
	GeminiAPIKey     string
	MessageBusURL    string
	MessageBusType   string // "nats" or "rabbitmq"
	LogLevel         string
}

var globalConfig *Config

// LoadConfig loads configuration from environment variables and secrets file
func LoadConfig() (*Config, error) {
	// Try to load .env file (optional)
	_ = godotenv.Load()

	// Try to load from secrets file first
	loadSecretsFromFile()

	cfg := &Config{
		OpenRouterAPIKey: getEnv("OPENROUTER_API_KEY", ""),
		GeminiAPIKey:     getEnv("GEMINI_API_KEY", ""),
		MessageBusURL:    getEnv("MESSAGE_BUS_URL", "nats://localhost:4222"),
		MessageBusType:   getEnv("MESSAGE_BUS_TYPE", "nats"),
		LogLevel:         getEnv("LOG_LEVEL", "info"),
	}

	// Validate API keys
	if err := cfg.Validate(); err != nil {
		return nil, fmt.Errorf("config validation failed: %w", err)
	}

	globalConfig = cfg
	return cfg, nil
}

// GetConfig returns the global configuration instance
func GetConfig() *Config {
	return globalConfig
}

// Validate checks that all required configuration is present
func (c *Config) Validate() error {
	if c.OpenRouterAPIKey == "" {
		return fmt.Errorf("OPENROUTER_API_KEY is required")
	}
	if c.GeminiAPIKey == "" {
		return fmt.Errorf("GEMINI_API_KEY is required")
	}
	return nil
}

// loadSecretsFromFile attempts to load API keys from config/secrets/api_keys.txt
func loadSecretsFromFile() {
	secretsPath := "config/secrets/api_keys.txt"
	data, err := os.ReadFile(secretsPath)
	if err != nil {
		// File doesn't exist or can't be read, that's okay
		return
	}

	lines := strings.Split(string(data), "\n")
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}

		// Parse KEY = VALUE format
		parts := strings.SplitN(line, "=", 2)
		if len(parts) != 2 {
			continue
		}

		key := strings.TrimSpace(parts[0])
		value := strings.TrimSpace(parts[1])

		// Set environment variable if not already set
		if os.Getenv(key) == "" {
			os.Setenv(key, value)
		}
	}
}

// getEnv gets an environment variable with a default value
func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

