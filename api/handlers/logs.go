package handlers

import (
	"encoding/json"
	"net/http"
	"strconv"
	"time"

	"github.com/sirupsen/logrus"
)

// LogsHandler handles logs API requests
type LogsHandler struct {
	logger *logrus.Logger
}

// NewLogsHandler creates a new logs handler
func NewLogsHandler(logger *logrus.Logger) *LogsHandler {
	return &LogsHandler{
		logger: logger,
	}
}

// LogsResponse represents the response for logs
type LogsResponse struct {
	Logs      []LogEntry `json:"logs"`
	Total     int        `json:"total"`
	Page      int        `json:"page"`
	PageSize  int        `json:"page_size"`
	HasMore   bool       `json:"has_more"`
}

// LogEntry represents a single log entry
type LogEntry struct {
	ID          string    `json:"id"`
	Timestamp   time.Time `json:"timestamp"`
	AgentID     string    `json:"agent_id"`
	AgentName   string    `json:"agent_name"`
	Action      string    `json:"action"`
	ActionTaken string    `json:"action_taken"`
	Reasoning   string    `json:"reasoning"`
	Explanation string    `json:"explanation"`
	Confidence  float64   `json:"confidence,omitempty"`
	Mode        string    `json:"mode"` // "auto" or "manual"
	Type        string    `json:"type"` // "info", "success", "warning", "error"
	Status      string    `json:"status,omitempty"`
	Metadata    map[string]interface{} `json:"metadata,omitempty"`
}

