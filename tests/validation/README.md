# System Validation - Phase 8, Part 4

This directory contains validation tests and scripts to verify that the testing, logging, and monitoring systems are working correctly.

## Overview

The validation system checks:
- ✅ Unit tests and integration tests for all agents
- ✅ Prometheus metrics collection and display
- ✅ Logstash log parsing and Elasticsearch storage
- ✅ Kibana dashboard functionality
- ✅ Grafana dashboard real-time data
- ✅ Alerting rules and critical thresholds

## Test Files

### 1. System Validation Tests (`system_validation_test.go`)

Tests for basic system connectivity:
- `TestPrometheusMetricsCollection`: Verifies Prometheus is collecting metrics
- `TestAgentMetricsExposed`: Verifies agents expose metrics on `/metrics` endpoints
- `TestElasticsearchConnection`: Verifies Elasticsearch is accessible
- `TestLogstashConnection`: Verifies Logstash is configured
- `TestKibanaConnection`: Verifies Kibana is accessible
- `TestGrafanaConnection`: Verifies Grafana is accessible
- `TestElasticsearchIndexExists`: Verifies agent-logs index exists
- `TestPrometheusTargets`: Verifies Prometheus has targets configured
- `TestGrafanaDataSources`: Verifies Grafana has data sources configured
- `TestAlertingRules`: Verifies Prometheus alerting rules are loaded

### 2. Logging Validation Tests (`logging_validation_test.go`)

Tests for logging system:
- `TestLogstashParsesLogs`: Verifies Logstash correctly parses logs
- `TestElasticsearchReceivesLogs`: Verifies Elasticsearch receives logs from Logstash
- `TestKibanaDisplaysLogs`: Verifies Kibana can display logs
- `TestLogStructure`: Verifies logs have expected structure
- `TestLogTypes`: Verifies different log types are being logged

### 3. Monitoring Validation Tests (`monitoring_validation_test.go`)

Tests for monitoring system:
- `TestGrafanaDashboardsExist`: Verifies Grafana dashboards exist
- `TestGrafanaRealTimeData`: Verifies Grafana shows real-time data
- `TestPrometheusMetricsDisplayed`: Verifies Prometheus metrics are displayed correctly
- `TestSystemHealthMetrics`: Verifies system health metrics are available
- `TestAgentPerformanceMetrics`: Verifies agent performance metrics are available
- `TestResourceUsageMetrics`: Verifies resource usage metrics are available
- `TestEventFlowMetrics`: Verifies event flow metrics are available
- `TestErrorRateMetrics`: Verifies error rate metrics are available

### 4. Alerting Validation Tests (`alerting_validation_test.go`)

Tests for alerting system:
- `TestAlertingRulesLoaded`: Verifies Prometheus alerting rules are loaded
- `TestCriticalThresholdAlerts`: Verifies critical threshold alerts are configured
- `TestWarningThresholdAlerts`: Verifies warning threshold alerts are configured
- `TestAlertExpressions`: Verifies alert expressions are valid

## Running Validation

### Run All Validation Tests

```bash
# Linux/Mac
go test ./tests/validation/... -v

# Windows
go test ./tests/validation/... -v
```

### Run Validation Script

```bash
# Linux/Mac
chmod +x tests/validation/run_validation.sh
./tests/validation/run_validation.sh

# Windows
tests\validation\run_validation.bat
```

### Generate Validation Report

```bash
go run tests/validation/generate_validation_report.go
```

This will generate `validation_report.json` with detailed validation results.

## Validation Checklist

### ✅ Unit Tests and Integration Tests

- [ ] Unit tests for all agents pass
- [ ] Integration tests for multi-agent communication pass
- [ ] Test coverage is adequate

### ✅ Prometheus Metrics Collection

- [ ] Prometheus is accessible at http://localhost:9090
- [ ] All agent metrics endpoints are configured
- [ ] Metrics are being collected
- [ ] Metrics are queryable via Prometheus API

### ✅ Logstash and Elasticsearch

- [ ] Elasticsearch is accessible at http://localhost:9200
- [ ] Logstash is processing logs
- [ ] Agent-logs index exists in Elasticsearch
- [ ] Logs are being stored in Elasticsearch
- [ ] Log structure is correct

### ✅ Kibana Dashboards

- [ ] Kibana is accessible at http://localhost:5601
- [ ] Kibana can connect to Elasticsearch
- [ ] Agent-logs index pattern is created
- [ ] Dashboards display logs correctly

### ✅ Grafana Dashboards

- [ ] Grafana is accessible at http://localhost:3000
- [ ] Prometheus data source is configured
- [ ] Dashboards are loaded
- [ ] Dashboards show real-time data
- [ ] System health dashboard works
- [ ] Agent performance dashboard works
- [ ] Resource usage dashboard works
- [ ] Event flows dashboard works
- [ ] Error rates dashboard works

### ✅ Alerting

- [ ] Alerting rules are loaded in Prometheus
- [ ] Critical alerts are configured
- [ ] Warning alerts are configured
- [ ] Alert expressions are valid
- [ ] Alerts can be triggered

## Expected Results

### All Services Running

If all services are running, you should see:
- ✅ Prometheus: Accessible and collecting metrics
- ✅ Elasticsearch: Accessible and storing logs
- ✅ Kibana: Accessible and displaying logs
- ✅ Grafana: Accessible and showing dashboards
- ✅ All agent metrics endpoints: Responding (if agents are running)

### Services Not Running

If services are not running, tests will:
- ⚠️ Skip tests that require services
- ✅ Still validate configuration files exist
- ✅ Still validate test structure

## Troubleshooting

### Prometheus Not Accessible

1. Check if Prometheus is running: `docker ps | grep prometheus`
2. Check Prometheus logs: `docker logs prometheus`
3. Verify configuration: `config/monitoring/prometheus.yml`

### Elasticsearch Not Accessible

1. Check if Elasticsearch is running: `docker ps | grep elasticsearch`
2. Check Elasticsearch logs: `docker logs elasticsearch`
3. Verify configuration: `config/logging/elasticsearch.yml`

### Kibana Not Accessible

1. Check if Kibana is running: `docker ps | grep kibana`
2. Check Kibana logs: `docker logs kibana`
3. Verify Elasticsearch connection: `config/logging/kibana.yml`

### Grafana Not Accessible

1. Check if Grafana is running: `docker ps | grep grafana`
2. Check Grafana logs: `docker logs grafana`
3. Verify Prometheus data source: `monitoring/grafana/provisioning/datasources/prometheus.yml`

### Agent Metrics Not Available

1. Check if agents are running
2. Verify metrics endpoints are exposed
3. Check Prometheus configuration includes agent targets
4. Verify agents are using Prometheus client libraries

## Next Steps

After validation:
1. **Fix Issues**: Address any failed validations
2. **Review Reports**: Check validation_report.json for details
3. **Monitor**: Use Grafana and Kibana to monitor system
4. **Test Alerts**: Trigger alerts to verify they work
5. **Document**: Update documentation with any findings

