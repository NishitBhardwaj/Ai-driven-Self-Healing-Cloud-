package performancemonitoring

import (
	"net/http"

	"github.com/ai-driven-self-healing-cloud/config/monitoring"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

// StartMetricsServer starts the Prometheus metrics HTTP server
func StartMetricsServer(port string) error {
	// Register metrics
	_ = monitoring.GetMetricsRegistry()
	
	// Start HTTP server for metrics
	http.Handle("/metrics", promhttp.Handler())
	return http.ListenAndServe(":"+port, nil)
}