// GetLogs handles GET /api/agents/logs
func (h *LogsHandler) GetLogs(w http.ResponseWriter, r *http.Request) {
	h.logger.WithField("endpoint", "/api/agents/logs").Info("Handling logs request")

	// Parse query parameters
	query := r.URL.Query()
	page, _ := strconv.Atoi(query.Get("page"))
	if page < 1 {
		page = 1
	}
	pageSize, _ := strconv.Atoi(query.Get("page_size"))
	if pageSize < 1 || pageSize > 1000 {
		pageSize = 100
	}
	agentID := query.Get("agent_id")
	logType := query.Get("type")
	startDate := query.Get("start_date")
	endDate := query.Get("end_date")

	// Get logs (in production, this would query a database)
	logs := h.getLogs(agentID, logType, startDate, endDate)

	// Paginate
	total := len(logs)
	start := (page - 1) * pageSize
	end := start + pageSize
	if start > total {
		start = total
	}
	if end > total {
		end = total
	}

	var paginatedLogs []LogEntry
	if start < total {
		paginatedLogs = logs[start:end]
	} else {
		paginatedLogs = []LogEntry{}
	}

	response := LogsResponse{
		Logs:     paginatedLogs,
		Total:    total,
		Page:     page,
		PageSize: pageSize,
		HasMore:  end < total,
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(response)
}

// getLogs retrieves logs (in production, this would query a database)
func (h *LogsHandler) getLogs(agentID, logType, startDate, endDate string) []LogEntry {
	// Generate sample logs
	logs := []LogEntry{
		{
			ID:          "log-1",
			Timestamp:   time.Now().Add(-5 * time.Minute),
			AgentID:     "self-healing-001",
			AgentName:   "Self-Healing Agent",
			Action:      "restart_pod",
			ActionTaken: "Restarted pod 'web-app-123'",
			Reasoning:   "Pod was in crash loop. Restarting should resolve the issue.",
			Explanation: "Pod was restarted due to crash loop detection. The system detected repeated pod crashes and automatically restarted the pod to restore service.",
			Confidence:  0.95,
			Mode:        "auto",
			Type:        "success",
			Status:      "completed",
		},
		{
			ID:          "log-2",
			Timestamp:   time.Now().Add(-10 * time.Minute),
			AgentID:     "scaling-001",
			AgentName:   "Scaling Agent",
			Action:      "scale_up",
			ActionTaken: "Scaled up from 3 to 5 replicas",
			Reasoning:   "CPU usage exceeded 95% threshold. Scaling up will distribute load.",
			Explanation: "CPU usage exceeded 95% threshold. Scaled up from 3 to 5 replicas to distribute load and reduce CPU usage per instance.",
			Confidence:  0.85,
			Mode:        "manual",
			Type:        "info",
			Status:      "completed",
		},
		{
			ID:          "log-3",
			Timestamp:   time.Now().Add(-15 * time.Minute),
			AgentID:     "security-001",
			AgentName:   "Security Agent",
			Action:      "block_ip",
			ActionTaken: "Blocked IP address 192.168.1.100",
			Reasoning:   "Multiple failed login attempts detected. Blocking IP to prevent breach.",
			Explanation: "Multiple failed login attempts detected from suspicious IP. Blocked the IP address to prevent potential security breach.",
			Confidence:  0.92,
			Mode:        "auto",
			Type:        "warning",
			Status:      "completed",
		},
		{
			ID:          "log-4",
			Timestamp:   time.Now().Add(-20 * time.Minute),
			AgentID:     "monitoring-001",
			AgentName:   "Performance Monitoring Agent",
			Action:      "collect_metrics",
			ActionTaken: "Collected system metrics",
			Reasoning:   "Scheduled metrics collection.",
			Explanation: "Collected system metrics and updated health status. All systems operating normally.",
			Confidence:  0.98,
			Mode:        "auto",
			Type:        "info",
			Status:      "completed",
		},
		{
			ID:          "log-5",
			Timestamp:   time.Now().Add(-25 * time.Minute),
			AgentID:     "self-healing-001",
			AgentName:   "Self-Healing Agent",
			Action:      "restart_service",
			ActionTaken: "Restarted service 'api-gateway'",
			Reasoning:   "Service was unresponsive. Restarting should restore functionality.",
			Explanation: "Service 'api-gateway' was unresponsive. Automatically restarted the service to restore functionality.",
			Confidence:  0.90,
			Mode:        "auto",
			Type:        "success",
			Status:      "completed",
		},
		{
			ID:          "log-6",
			Timestamp:   time.Now().Add(-30 * time.Minute),
			AgentID:     "scaling-001",
			AgentName:   "Scaling Agent",
			Action:      "scale_down",
			ActionTaken: "Scaled down from 5 to 3 replicas",
			Reasoning:   "CPU usage dropped below 50%. Scaling down to optimize costs.",
			Explanation: "CPU usage dropped below 50% threshold. Scaled down from 5 to 3 replicas to optimize resource usage and costs.",
			Confidence:  0.88,
			Mode:        "auto",
			Type:        "info",
			Status:      "completed",
		},
	}

	// Filter by agent ID
	if agentID != "" {
		filtered := []LogEntry{}
		for _, log := range logs {
			if log.AgentID == agentID {
				filtered = append(filtered, log)
			}
		}
		logs = filtered
	}

	// Filter by type
	if logType != "" {
		filtered := []LogEntry{}
		for _, log := range logs {
			if log.Type == logType {
				filtered = append(filtered, log)
			}
		}
		logs = filtered
	}

	// Filter by date range
	if startDate != "" {
		start, err := time.Parse(time.RFC3339, startDate)
		if err == nil {
			filtered := []LogEntry{}
			for _, log := range logs {
				if log.Timestamp.After(start) || log.Timestamp.Equal(start) {
					filtered = append(filtered, log)
				}
			}
			logs = filtered
		}
	}

	if endDate != "" {
		end, err := time.Parse(time.RFC3339, endDate)
		if err == nil {
			filtered := []LogEntry{}
			for _, log := range logs {
				if log.Timestamp.Before(end) || log.Timestamp.Equal(end) {
					filtered = append(filtered, log)
				}
			}
			logs = filtered
		}
	}

	// Sort by timestamp (newest first)
	for i := 0; i < len(logs)-1; i++ {
		for j := i + 1; j < len(logs); j++ {
			if logs[i].Timestamp.Before(logs[j].Timestamp) {
				logs[i], logs[j] = logs[j], logs[i]
			}
		}
	}

	return logs
}

