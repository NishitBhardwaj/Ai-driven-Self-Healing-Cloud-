#!/bin/bash

# Delete Service Script
# This script deletes a Kubernetes service to simulate service unavailability
# Used for chaos engineering and testing the Self-Healing Agent's response to service failures

set -e

NAMESPACE="${NAMESPACE:-self-healing-cloud}"
SERVICE="${SERVICE:-}"
BACKUP="${BACKUP:-true}"  # Whether to backup service before deletion
RESTORE_AFTER="${RESTORE_AFTER:-0}"  # Seconds to wait before restoring (0 = don't restore)

echo "=========================================="
echo "Delete Service - Chaos Engineering"
echo "=========================================="
echo "Namespace: $NAMESPACE"
echo "Service: ${SERVICE:-<required>}"
echo "Backup: $BACKUP"
echo "Restore After: ${RESTORE_AFTER} seconds (0 = manual restore)"
echo ""

# Validate service name
if [ -z "$SERVICE" ]; then
    echo "ERROR: Service name is required"
    echo ""
    echo "Usage:"
    echo "  SERVICE=compute-service ./delete_service.sh"
    echo "  or"
    echo "  ./delete_service.sh compute-service"
    echo ""
    echo "Available services in namespace $NAMESPACE:"
    kubectl get services -n "$NAMESPACE" -o custom-columns=NAME:.metadata.name || echo "No services found"
    exit 1
fi

# Check if service exists
if ! kubectl get service "$SERVICE" -n "$NAMESPACE" &>/dev/null; then
    echo "ERROR: Service '$SERVICE' not found in namespace '$NAMESPACE'"
    echo ""
    echo "Available services:"
    kubectl get services -n "$NAMESPACE" -o custom-columns=NAME:.metadata.name
    exit 1
fi

# Backup service if requested
BACKUP_FILE=""
if [ "$BACKUP" = "true" ]; then
    BACKUP_FILE="/tmp/${SERVICE}-backup-$(date +%s).yaml"
    echo "Backing up service to: $BACKUP_FILE"
    kubectl get service "$SERVICE" -n "$NAMESPACE" -o yaml > "$BACKUP_FILE"
    echo "✅ Service backed up"
    echo ""
fi

# Show service details
echo "Service details before deletion:"
kubectl get service "$SERVICE" -n "$NAMESPACE" -o wide
echo ""

# Confirm deletion
read -p "Are you sure you want to delete service '$SERVICE'? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    if [ -n "$BACKUP_FILE" ]; then
        rm -f "$BACKUP_FILE"
    fi
    exit 0
fi

# Delete the service
echo ""
echo "Deleting service: $SERVICE"
kubectl delete service "$SERVICE" -n "$NAMESPACE" || {
    echo "ERROR: Failed to delete service"
    exit 1
}

echo ""
echo "✅ Service '$SERVICE' has been deleted"
echo ""

# Show impact
echo "Checking for pods that were using this service..."
PODS=$(kubectl get pods -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || echo "")
if [ -n "$PODS" ]; then
    echo "Pods in namespace (may be affected by service deletion):"
    kubectl get pods -n "$NAMESPACE" -o wide
fi

# Restore after specified duration
if [ "$RESTORE_AFTER" -gt 0 ] && [ -n "$BACKUP_FILE" ] && [ -f "$BACKUP_FILE" ]; then
    echo ""
    echo "Waiting $RESTORE_AFTER seconds before restoring service..."
    sleep "$RESTORE_AFTER"
    
    echo ""
    echo "Restoring service from backup..."
    kubectl apply -f "$BACKUP_FILE" || {
        echo "ERROR: Failed to restore service"
        echo "Manual restore command: kubectl apply -f $BACKUP_FILE"
        exit 1
    }
    
    echo "✅ Service restored"
    rm -f "$BACKUP_FILE"
else
    echo ""
    if [ -n "$BACKUP_FILE" ] && [ -f "$BACKUP_FILE" ]; then
        echo "To restore the service manually:"
        echo "  kubectl apply -f $BACKUP_FILE"
    else
        echo "⚠️  No backup available. Service must be recreated manually."
    fi
fi

echo ""
echo "=========================================="
echo "Service deletion script completed"
echo "=========================================="
echo ""
echo "Impact:"
echo "  - Service endpoints are no longer available"
echo "  - DNS resolution for service will fail"
echo "  - Pods trying to connect will experience connection failures"
echo ""
echo "This simulates:"
echo "  - Service misconfiguration"
echo "  - Accidental service deletion"
echo "  - Network partition affecting service discovery"

