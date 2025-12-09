package performancemonitoring

import (
	"bytes"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"time"

	"github.com/sirupsen/logrus"
)

// MetricsAnalyzer analyzes Prometheus metrics and detects anomalies
type MetricsAnalyzer struct {
	logger *logrus.Logger
}

// NewMetricsAnalyzer creates a new MetricsAnalyzer instance
func NewMetricsAnalyzer() *MetricsAnalyzer {
	return &MetricsAnalyzer{
		logger: logrus.New(),
	}
}

// Metric represents a Prometheus metric
type Metric struct {
	Name      string                 `json:"name"`
	Value     float64                `json:"value"`
	Labels    map[string]string     `json:"labels"`
	Timestamp time.Time              `json:"timestamp"`
	Metadata  map[string]interface{} `json:"metadata"`
}

// Anomaly represents a detected anomaly
type Anomaly struct {
	MetricName    string    `json:"metric_name"`
	DetectedAt    time.Time `json:"detected_at"`
	Severity      string    `json:"severity"`
	Description   string    `json:"description"`
	ExpectedValue float64   `json:"expected_value"`
	ActualValue   float64   `json:"actual_value"`
}

// AnalyzeMetrics analyzes metrics and detects anomalies using AI Engine (feeds data to all models)
func (ma *MetricsAnalyzer) AnalyzeMetrics(metrics []Metric) ([]Anomaly, error) {
	ma.logger.WithField("count", len(metrics)).Info("Analyzing metrics using AI Engine")
	
	// Log action trigger to ELK Stack
	ma.logActionTriggerToELK("analyze_metrics", metrics)

	// Feed metrics to AI Engine
	aiResults, err := ma.feedMetricsToAI(metrics)
	if err != nil {
		ma.logger.WithError(err).Warn("AI Engine analysis failed, using fallback")
		return ma.fallbackAnomalyDetection(metrics), nil
	}

	// Convert AI results to anomalies
	anomalies := ma.convertAIResultsToAnomalies(aiResults, metrics)
	
	// Record metrics
	for range anomalies {
		recordAnomalyDetected()
	}
	
	// Update CPU and memory usage metrics
	for _, metric := range metrics {
		if metric.Name == "cpu_usage" {
			setCPUUsage(metric.Service, metric.Node, metric.Value)
		} else if metric.Name == "memory_usage" {
			setMemoryUsage(metric.Service, metric.Node, metric.Value)
		}
	}
	
	return anomalies, nil
}

// feedMetricsToAI feeds metrics to all AI models
func (ma *MetricsAnalyzer) feedMetricsToAI(metrics []Metric) (map[string]interface{}, error) {
	// Get script path
	scriptPath := filepath.Join(filepath.Dir(os.Args[0]), "agents", "performance-monitoring", "ai_integration_wrapper.py")
	if _, err := os.Stat(scriptPath); os.IsNotExist(err) {
		scriptPath = "agents/performance-monitoring/ai_integration_wrapper.py"
	}

	// Convert metrics to map format
	metricsMap := make(map[string][]float64)
	for _, metric := range metrics {
		if _, exists := metricsMap[metric.Name]; !exists {
			metricsMap[metric.Name] = []float64{}
		}
		metricsMap[metric.Name] = append(metricsMap[metric.Name], metric.Value)
	}

	input := map[string]interface{}{
		"metrics": metricsMap,
	}

	inputJSON, err := json.Marshal(input)
	if err != nil {
		return nil, err
	}

	// Call Python script
	cmd := exec.Command("python3", scriptPath, "feed_metrics_to_models")
	cmd.Stdin = bytes.NewReader(inputJSON)
	output, err := cmd.Output()
	if err != nil {
		return nil, err
	}

	// Parse output
	var result map[string]interface{}
	if err := json.Unmarshal(output, &result); err != nil {
		return nil, err
	}

	return result, nil
}

// convertAIResultsToAnomalies converts AI results to Anomaly structs
func (ma *MetricsAnalyzer) convertAIResultsToAnomalies(aiResults map[string]interface{}, metrics []Metric) []Anomaly {
	anomalies := []Anomaly{}

	// Check forecast results
	if forecast, ok := aiResults["forecast"].(map[string]interface{}); ok {
		// Check for predicted anomalies
		if cpuForecast, ok := forecast["cpu_forecast"].([]interface{}); ok && len(cpuForecast) > 0 {
			if cpu, ok := cpuForecast[0].(float64); ok && cpu > 80.0 {
				anomalies = append(anomalies, Anomaly{
					MetricName:    "cpu_usage",
					DetectedAt:    time.Now(),
					Severity:      "high",
					Description:   "AI Engine predicted high CPU usage",
					ExpectedValue: 80.0,
					ActualValue:   cpu,
				})
			}
		}
	}

	// Check anomaly trends
	if trends, ok := aiResults["anomaly_trends"].(map[string]interface{}); ok {
		if trend, ok := trends["trend"].(string); ok && trend != "normal" {
			anomalies = append(anomalies, Anomaly{
				MetricName:    "system",
				DetectedAt:    time.Now(),
				Severity:      "medium",
				Description:   fmt.Sprintf("AI Engine detected %s anomaly trend", trend),
				ExpectedValue: 0.0,
				ActualValue:   1.0,
			})
		}
	}

	// Fallback to basic threshold check if no AI anomalies
	if len(anomalies) == 0 {
		return ma.fallbackAnomalyDetection(metrics)
	}

	return anomalies
}

// fallbackAnomalyDetection provides fallback when AI is unavailable
func (ma *MetricsAnalyzer) fallbackAnomalyDetection(metrics []Metric) []Anomaly {
	anomalies := []Anomaly{}
	for _, metric := range metrics {
		if metric.Value > 100.0 {
			anomalies = append(anomalies, Anomaly{
				MetricName:    metric.Name,
				DetectedAt:    time.Now(),
				Severity:      "high",
				Description:   "Metric value exceeds threshold",
				ExpectedValue: 80.0,
				ActualValue:   metric.Value,
			})
		}
	}
	return anomalies
}

// CollectMetrics collects metrics from Prometheus
func (ma *MetricsAnalyzer) CollectMetrics(prometheusURL string) ([]Metric, error) {
	ma.logger.WithField("url", prometheusURL).Info("Collecting metrics from Prometheus")

	// TODO: Implement actual Prometheus query in Phase 5
	metrics := []Metric{
		{
			Name:      "cpu_usage",
			Value:     75.5,
			Labels:    map[string]string{"service": "api"},
			Timestamp: time.Now(),
		},
		{
			Name:      "memory_usage",
			Value:     60.2,
			Labels:    map[string]string{"service": "api"},
			Timestamp: time.Now(),
		},
	}

	return metrics, nil
}

