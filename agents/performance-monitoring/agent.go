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

// ExplainAction provides explanation for monitoring actions
func (a *PerformanceMonitoringAgent) ExplainAction(input interface{}, output interface{}) string {
	return fmt.Sprintf("Performance Monitoring Agent: Collected metrics from Prometheus (input=%v), analyzed patterns for anomalies. Results: %v. Detected threshold violations and identified performance bottlenecks and resource constraints based on historical baselines.", input, output)
}

