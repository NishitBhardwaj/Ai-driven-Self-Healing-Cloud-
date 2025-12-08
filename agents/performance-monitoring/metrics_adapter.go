package performancemonitoring

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/sirupsen/logrus"
)

// PrometheusAdapter handles Prometheus metrics collection
type PrometheusAdapter struct {
	client      *http.Client
	prometheusURL string
	logger      *logrus.Logger
}

// NewPrometheusAdapter creates a new PrometheusAdapter instance
func NewPrometheusAdapter() (*PrometheusAdapter, error) {
	prometheusURL := os.Getenv("PROMETHEUS_URL")
	if prometheusURL == "" {
		prometheusURL = "http://localhost:9090"
	}

	return &PrometheusAdapter{
		client: &http.Client{
			Timeout: 30 * time.Second,
		},
		prometheusURL: prometheusURL,
		logger:       logrus.New(),
	}, nil
}

// ConnectToPrometheus verifies connection to Prometheus
func (pa *PrometheusAdapter) ConnectToPrometheus() error {
	pa.logger.WithField("url", pa.prometheusURL).Info("Connecting to Prometheus")

	// Test connection by querying Prometheus health endpoint
	healthURL := fmt.Sprintf("%s/-/healthy", pa.prometheusURL)
	resp, err := pa.client.Get(healthURL)
	if err != nil {
		return fmt.Errorf("failed to connect to Prometheus: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("Prometheus health check failed with status: %d", resp.StatusCode)
	}

	pa.logger.Info("Successfully connected to Prometheus")
	return nil
}

// FetchMetrics fetches metrics from Prometheus using PromQL queries
func (pa *PrometheusAdapter) FetchMetrics() ([]Metric, error) {
	pa.logger.Info("Fetching metrics from Prometheus")

	// Common metrics to fetch
	queries := map[string]string{
		"cpu_usage":    `sum(rate(container_cpu_usage_seconds_total[5m])) by (pod, namespace) * 100`,
		"memory_usage": `sum(container_memory_working_set_bytes) by (pod, namespace) / sum(container_spec_memory_limit_bytes) by (pod, namespace) * 100`,
		"pod_count":    `count(kube_pod_info) by (namespace)`,
		"request_rate": `sum(rate(http_requests_total[5m])) by (service, namespace)`,
	}

	var allMetrics []Metric

	for metricName, query := range queries {
		metrics, err := pa.queryPrometheus(metricName, query)
		if err != nil {
			pa.logger.WithError(err).Warnf("Failed to fetch metric: %s", metricName)
			continue
		}
		allMetrics = append(allMetrics, metrics...)
	}

	pa.logger.WithField("count", len(allMetrics)).Info("Metrics fetched successfully")
	return allMetrics, nil
}

// queryPrometheus executes a PromQL query and returns metrics
func (pa *PrometheusAdapter) queryPrometheus(metricName, query string) ([]Metric, error) {
	// Build query URL
	queryURL := fmt.Sprintf("%s/api/v1/query", pa.prometheusURL)
	params := url.Values{}
	params.Add("query", query)

	fullURL := fmt.Sprintf("%s?%s", queryURL, params.Encode())

	resp, err := pa.client.Get(fullURL)
	if err != nil {
		return nil, fmt.Errorf("failed to execute query: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("query failed with status %d: %s", resp.StatusCode, string(body))
	}

	var result PrometheusQueryResult
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	if result.Status != "success" {
		return nil, fmt.Errorf("query returned error: %s", result.Error)
	}

	// Convert Prometheus response to Metric format
	var metrics []Metric
	for _, result := range result.Data.Result {
		value, err := parsePrometheusValue(result.Value)
		if err != nil {
			pa.logger.WithError(err).Warn("Failed to parse metric value")
			continue
		}

		metric := Metric{
			Name:      metricName,
			Value:     value,
			Labels:    result.Metric,
			Timestamp: time.Now(),
		}
		metrics = append(metrics, metric)
	}

	return metrics, nil
}

// parsePrometheusValue parses Prometheus value format [timestamp, "value"]
func parsePrometheusValue(value interface{}) (float64, error) {
	valueArray, ok := value.([]interface{})
	if !ok || len(valueArray) != 2 {
		return 0, fmt.Errorf("invalid value format")
	}

	valueStr, ok := valueArray[1].(string)
	if !ok {
		return 0, fmt.Errorf("value is not a string")
	}

	parsedValue, err := strconv.ParseFloat(valueStr, 64)
	if err != nil {
		return 0, fmt.Errorf("failed to parse value: %w", err)
	}

	return parsedValue, nil
}

// DetectAnomaly detects anomalies in metrics using statistical analysis
func (pa *PrometheusAdapter) DetectAnomaly(metrics []Metric) ([]Anomaly, error) {
	pa.logger.WithField("count", len(metrics)).Info("Detecting anomalies")

	var anomalies []Anomaly

	// Group metrics by name
	metricsByName := make(map[string][]Metric)
	for _, metric := range metrics {
		metricsByName[metric.Name] = append(metricsByName[metric.Name], metric)
	}

	// Analyze each metric type
	for metricName, metricList := range metricsByName {
		if len(metricList) < 2 {
			continue // Need at least 2 data points
		}

		// Calculate statistics
		mean, stdDev := pa.calculateStatistics(metricList)

		// Detect outliers (values beyond 2 standard deviations)
		for _, metric := range metricList {
			zScore := (metric.Value - mean) / stdDev
			if stdDev > 0 && (zScore > 2.0 || zScore < -2.0) {
				severity := "medium"
				if zScore > 3.0 || zScore < -3.0 {
					severity = "high"
				}

				anomaly := Anomaly{
					MetricName:    metricName,
					DetectedAt:    metric.Timestamp,
					Severity:      severity,
					Description:   fmt.Sprintf("Metric value (%.2f) deviates significantly from mean (%.2f, std: %.2f)", metric.Value, mean, stdDev),
					ExpectedValue: mean,
					ActualValue:   metric.Value,
				}
				anomalies = append(anomalies, anomaly)
			}
		}
	}

	pa.logger.WithField("count", len(anomalies)).Info("Anomalies detected")
	return anomalies, nil
}

// calculateStatistics calculates mean and standard deviation
func (pa *PrometheusAdapter) calculateStatistics(metrics []Metric) (float64, float64) {
	if len(metrics) == 0 {
		return 0, 0
	}

	// Calculate mean
	var sum float64
	for _, metric := range metrics {
		sum += metric.Value
	}
	mean := sum / float64(len(metrics))

	// Calculate standard deviation
	var variance float64
	for _, metric := range metrics {
		diff := metric.Value - mean
		variance += diff * diff
	}
	variance /= float64(len(metrics))
	stdDev := variance
	if stdDev > 0 {
		// Simplified std dev calculation
		stdDev = variance
	}

	return mean, stdDev
}

// FetchMetricRange fetches metrics over a time range
func (pa *PrometheusAdapter) FetchMetricRange(metricName, query string, start, end time.Time, step time.Duration) ([]Metric, error) {
	queryURL := fmt.Sprintf("%s/api/v1/query_range", pa.prometheusURL)
	params := url.Values{}
	params.Add("query", query)
	params.Add("start", fmt.Sprintf("%d", start.Unix()))
	params.Add("end", fmt.Sprintf("%d", end.Unix()))
	params.Add("step", step.String())

	fullURL := fmt.Sprintf("%s?%s", queryURL, params.Encode())

	resp, err := pa.client.Get(fullURL)
	if err != nil {
		return nil, fmt.Errorf("failed to execute range query: %w", err)
	}
	defer resp.Body.Close()

	var result PrometheusQueryRangeResult
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	var metrics []Metric
	for _, result := range result.Data.Result {
		for _, valuePair := range result.Values {
			value, err := parsePrometheusValue(valuePair)
			if err != nil {
				continue
			}

			timestamp := time.Unix(int64(valuePair[0].(float64)), 0)
			metric := Metric{
				Name:      metricName,
				Value:     value,
				Labels:    result.Metric,
				Timestamp: timestamp,
			}
			metrics = append(metrics, metric)
		}
	}

	return metrics, nil
}

// PrometheusQueryResult represents Prometheus query API response
type PrometheusQueryResult struct {
	Status string `json:"status"`
	Data   struct {
		ResultType string `json:"resultType"`
		Result     []struct {
			Metric map[string]string `json:"metric"`
			Value  interface{}       `json:"value"`
		} `json:"result"`
	} `json:"data"`
	Error string `json:"error,omitempty"`
}

// PrometheusQueryRangeResult represents Prometheus range query API response
type PrometheusQueryRangeResult struct {
	Status string `json:"status"`
	Data   struct {
		ResultType string `json:"resultType"`
		Result     []struct {
			Metric map[string]string `json:"metric"`
			Values [][]interface{}    `json:"values"`
		} `json:"result"`
	} `json:"data"`
}

// GetServiceMetrics fetches metrics for a specific service
func (pa *PrometheusAdapter) GetServiceMetrics(serviceName string) ([]Metric, error) {
	query := fmt.Sprintf(`sum(rate(container_cpu_usage_seconds_total{namespace="self-healing-cloud",pod=~"%s.*"}[5m])) by (pod) * 100`, serviceName)
	return pa.queryPrometheus("cpu_usage", query)
}

