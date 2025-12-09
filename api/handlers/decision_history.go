package handlers

import (
	"encoding/json"
	"net/http"
	"strconv"
	"time"

	"github.com/sirupsen/logrus"
)

// DecisionHistoryHandler handles decision history API requests
type DecisionHistoryHandler struct {
	logger *logrus.Logger
}

// NewDecisionHistoryHandler creates a new decision history handler
func NewDecisionHistoryHandler(logger *logrus.Logger) *DecisionHistoryHandler {
	return &DecisionHistoryHandler{
		logger: logger,
	}
}

// DecisionHistoryResponse represents the response for decision history
type DecisionHistoryResponse struct {
	Decisions []Decision `json:"decisions"`
	Total     int        `json:"total"`
	Page      int        `json:"page"`
	PageSize  int        `json:"page_size"`
	HasMore   bool       `json:"has_more"`
}

// Decision represents a decision made by an agent
type Decision struct {
	ID              string                 `json:"id"`
	AgentID         string                 `json:"agent_id"`
	AgentName       string                 `json:"agent_name"`
	Mode            string                 `json:"mode"` // "auto" or "manual"
	Problem         string                 `json:"problem"`
	Reasoning       string                 `json:"reasoning"`
	ActionTaken     string                 `json:"action_taken"`
	Explanation     string                 `json:"explanation"`
	Confidence      float64                `json:"confidence"`
	SelectedOption  *ActionOption          `json:"selected_option,omitempty"`
	Options         []ActionOption         `json:"options,omitempty"`
	ReasoningChain  []ReasoningStep        `json:"reasoning_chain,omitempty"`
	AlternativeActions []string            `json:"alternative_actions,omitempty"`
	ExecutionResult map[string]interface{} `json:"execution_result,omitempty"`
	Timestamp       time.Time              `json:"timestamp"`
	Status          string                 `json:"status"` // "pending", "executed", "rejected"
}

// ActionOption represents an action option in a decision
type ActionOption struct {
	ID            string  `json:"id"`
	Description   string  `json:"description"`
	Reasoning     string  `json:"reasoning"`
	Risk          string  `json:"risk"`
	Impact        string  `json:"impact"`
	EstimatedCost float64 `json:"estimated_cost"`
}

// ReasoningStep represents a step in the reasoning chain
type ReasoningStep struct {
	StepNumber int                    `json:"step_number"`
	Description string                 `json:"description"`
	Reasoning   string                 `json:"reasoning"`
	Input       map[string]interface{} `json:"input,omitempty"`
	Output      map[string]interface{} `json:"output,omitempty"`
}

