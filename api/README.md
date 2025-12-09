# API - REST Endpoints for Agent Status and Logs

## Overview

This package provides REST API endpoints for querying agent statuses, logs, and decision history. These endpoints are used by the dashboard to display real-time information about agents and their actions.

## Endpoints

### 1. Agent Status API

**Endpoint**: `GET /api/agents/status`

**Description**: Returns the status of all agents including their last action, confidence level, and explanation.

**Response**:
```json
{
  "agents": [
    {
      "id": "self-healing-001",
      "name": "Self-Healing Agent",
      "status": "running",
      "last_action": {
        "type": "restart_pod",
        "description": "Restarted pod 'web-app-123'",
        "timestamp": "2024-01-01T12:00:00Z",
        "success": true
      },
      "confidence": 0.95,
      "explanation": "Pod was restarted due to crash loop detection...",
      "mode": "auto",
      "last_update": "2024-01-01T12:00:00Z"
    }
  ]
}
```

**Fields**:
- `id`: Agent identifier
- `name`: Human-readable agent name
- `status`: "running", "stopped", or "error"
- `last_action`: Last action taken (optional)
- `confidence`: Confidence level (0.0 to 1.0)
- `explanation`: Explanation of last decision
- `mode`: "auto" or "manual"
- `last_update`: Last update timestamp

### 2. Logs API

**Endpoint**: `GET /api/agents/logs`

**Description**: Returns logs of agent actions with reasoning and explanations.

**Query Parameters**:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 100, max: 1000)
- `agent_id`: Filter by agent ID
- `type`: Filter by log type (info, success, warning, error)
- `start_date`: Filter by start date (RFC3339)
- `end_date`: Filter by end date (RFC3339)

**Response**:
```json
{
  "logs": [
    {
      "id": "log-1",
      "timestamp": "2024-01-01T12:00:00Z",
      "agent_id": "self-healing-001",
      "agent_name": "Self-Healing Agent",
      "action": "restart_pod",
      "action_taken": "Restarted pod 'web-app-123'",
      "reasoning": "Pod was in crash loop. Restarting should resolve the issue.",
      "explanation": "Pod was restarted due to crash loop detection...",
      "confidence": 0.95,
      "mode": "auto",
      "type": "success",
      "status": "completed"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 100,
  "has_more": false
}
```

**Fields**:
- `id`: Log entry identifier
- `timestamp`: When the action occurred
- `agent_id`: Agent identifier
- `agent_name`: Agent name
- `action`: Action type
- `action_taken`: Description of action
- `reasoning`: Reasoning for the action
- `explanation`: Full explanation
- `confidence`: Confidence level
- `mode`: "auto" or "manual"
- `type`: "info", "success", "warning", or "error"
- `status`: Action status

### 3. Decision History API

**Endpoint**: `GET /api/agents/decision-history`

**Description**: Returns decision history including explanations, confidence scores, and reasoning chains.

**Query Parameters**:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 50, max: 1000)
- `agent_id`: Filter by agent ID
- `mode`: Filter by mode (auto, manual)
- `status`: Filter by status (pending, executed, rejected)
- `start_date`: Filter by start date (RFC3339)
- `end_date`: Filter by end date (RFC3339)

**Response**:
```json
{
  "decisions": [
    {
      "id": "decision-1",
      "agent_id": "self-healing-001",
      "agent_name": "Self-Healing Agent",
      "mode": "auto",
      "problem": "Pod 'web-app-123' is in crash loop",
      "reasoning": "Detected repeated pod crashes...",
      "action_taken": "restart_pod",
      "explanation": "Pod was restarted due to crash loop detection...",
      "confidence": 0.95,
      "selected_option": {
        "id": "restart_pod",
        "description": "Restart the failed pod",
        "reasoning": "Pod is in crash loop, restarting should resolve",
        "risk": "low",
        "impact": "medium",
        "estimated_cost": 0.0
      },
      "options": [...],
      "reasoning_chain": [
        {
          "step_number": 1,
          "description": "Problem Detection",
          "reasoning": "Detected pod crash loop"
        }
      ],
      "alternative_actions": ["rebuild_deployment", "rollback"],
      "execution_result": {
        "status": "success",
        "pod_name": "web-app-123"
      },
      "timestamp": "2024-01-01T12:00:00Z",
      "status": "executed"
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 50,
  "has_more": false
}
```

**Fields**:
- `id`: Decision identifier
- `agent_id`: Agent identifier
- `agent_name`: Agent name
- `mode`: "auto" or "manual"
- `problem`: Problem description
- `reasoning`: Reasoning for decision
- `action_taken`: Action that was taken
- `explanation`: Full explanation
- `confidence`: Confidence level (0.0 to 1.0)
- `selected_option`: Selected action option
- `options`: Available options (for manual mode)
- `reasoning_chain`: Step-by-step reasoning
- `alternative_actions`: Other actions considered
- `execution_result`: Result of execution
- `timestamp`: When decision was made
- `status`: "pending", "executed", or "rejected"

## Usage

### Integration with Server

```go
import (
    "github.com/ai-driven-self-healing-cloud/api"
    "github.com/ai-driven-self-healing-cloud/agents/core"
)

func main() {
    registry := core.GetRegistry()
    logger := logrus.New()
    
    router := api.SetupRoutes(registry, logger)
    
    http.ListenAndServe(":8080", router)
}
```

### Example Requests

**Get Agent Status**:
```bash
curl http://localhost:8080/api/agents/status
```

**Get Logs**:
```bash
curl "http://localhost:8080/api/agents/logs?page=1&page_size=50&agent_id=self-healing-001"
```

**Get Decision History**:
```bash
curl "http://localhost:8080/api/agents/decision-history?mode=auto&page=1&page_size=20"
```

## CORS

All endpoints include CORS headers to allow cross-origin requests from the dashboard.

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200 OK`: Success
- `400 Bad Request`: Invalid parameters
- `500 Internal Server Error`: Server error

## Next Steps

1. **Database Integration**: Store data in database instead of in-memory
2. **Authentication**: Add authentication/authorization
3. **Rate Limiting**: Implement rate limiting
4. **Caching**: Add caching for frequently accessed data
5. **WebSocket Integration**: Connect to WebSocket for real-time updates

