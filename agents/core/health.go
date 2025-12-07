package core

import "time"

// HealthStatus represents the health status of an agent or system
type HealthStatus struct {
	Healthy   bool
	Status    string
	Message   string
	Timestamp time.Time
}

// HealthCheckResult represents a health check result with metadata
type HealthCheckResult struct {
	Component string
	HealthStatus
}