// GetDecisionHistory handles GET /api/agents/decision-history
func (h *DecisionHistoryHandler) GetDecisionHistory(w http.ResponseWriter, r *http.Request) {
	h.logger.WithField("endpoint", "/api/agents/decision-history").Info("Handling decision history request")

	// Parse query parameters
	query := r.URL.Query()
	page, _ := strconv.Atoi(query.Get("page"))
	if page < 1 {
		page = 1
	}
	pageSize, _ := strconv.Atoi(query.Get("page_size"))
	if pageSize < 1 || pageSize > 1000 {
		pageSize = 50
	}
	agentID := query.Get("agent_id")
	mode := query.Get("mode")
	status := query.Get("status")
	startDate := query.Get("start_date")
	endDate := query.Get("end_date")

	// Get decisions (in production, this would query a database)
	decisions := h.getDecisions(agentID, mode, status, startDate, endDate)

	// Paginate
	total := len(decisions)
	start := (page - 1) * pageSize
	end := start + pageSize
	if start > total {
		start = total
	}
	if end > total {
		end = total
	}

	var paginatedDecisions []Decision
	if start < total {
		paginatedDecisions = decisions[start:end]
	} else {
		paginatedDecisions = []Decision{}
	}

	response := DecisionHistoryResponse{
		Decisions: paginatedDecisions,
		Total:     total,
		Page:      page,
		PageSize:  pageSize,
		HasMore:   end < total,
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(response)
}

// getDecisions retrieves decisions (in production, this would query a database)
func (h *DecisionHistoryHandler) getDecisions(agentID, mode, status, startDate, endDate string) []Decision {
	// Generate sample decisions
	decisions := []Decision{
		{
			ID:          "decision-1",
			AgentID:     "self-healing-001",
			AgentName:   "Self-Healing Agent",
			Mode:        "auto",
			Problem:     "Pod 'web-app-123' is in crash loop",
			Reasoning:   "Detected repeated pod crashes. Analysis shows memory leak in application code.",
			ActionTaken: "restart_pod",
			Explanation: "Pod was restarted due to crash loop detection. The system detected repeated pod crashes and automatically restarted the pod to restore service.",
			Confidence:  0.95,
			SelectedOption: &ActionOption{
				ID:          "restart_pod",
				Description: "Restart the failed pod",
				Reasoning:   "Pod is in crash loop, restarting should resolve the issue",
				Risk:        "low",
				Impact:      "medium",
			},
			ReasoningChain: []ReasoningStep{
				{
					StepNumber: 1,
					Description: "Problem Detection",
					Reasoning:   "Detected pod crash loop",
				},
				{
					StepNumber: 2,
					Description: "Analysis",
					Reasoning:   "Analyzed crash logs and determined memory leak",
				},
				{
					StepNumber: 3,
					Description: "Action Selection",
					Reasoning:   "Selected restart_pod as best action",
				},
				{
					StepNumber: 4,
					Description: "Execution",
					Reasoning:   "Executed pod restart successfully",
				},
			},
			AlternativeActions: []string{"rebuild_deployment", "rollback"},
			ExecutionResult: map[string]interface{}{
				"status":   "success",
				"pod_name": "web-app-123",
			},
			Timestamp: time.Now().Add(-5 * time.Minute),
			Status:    "executed",
		},
		{
			ID:          "decision-2",
			AgentID:     "scaling-001",
			AgentName:   "Scaling Agent",
			Mode:        "manual",
			Problem:     "CPU usage is at 95% and response times are increasing",
			Reasoning:   "CPU usage has been above 90% for 5 minutes. The system needs more capacity to handle the current load.",
			ActionTaken: "scale_up",
			Explanation: "CPU usage exceeded 95% threshold. Scaled up from 3 to 5 replicas to distribute load and reduce CPU usage per instance.",
			Confidence:  0.85,
			SelectedOption: &ActionOption{
				ID:            "scale_up",
				Description:   "Scale up from 3 to 5 replicas",
				Reasoning:     "Adding more replicas will distribute the load and reduce CPU usage per instance",
				Risk:          "low",
				Impact:        "high",
				EstimatedCost: 15.50,
			},
			Options: []ActionOption{
				{
					ID:            "scale_up",
					Description:   "Scale up from 3 to 5 replicas",
					Reasoning:     "Adding more replicas will distribute the load",
					Risk:          "low",
					Impact:        "high",
					EstimatedCost: 15.50,
				},
				{
					ID:            "optimize",
					Description:   "Optimize existing resources",
					Reasoning:     "Optimize the current deployment configuration",
					Risk:          "medium",
					Impact:        "medium",
					EstimatedCost: 0.0,
				},
			},
			ReasoningChain: []ReasoningStep{
				{
					StepNumber: 1,
					Description: "CPU Usage Detection",
					Reasoning:   "CPU usage exceeds 85% threshold",
				},
				{
					StepNumber: 2,
					Description: "Historical Data Analysis",
					Reasoning:   "Checked historical data for load trends",
				},
				{
					StepNumber: 3,
					Description: "Transformer Forecasting",
					Reasoning:   "Predicted future demand using Transformer forecasting",
				},
				{
					StepNumber: 4,
					Description: "User Confirmation",
					Reasoning:   "User approved scale_up action",
				},
				{
					StepNumber: 5,
					Description: "Action Execution",
					Reasoning:   "Scaling action executed successfully",
				},
			},
			AlternativeActions: []string{"optimize", "restart_service"},
			ExecutionResult: map[string]interface{}{
				"status":   "success",
				"replicas": 5,
			},
			Timestamp: time.Now().Add(-10 * time.Minute),
			Status:    "executed",
		},
		{
			ID:          "decision-3",
			AgentID:     "security-001",
			AgentName:   "Security Agent",
			Mode:        "auto",
			Problem:     "Suspicious activity detected from IP 192.168.1.100",
			Reasoning:   "Multiple failed login attempts detected from unknown IP address",
			ActionTaken: "block_ip",
			Explanation: "Multiple failed login attempts detected from suspicious IP. Blocked the IP address to prevent potential security breach.",
			Confidence:  0.92,
			SelectedOption: &ActionOption{
				ID:          "block_ip",
				Description: "Block the suspicious IP address",
				Reasoning:   "Prevent further attack attempts",
				Risk:        "low",
				Impact:      "high",
			},
			ReasoningChain: []ReasoningStep{
				{
					StepNumber: 1,
					Description: "Threat Detection",
					Reasoning:   "Detected multiple failed login attempts",
				},
				{
					StepNumber: 2,
					Description: "Risk Assessment",
					Reasoning:   "Assessed threat level as high",
				},
				{
					StepNumber: 3,
					Description: "Action Selection",
					Reasoning:   "Selected block_ip as immediate response",
				},
				{
					StepNumber: 4,
					Description: "Execution",
					Reasoning:   "Blocked IP address successfully",
				},
			},
			AlternativeActions: []string{"investigate", "alert"},
			ExecutionResult: map[string]interface{}{
				"status": "success",
				"ip":     "192.168.1.100",
			},
			Timestamp: time.Now().Add(-15 * time.Minute),
			Status:    "executed",
		},
	}

	// Filter by agent ID
	if agentID != "" {
		filtered := []Decision{}
		for _, decision := range decisions {
			if decision.AgentID == agentID {
				filtered = append(filtered, decision)
			}
		}
		decisions = filtered
	}

	// Filter by mode
	if mode != "" {
		filtered := []Decision{}
		for _, decision := range decisions {
			if decision.Mode == mode {
				filtered = append(filtered, decision)
			}
		}
		decisions = filtered
	}

	// Filter by status
	if status != "" {
		filtered := []Decision{}
		for _, decision := range decisions {
			if decision.Status == status {
				filtered = append(filtered, decision)
			}
		}
		decisions = filtered
	}

	// Filter by date range
	if startDate != "" {
		start, err := time.Parse(time.RFC3339, startDate)
		if err == nil {
			filtered := []Decision{}
			for _, decision := range decisions {
				if decision.Timestamp.After(start) || decision.Timestamp.Equal(start) {
					filtered = append(filtered, decision)
				}
			}
			decisions = filtered
		}
	}

	if endDate != "" {
		end, err := time.Parse(time.RFC3339, endDate)
		if err == nil {
			filtered := []Decision{}
			for _, decision := range decisions {
				if decision.Timestamp.Before(end) || decision.Timestamp.Equal(end) {
					filtered = append(filtered, decision)
				}
			}
			decisions = filtered
		}
	}

	// Sort by timestamp (newest first)
	for i := 0; i < len(decisions)-1; i++ {
		for j := i + 1; j < len(decisions); j++ {
			if decisions[i].Timestamp.Before(decisions[j].Timestamp) {
				decisions[i], decisions[j] = decisions[j], decisions[i]
			}
		}
	}

	return decisions
}

