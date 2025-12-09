package logging

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net"
	"os"
	"time"

	"github.com/ai-driven-self-healing-cloud/agents/core"
	"github.com/sirupsen/logrus"
)

// ELKLogger provides logging to ELK Stack for agents
type ELKLogger struct {
	logstashHost string
	logstashPort int
	tcpConn      net.Conn
	udpConn      *net.UDPConn
	enabled      bool
	logger       *logrus.Logger
}

// NewELKLogger creates a new ELK logger
func NewELKLogger(logstashHost string, logstashPort int) *ELKLogger {
	elk := &ELKLogger{
		logstashHost: logstashHost,
		logstashPort: logstashPort,
		enabled:      logstashHost != "",
		logger:       logrus.New(),
	}

	// Connect to Logstash if enabled
	if elk.enabled {
		elk.connect()
	}

	return elk
}

// connect establishes connection to Logstash
func (e *ELKLogger) connect() {
	// TCP connection for structured logs
	tcpAddr, err := net.ResolveTCPAddr("tcp", fmt.Sprintf("%s:%d", e.logstashHost, e.logstashPort))
	if err == nil {
		conn, err := net.DialTCP("tcp", nil, tcpAddr)
		if err == nil {
			e.tcpConn = conn
		}
	}

	// UDP connection for high-volume logs
	udpAddr, err := net.ResolveUDPAddr("udp", fmt.Sprintf("%s:%d", e.logstashHost, e.logstashPort+1))
	if err == nil {
		conn, err := net.DialUDP("udp", nil, udpAddr)
		if err == nil {
			e.udpConn = conn
		}
	}
}

// LogAction logs an agent action with explanation
func (e *ELKLogger) LogAction(agentID, agentName, action string, explanation *core.ActionExplanation) error {
	logEntry := map[string]interface{}{
		"@timestamp":       time.Now().Format(time.RFC3339),
		"agent_id":         agentID,
		"agent_name":       agentName,
		"action":           action,
		"action_taken":     explanation.ActionTaken,
		"explanation":      explanation.Reasoning,
		"reasoning":        explanation.Reasoning,
		"confidence":       explanation.ConfidenceLevel,
		"confidence_level": explanation.ConfidenceLevel,
		"mode":             string(explanation.Mode),
		"log_type":         "action",
		"level":            "info",
		"message":          fmt.Sprintf("Agent %s performed action: %s", agentName, action),
	}

	// Add reasoning chain if available
	if len(explanation.ReasoningChain) > 0 {
		logEntry["reasoning_chain"] = explanation.ReasoningChain
	}

	// Add alternative actions if available
	if len(explanation.AlternativeActions) > 0 {
		logEntry["alternative_actions"] = explanation.AlternativeActions
	}

	// Add context if available
	if explanation.Context != nil {
		logEntry["context"] = explanation.Context
	}

	return e.sendLog(logEntry)
}

// LogError logs an agent error
func (e *ELKLogger) LogError(agentID, agentName string, err error, context map[string]interface{}) error {
	logEntry := map[string]interface{}{
		"@timestamp": time.Now().Format(time.RFC3339),
		"agent_id":   agentID,
		"agent_name": agentName,
		"error":      err.Error(),
		"log_type":   "error",
		"level":      "error",
		"message":    fmt.Sprintf("Agent %s encountered error: %s", agentName, err.Error()),
	}

	if context != nil {
		for k, v := range context {
			logEntry[k] = v
		}
	}

	return e.sendLog(logEntry)
}

// LogExplanation logs an explanation with confidence level
func (e *ELKLogger) LogExplanation(agentID, agentName string, explanation *core.ActionExplanation) error {
	return e.LogAction(agentID, agentName, explanation.ActionTaken, explanation)
}

// LogEvent logs an event received by an agent
func (e *ELKLogger) LogEvent(agentID, agentName, eventType string, payload interface{}) error {
	logEntry := map[string]interface{}{
		"@timestamp": time.Now().Format(time.RFC3339),
		"agent_id":   agentID,
		"agent_name": agentName,
		"event_type": eventType,
		"log_type":   "event",
		"level":      "info",
		"message":    fmt.Sprintf("Agent %s received event: %s", agentName, eventType),
	}

	// Add payload if it's a map
	if payloadMap, ok := payload.(map[string]interface{}); ok {
		for k, v := range payloadMap {
			logEntry[k] = v
		}
	} else {
		logEntry["payload"] = payload
	}

	return e.sendLog(logEntry)
}

// LogConfidence logs confidence level for a decision
func (e *ELKLogger) LogConfidence(agentID, agentName string, confidence float64, mode string, reasoning string) error {
	logEntry := map[string]interface{}{
		"@timestamp":       time.Now().Format(time.RFC3339),
		"agent_id":         agentID,
		"agent_name":       agentName,
		"confidence":       confidence,
		"confidence_level": confidence,
		"mode":             mode,
		"decision_mode":    mode,
		"reasoning":        reasoning,
		"log_type":         "confidence",
		"level":            "info",
		"message":          fmt.Sprintf("Agent %s decision confidence: %.0f%% (%s mode)", agentName, confidence*100, mode),
	}

	return e.sendLog(logEntry)
}

// sendLog sends log entry to Logstash
func (e *ELKLogger) sendLog(logEntry map[string]interface{}) error {
	if !e.enabled {
		// Fallback to file logging
		return e.logToFile(logEntry)
	}

	// Convert to JSON
	jsonData, err := json.Marshal(logEntry)
	if err != nil {
		return fmt.Errorf("failed to marshal log entry: %w", err)
	}

	// Try TCP first (for structured logs)
	if e.tcpConn != nil {
		_, err = e.tcpConn.Write(append(jsonData, '\n'))
		if err == nil {
			return nil
		}
	}

	// Fallback to UDP (for high-volume logs)
	if e.udpConn != nil {
		_, err = e.udpConn.Write(jsonData)
		if err == nil {
			return nil
		}
	}

	// Final fallback to file
	return e.logToFile(logEntry)
}

// logToFile logs to file as fallback
func (e *ELKLogger) logToFile(logEntry map[string]interface{}) error {
	logDir := "logs/elk"
	if err := os.MkdirAll(logDir, 0755); err != nil {
		return fmt.Errorf("failed to create log directory: %w", err)
	}

	logFile := fmt.Sprintf("%s/agent-logs-%s.log", logDir, time.Now().Format("2006-01-02"))
	file, err := os.OpenFile(logFile, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return fmt.Errorf("failed to open log file: %w", err)
	}
	defer file.Close()

	jsonData, err := json.Marshal(logEntry)
	if err != nil {
		return fmt.Errorf("failed to marshal log entry: %w", err)
	}

	logLine := fmt.Sprintf("%s\n", string(jsonData))
	_, err = file.WriteString(logLine)
	return err
}

// Close closes connections
func (e *ELKLogger) Close() error {
	if e.tcpConn != nil {
		e.tcpConn.Close()
	}
	if e.udpConn != nil {
		e.udpConn.Close()
	}
	return nil
}

// GetDefaultELKLogger returns default ELK logger based on environment
func GetDefaultELKLogger() *ELKLogger {
	logstashHost := os.Getenv("LOGSTASH_HOST")
	if logstashHost == "" {
		logstashHost = "localhost"
	}

	logstashPort := 5000
	if port := os.Getenv("LOGSTASH_PORT"); port != "" {
		fmt.Sscanf(port, "%d", &logstashPort)
	}

	return NewELKLogger(logstashHost, logstashPort)
}

