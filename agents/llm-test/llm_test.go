package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"time"

	"github.com/ai-driven-self-healing-cloud/config"
	"github.com/sirupsen/logrus"
)

// OpenRouterRequest represents a request to OpenRouter API
type OpenRouterRequest struct {
	Model    string    `json:"model"`
	Messages []Message `json:"messages"`
}

// Message represents a chat message
type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

// OpenRouterResponse represents a response from OpenRouter API
type OpenRouterResponse struct {
	Choices []struct {
		Message Message `json:"message"`
	} `json:"choices"`
	Error *struct {
		Message string `json:"message"`
	} `json:"error"`
}

// GeminiRequest represents a request to Gemini API
type GeminiRequest struct {
	Contents []struct {
		Parts []struct {
			Text string `json:"text"`
		} `json:"parts"`
	} `json:"contents"`
}

// GeminiResponse represents a response from Gemini API
type GeminiResponse struct {
	Candidates []struct {
		Content struct {
			Parts []struct {
				Text string `json:"text"`
			} `json:"parts"`
		} `json:"content"`
	} `json:"candidates"`
	Error *struct {
		Message string `json:"message"`
	} `json:"error"`
}

func main() {
	logger := logrus.New()
	logger.SetFormatter(&logrus.TextFormatter{
		FullTimestamp: true,
		ForceColors:   true,
	})

	// Load configuration
	cfg, err := config.LoadConfig()
	if err != nil {
		logger.WithError(err).Fatal("Failed to load configuration")
		os.Exit(1)
	}

	testPrompt := "Hello, are you online?"

	logger.Info("Testing LLM connectivity...")
	logger.Info("")

	// Test OpenRouter
	logger.Info("Testing OpenRouter API...")
	if err := testOpenRouter(cfg.OpenRouterAPIKey, testPrompt, logger); err != nil {
		logger.WithError(err).Error("OpenRouter test failed")
		os.Exit(1)
	}
	logger.Info("✓ OpenRouter OK")
	logger.Info("")

	// Test Gemini
	logger.Info("Testing Gemini API...")
	if err := testGemini(cfg.GeminiAPIKey, testPrompt, logger); err != nil {
		logger.WithError(err).Error("Gemini test failed")
		os.Exit(1)
	}
	logger.Info("✓ Gemini OK")
	logger.Info("")

	logger.Info("✓ LLM Test OK - All APIs are responding")
}

func testOpenRouter(apiKey, prompt string, logger *logrus.Logger) error {
	url := "https://openrouter.ai/api/v1/chat/completions"

	reqBody := OpenRouterRequest{
		Model: "openai/gpt-3.5-turbo",
		Messages: []Message{
			{
				Role:    "user",
				Content: prompt,
			},
		},
	}

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return fmt.Errorf("failed to marshal request: %w", err)
	}

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+apiKey)
	req.Header.Set("HTTP-Referer", "https://github.com/ai-driven-self-healing-cloud")
	req.Header.Set("X-Title", "AI-Driven Self-Healing Cloud")

	client := &http.Client{
		Timeout: 30 * time.Second,
	}

	resp, err := client.Do(req)
	if err != nil {
		return fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("API returned status %d: %s", resp.StatusCode, string(body))
	}

	var openRouterResp OpenRouterResponse
	if err := json.Unmarshal(body, &openRouterResp); err != nil {
		return fmt.Errorf("failed to parse response: %w", err)
	}

	if openRouterResp.Error != nil {
		return fmt.Errorf("API error: %s", openRouterResp.Error.Message)
	}

	if len(openRouterResp.Choices) == 0 {
		return fmt.Errorf("no choices in response")
	}

	logger.WithField("response", openRouterResp.Choices[0].Message.Content).Debug("OpenRouter response received")
	return nil
}

func testGemini(apiKey, prompt string, logger *logrus.Logger) error {
	url := fmt.Sprintf("https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=%s", apiKey)

	reqBody := GeminiRequest{
		Contents: []struct {
			Parts []struct {
				Text string `json:"text"`
			} `json:"parts"`
		}{
			{
				Parts: []struct {
					Text string `json:"text"`
				}{
					{Text: prompt},
				},
			},
		},
	}

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return fmt.Errorf("failed to marshal request: %w", err)
	}

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{
		Timeout: 30 * time.Second,
	}

	resp, err := client.Do(req)
	if err != nil {
		return fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("API returned status %d: %s", resp.StatusCode, string(body))
	}

	var geminiResp GeminiResponse
	if err := json.Unmarshal(body, &geminiResp); err != nil {
		return fmt.Errorf("failed to parse response: %w", err)
	}

	if geminiResp.Error != nil {
		return fmt.Errorf("API error: %s", geminiResp.Error.Message)
	}

	if len(geminiResp.Candidates) == 0 {
		return fmt.Errorf("no candidates in response")
	}

	logger.WithField("response", geminiResp.Candidates[0].Content.Parts[0].Text).Debug("Gemini response received")
	return nil
}

