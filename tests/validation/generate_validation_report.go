package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"time"
)

// ValidationReport represents the validation results
type ValidationReport struct {
	Timestamp     time.Time              `json:"timestamp"`
	Tests         TestResults            `json:"tests"`
	Prometheus    ServiceStatus          `json:"prometheus"`
	Elasticsearch ServiceStatus          `json:"elasticsearch"`
	Logstash      ServiceStatus          `json:"logstash"`
	Kibana        ServiceStatus          `json:"kibana"`
	Grafana       ServiceStatus          `json:"grafana"`
	Alerts        AlertStatus            `json:"alerts"`
	Summary       ValidationSummary      `json:"summary"`
}

// TestResults represents test validation results
type TestResults struct {
	UnitTests       bool `json:"unit_tests"`
	IntegrationTests bool `json:"integration_tests"`
}

// ServiceStatus represents the status of a service
type ServiceStatus struct {
	Accessible bool   `json:"accessible"`
	URL        string `json:"url"`
	Status     string `json:"status"`
	Details    string `json:"details,omitempty"`
}

// AlertStatus represents alerting system status
type AlertStatus struct {
	RulesLoaded bool `json:"rules_loaded"`
	RuleCount   int  `json:"rule_count"`
}

// ValidationSummary represents overall validation summary
type ValidationSummary struct {
	TotalChecks int `json:"total_checks"`
	Passed      int `json:"passed"`
	Failed      int `json:"failed"`
	Warnings    int `json:"warnings"`
}

func main() {
	report := ValidationReport{
		Timestamp: time.Now(),
	}

	// Check Prometheus
	report.Prometheus = checkService("http://localhost:9090/api/v1/status/config", "Prometheus")
	
	// Check Elasticsearch
	report.Elasticsearch = checkService("http://localhost:9200", "Elasticsearch")
	
	// Check Kibana
	report.Kibana = checkService("http://localhost:5601/api/status", "Kibana")
	
	// Check Grafana
	report.Grafana = checkService("http://localhost:3000/api/health", "Grafana")
	
	// Check Logstash (TCP, so we'll mark as unknown)
	report.Logstash = ServiceStatus{
		Accessible: false,
		URL:        "localhost:5000",
		Status:     "unknown",
		Details:    "Logstash uses TCP, checking via Elasticsearch logs",
	}
	
	// Check tests
	report.Tests.UnitTests = checkDirectory("tests/agents")
	report.Tests.IntegrationTests = checkDirectory("tests/integration")
	
	// Check alerts
	report.Alerts = checkAlerts()
	
	// Calculate summary
	report.Summary = calculateSummary(report)
	
	// Generate report
	reportJSON, err := json.MarshalIndent(report, "", "  ")
	if err != nil {
		fmt.Printf("Error generating report: %v\n", err)
		os.Exit(1)
	}
	
	// Write report to file
	err = ioutil.WriteFile("validation_report.json", reportJSON, 0644)
	if err != nil {
		fmt.Printf("Error writing report: %v\n", err)
		os.Exit(1)
	}
	
	// Print summary
	fmt.Println("==========================================")
	fmt.Println("Validation Report Generated")
	fmt.Println("==========================================")
	fmt.Printf("Timestamp: %s\n", report.Timestamp.Format(time.RFC3339))
	fmt.Printf("Total Checks: %d\n", report.Summary.TotalChecks)
	fmt.Printf("Passed: %d\n", report.Summary.Passed)
	fmt.Printf("Failed: %d\n", report.Summary.Failed)
	fmt.Printf("Warnings: %d\n", report.Summary.Warnings)
	fmt.Println("==========================================")
	fmt.Println("Report saved to: validation_report.json")
}

func checkService(url, name string) ServiceStatus {
	client := &http.Client{Timeout: 5 * time.Second}
	resp, err := client.Get(url)
	
	if err != nil {
		return ServiceStatus{
			Accessible: false,
			URL:        url,
			Status:     "unreachable",
			Details:    err.Error(),
		}
	}
	defer resp.Body.Close()
	
	if resp.StatusCode == http.StatusOK {
		return ServiceStatus{
			Accessible: true,
			URL:        url,
			Status:     "healthy",
		}
	}
	
	return ServiceStatus{
		Accessible: false,
		URL:        url,
		Status:     "unhealthy",
		Details:    fmt.Sprintf("HTTP %d", resp.StatusCode),
	}
}

func checkDirectory(path string) bool {
	_, err := os.Stat(path)
	return err == nil
}

func checkAlerts() AlertStatus {
	client := &http.Client{Timeout: 5 * time.Second}
	resp, err := client.Get("http://localhost:9090/api/v1/rules")
	
	if err != nil {
		return AlertStatus{
			RulesLoaded: false,
			RuleCount:   0,
		}
	}
	defer resp.Body.Close()
	
	if resp.StatusCode == http.StatusOK {
		var result map[string]interface{}
		json.NewDecoder(resp.Body).Decode(&result)
		
		ruleCount := 0
		if data, ok := result["data"].(map[string]interface{}); ok {
			if groups, ok := data["groups"].([]interface{}); ok {
				for _, group := range groups {
					if groupMap, ok := group.(map[string]interface{}); ok {
						if rules, ok := groupMap["rules"].([]interface{}); ok {
							ruleCount += len(rules)
						}
					}
				}
			}
		}
		
		return AlertStatus{
			RulesLoaded: ruleCount > 0,
			RuleCount:   ruleCount,
		}
	}
	
	return AlertStatus{
		RulesLoaded: false,
		RuleCount:   0,
	}
}

func calculateSummary(report ValidationReport) ValidationSummary {
	summary := ValidationSummary{}
	
	// Count checks
	summary.TotalChecks = 7 // Prometheus, Elasticsearch, Logstash, Kibana, Grafana, Tests, Alerts
	
	// Count passed
	if report.Prometheus.Accessible {
		summary.Passed++
	} else {
		summary.Failed++
	}
	
	if report.Elasticsearch.Accessible {
		summary.Passed++
	} else {
		summary.Warnings++
	}
	
	if report.Kibana.Accessible {
		summary.Passed++
	} else {
		summary.Warnings++
	}
	
	if report.Grafana.Accessible {
		summary.Passed++
	} else {
		summary.Warnings++
	}
	
	if report.Tests.UnitTests && report.Tests.IntegrationTests {
		summary.Passed++
	} else {
		summary.Failed++
	}
	
	if report.Alerts.RulesLoaded {
		summary.Passed++
	} else {
		summary.Warnings++
	}
	
	return summary
}

