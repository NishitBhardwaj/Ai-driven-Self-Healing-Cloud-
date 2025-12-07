# Scaling Agent

## Purpose

The Scaling Agent is responsible for:
- Predicting traffic load based on historical patterns
- Automatically scaling pods or cloud instances up/down
- Optimizing resource utilization
- Maintaining performance while minimizing costs

## Responsibilities

1. **Load Prediction**: Uses historical data to predict future load
2. **Scaling Decisions**: Determines when and how much to scale
3. **Auto-Scaling**: Executes scaling operations (scale up/down)
4. **Cost Optimization**: Balances performance with resource costs

## Endpoints

- `GET /health` - Health check endpoint
- `POST /action` - Execute a scaling action
- `GET /status` - Get agent status

## Scaling Logic

- **Scale Up**: Triggered when metrics exceed threshold
- **Scale Down**: Triggered when metrics are below threshold
- **Cooldown**: Prevents rapid scaling oscillations

## Configuration

See `config.json` for scaling thresholds, replica limits, and evaluation intervals.

## Events

- Publishes: `scale.up`, `scale.down`, `scale.completed`
- Subscribes: `scale.required`, `threshold.exceeded`

