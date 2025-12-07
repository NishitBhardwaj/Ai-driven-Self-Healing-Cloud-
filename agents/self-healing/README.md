# Self-Healing Agent

## Purpose

The Self-Healing Agent is responsible for:
- Detecting service failures automatically
- Initiating recovery actions without human intervention
- Providing explanations for healing decisions
- Coordinating with other agents during recovery

## Responsibilities

1. **Failure Detection**: Monitors services for failures and errors
2. **Recovery Strategy Selection**: Chooses appropriate healing action
3. **Automatic Recovery**: Executes healing actions (restart, rollback, replace)
4. **Explainability**: Provides reasoning for healing decisions

## Endpoints

- `GET /health` - Health check endpoint
- `POST /heal` - Manually trigger healing for a service
- `POST /action` - Execute a healing action
- `GET /status` - Get agent status

## Healing Strategies

- **Restart**: Restarts a failed service
- **Rollback**: Rolls back to previous working version
- **Replace**: Replaces failed pod/instance

## Configuration

See `config.json` for healing strategy configuration and thresholds.

## Events

- Publishes: `healing.started`, `healing.completed`, `healing.failed`
- Subscribes: `healing.required`, `error.detected`

