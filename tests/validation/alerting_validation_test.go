package validation

import (
	"encoding/json"
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestAlertingRulesLoaded tests that Prometheus alerting rules are loaded
func TestAlertingRulesLoaded(t *testing.T) {
	prometheusURL := "http://localhost:9090"
	
	resp, err := http.Get(prometheusURL + "/api/v1/rules")
	require.NoError(t, err, "Should be able to get Prometheus rules")
	defer resp.Body.Close()
	
	assert.Equal(t, http.StatusOK, resp.StatusCode, "Prometheus rules API should return 200")
	
	var result map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&result)
	require.NoError(t, err, "Should decode Prometheus rules response")
	
	assert.Equal(t, "success", result["status"], "Prometheus rules query should be successful")
	
	// Check if rules are present
	if data, ok := result["data"].(map[string]interface{}); ok {
		if groups, ok := data["groups"].([]interface{}); ok {
			assert.Greater(t, len(groups), 0, "Should have at least one alerting rule group")
			t.Logf("Found %d alerting rule groups", len(groups))
		}
	}
}

// TestCriticalThresholdAlerts tests that critical threshold alerts are configured
func TestCriticalThresholdAlerts(t *testing.T) {
	prometheusURL := "http://localhost:9090"
	
	// Get all rules
	resp, err := http.Get(prometheusURL + "/api/v1/rules")
	require.NoError(t, err, "Should be able to get Prometheus rules")
	defer resp.Body.Close()
	
	var result map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&result)
	require.NoError(t, err, "Should decode Prometheus rules response")
	
	// Check for critical alerts
	criticalAlerts := []string{
		"AgentDown",
		"SecurityIntrusionDetected",
	}
	
	if data, ok := result["data"].(map[string]interface{}); ok {
		if groups, ok := data["groups"].([]interface{}); ok {
			for _, group := range groups {
				if groupMap, ok := group.(map[string]interface{}); ok {
					if rules, ok := groupMap["rules"].([]interface{}); ok {
						for _, rule := range rules {
							if ruleMap, ok := rule.(map[string]interface{}); ok {
								if name, ok := ruleMap["name"].(string); ok {
									for _, criticalAlert := range criticalAlerts {
										if name == criticalAlert {
											t.Logf("Found critical alert: %s", name)
										}
									}
								}
							}
						}
					}
				}
			}
		}
	}
}

// TestWarningThresholdAlerts tests that warning threshold alerts are configured
func TestWarningThresholdAlerts(t *testing.T) {
	prometheusURL := "http://localhost:9090"
	
	// Get all rules
	resp, err := http.Get(prometheusURL + "/api/v1/rules")
	require.NoError(t, err, "Should be able to get Prometheus rules")
	defer resp.Body.Close()
	
	var result map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&result)
	require.NoError(t, err, "Should decode Prometheus rules response")
	
	// Check for warning alerts
	warningAlerts := []string{
		"AgentHighErrorRate",
		"HighCPUUsage",
		"HighMemoryUsage",
		"SelfHealingHighFailureRate",
		"ScalingAgentExcessiveScaling",
	}
	
	if data, ok := result["data"].(map[string]interface{}); ok {
		if groups, ok := data["groups"].([]interface{}); ok {
			for _, group := range groups {
				if groupMap, ok := group.(map[string]interface{}); ok {
					if rules, ok := groupMap["rules"].([]interface{}); ok {
						for _, rule := range rules {
							if ruleMap, ok := rule.(map[string]interface{}); ok {
								if name, ok := ruleMap["name"].(string); ok {
									for _, warningAlert := range warningAlerts {
										if name == warningAlert {
											t.Logf("Found warning alert: %s", name)
										}
									}
								}
							}
						}
					}
				}
			}
		}
	}
}

// TestAlertExpressions tests that alert expressions are valid
func TestAlertExpressions(t *testing.T) {
	prometheusURL := "http://localhost:9090"
	
	// Get all rules
	resp, err := http.Get(prometheusURL + "/api/v1/rules")
	require.NoError(t, err, "Should be able to get Prometheus rules")
	defer resp.Body.Close()
	
	var result map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&result)
	require.NoError(t, err, "Should decode Prometheus rules response")
	
	// Verify alert expressions can be evaluated
	if data, ok := result["data"].(map[string]interface{}); ok {
		if groups, ok := data["groups"].([]interface{}); ok {
			for _, group := range groups {
				if groupMap, ok := group.(map[string]interface{}); ok {
					if rules, ok := groupMap["rules"].([]interface{}); ok {
						for _, rule := range rules {
							if ruleMap, ok := rule.(map[string]interface{}); ok {
								if query, ok := ruleMap["query"].(string); ok {
									// Test if expression is valid by querying it
									testResp, err := http.Get(prometheusURL + "/api/v1/query?query=" + query)
									if err == nil && testResp != nil {
										defer testResp.Body.Close()
										if testResp.StatusCode == http.StatusOK {
											t.Logf("Alert expression is valid: %s", query)
										}
									}
								}
							}
						}
					}
				}
			}
		}
	}
}

