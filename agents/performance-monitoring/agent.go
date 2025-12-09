package performancemonitoring

import (
	"fmt"
	"time"

	"github.com/ai-driven-self-healing-cloud/agents/core"
	"github.com/ai-driven-self-healing-cloud/agents/events"
	"github.com/ai-driven-self-healing-cloud/config"
	"github.com/sirupsen/logrus"
)

// PerformanceMonitoringAgent collects Prometheus metrics and detects anomalies
type PerformanceMonitoringAgent struct {
	*core.Agent
	logger     *logrus.Logger
	messageBus config.MessageBus
	analyzer   *MetricsAnalyzer
}

// NewPerformanceMonitoringAgent creates a new Performance Monitoring Agent instance
func NewPerformanceMonitoringAgent() *PerformanceMonitoringAgent {
	baseAgent := core.NewAgent(
		"performance-monitoring-agent",
		"Performance Monitoring Agent",
		"Collects Prometheus metrics and detects anomalies",
	)

	return &PerformanceMonitoringAgent{
		Agent:    baseAgent,
		logger:   config.GetLogger(),
		analyzer: NewMetricsAnalyzer(),
	}
}

// Init initializes the agent
func (a *PerformanceMonitoringAgent) Init() error {
	a.logger.WithField("agent", a.GetName()).Info("Initializing Performance Monitoring Agent")
	
	bus, err := config.ConnectMessageBus()
	if err != nil {
		a.logger.WithError(err).Warn("Message bus not available, continuing without it")
	} else {
		a.messageBus = bus
	}

	return nil
}

// Start begins the agent's operation
func (a *PerformanceMonitoringAgent) Start() error {
	if err := a.Init(); err != nil {
		return err
	}

	a.Status = core.StatusStarting
	a.StartedAt = time.Now()
	a.Error = nil

	// Subscribe to metrics events
	if a.messageBus != nil {
		a.messageBus.Subscribe(events.METRICS_COLLECTED, a.handleMetricsEvent)
	}

	a.Status = core.StatusRunning
	a.logger.WithField("agent", a.GetName()).Info("Performance Monitoring Agent started")
	return nil
}

// Stop gracefully shuts down the agent
func (a *PerformanceMonitoringAgent) Stop() error {
	a.Status = core.StatusStopping
	a.logger.WithField("agent", a.GetName()).Info("Performance Monitoring Agent stopping")
	a.Status = core.StatusStopped
	a.StoppedAt = time.Now()
	return nil
}

// HandleMessage processes incoming messages
func (a *PerformanceMonitoringAgent) HandleMessage(event interface{}) error {
	a.logger.WithField("agent", a.GetName()).Debug("Received monitoring message")
	return nil
}

// handleMetricsEvent handles metrics collected events
func (a *PerformanceMonitoringAgent) handleMetricsEvent(data []byte) {
	a.logger.Info("Metrics event received, analyzing...")
	// Analyze metrics
}

// ExplainAction provides human-readable explanation for monitoring actions
func (a *PerformanceMonitoringAgent) ExplainAction(input interface{}, output interface{}) string {
	var problem, action, reason string
	
	// Parse output to extract findings
	if outputMap, ok := output.(map[string]interface{}); ok {
		if anomalies, ok := outputMap["anomalies"].([]interface{}); ok && len(anomalies) > 0 {
			problem = fmt.Sprintf("%d anomaly(ies) in system metrics", len(anomalies))
		}
		if thresholdViolations, ok := outputMap["threshold_violations"].([]interface{}); ok && len(thresholdViolations) > 0 {
			if problem != "" {
				problem += fmt.Sprintf(" and %d threshold violation(s)", len(thresholdViolations))
			} else {
				problem = fmt.Sprintf("%d threshold violation(s)", len(thresholdViolations))
			}
		}
		if actionTaken, ok := outputMap["action"].(string); ok {
			action = actionTaken
		}
	}
	
	// Default values
	if problem == "" {
		problem = "system metrics were collected and analyzed"
	}
	if action == "" {
		action = "analyzed the metrics"
	}
	reason = "to identify performance bottlenecks and ensure system health"
	
	// Format explanation
	explanation := fmt.Sprintf("The agent detected that %s and %s %s.", problem, action, reason)
	
	return explanation
}

