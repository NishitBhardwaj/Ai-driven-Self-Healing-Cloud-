#!/bin/bash

# Setup script for ELK Stack
# This script sets up the ELK Stack for centralized logging

set -e

echo "=========================================="
echo "ELK Stack Setup"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "Starting ELK Stack..."
cd "$(dirname "$0")"

# Start ELK Stack
docker-compose -f elk-docker-compose.yml up -d

echo ""
echo "Waiting for services to be ready..."
sleep 10

# Check Elasticsearch
echo "Checking Elasticsearch..."
for i in {1..30}; do
    if curl -s http://localhost:9200/_cluster/health > /dev/null 2>&1; then
        echo "✓ Elasticsearch is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "✗ Elasticsearch failed to start"
        exit 1
    fi
    sleep 2
done

# Check Logstash
echo "Checking Logstash..."
if docker ps | grep -q logstash; then
    echo "✓ Logstash is running"
else
    echo "✗ Logstash failed to start"
    exit 1
fi

# Check Kibana
echo "Checking Kibana..."
for i in {1..30}; do
    if curl -s http://localhost:5601/api/status > /dev/null 2>&1; then
        echo "✓ Kibana is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "✗ Kibana failed to start"
        exit 1
    fi
    sleep 2
done

echo ""
echo "=========================================="
echo "ELK Stack is ready!"
echo "=========================================="
echo ""
echo "Elasticsearch: http://localhost:9200"
echo "Kibana: http://localhost:5601"
echo "Logstash: TCP localhost:5000, UDP localhost:5001"
echo ""
echo "Next steps:"
echo "1. Open Kibana at http://localhost:5601"
echo "2. Create index pattern: agent-logs-*"
echo "3. Import dashboards from config/logging/kibana-dashboards/"
echo "4. Configure agents to send logs to Logstash"
echo ""

