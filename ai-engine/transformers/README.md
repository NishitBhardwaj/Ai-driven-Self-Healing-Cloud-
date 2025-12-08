# Transformers Module

This module implements Transformer models for anomaly detection and workload forecasting in the cloud system.

## Overview

The Transformers module:
- Detects anomalies in time series metrics
- Forecasts future workload demands
- Provides scaling recommendations
- Uses attention mechanisms for long-range dependencies

## Components

### `model.py` - Transformer Models
- **TransformerEncoder**: Base transformer encoder
- **AnomalyDetector**: Detects anomalies in metrics
- **WorkloadForecaster**: Predicts future workload
- **MultiTaskTransformer**: Combined model for both tasks

### `dataset.py` - Data Handling
- **TimeSeriesDataset**: General time series dataset
- **AnomalyDataset**: Dataset for anomaly detection
- **ForecastingDataset**: Dataset for forecasting

### `forecasting.py` - High-Level Interface
- **WorkloadForecastEngine**: Engine for workload forecasting
- **AnomalyDetectionEngine**: Engine for anomaly detection
- **ForecastingPipeline**: Complete analysis pipeline

## Usage

### Workload Forecasting

```python
from ai_engine.transformers.forecasting import WorkloadForecastEngine
import numpy as np

# Create engine
engine = WorkloadForecastEngine(input_dim=5, output_dim=5)

# Historical data [time_steps, features]
historical = np.random.randn(200, 5)

# Forecast
forecast = engine.forecast(historical, forecast_horizon=24)
```

### Anomaly Detection

```python
from ai_engine.transformers.forecasting import AnomalyDetectionEngine

# Create engine
engine = AnomalyDetectionEngine(input_dim=5)

# Detect anomalies
is_anomaly, prob, details = engine.detect(time_series, threshold=0.5)
```

### Complete Analysis

```python
from ai_engine.transformers.forecasting import ForecastingPipeline

# Create pipeline
pipeline = ForecastingPipeline()

# Analyze
results = pipeline.analyze(historical_data, forecast_horizon=24)

# Get scaling recommendation
recommendation = pipeline.get_scaling_recommendation(
    historical_data,
    forecast_horizon=24
)
```

## Model Architecture

### Transformer Encoder
- Multi-head self-attention
- Positional encoding
- Feed-forward networks
- Layer normalization
- Residual connections

### Anomaly Detection
- Encoder-decoder architecture
- Classification head for anomaly detection
- Reconstruction head for reconstruction-based detection

### Forecasting
- Encoder-decoder architecture
- Decoder generates future timesteps
- Output projection to metric dimensions

## Training

Models can be trained on historical data:

```python
# Training code would use PyTorch training loop
# with TimeSeriesDataset or ForecastingDataset
```

## Dependencies

- PyTorch
- NumPy

## Related Modules

- RL module for learning optimal actions
- GNN module for dependency modeling
- LLM reasoning for high-level decisions
- Meta-Agent for orchestration

