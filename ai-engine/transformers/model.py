"""
Transformer Encoder-Decoder Model for Time Series Forecasting
Forecasts workload spikes, anomaly trends, resource saturation
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class PositionalEncoding(nn.Module):
    """Positional encoding for transformer"""
    
    def __init__(self, d_model: int, max_len: int = 5000, dropout: float = 0.1):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer('pe', pe)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.pe[:x.size(0), :]
        return self.dropout(x)


class TransformerEncoder(nn.Module):
    """Transformer encoder for time series"""
    
    def __init__(
        self,
        input_dim: int,
        d_model: int = 128,
        nhead: int = 8,
        num_layers: int = 4,
        dim_feedforward: int = 512,
        dropout: float = 0.1,
        max_len: int = 1000
    ):
        super(TransformerEncoder, self).__init__()
        
        self.d_model = d_model
        self.input_projection = nn.Linear(input_dim, d_model)
        self.pos_encoder = PositionalEncoding(d_model, max_len, dropout)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            activation='relu',
            batch_first=False
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        logger.info(f"TransformerEncoder initialized: d_model={d_model}, nhead={nhead}, layers={num_layers}")
    
    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Forward pass
        
        Args:
            x: Input tensor [seq_len, batch_size, input_dim]
            mask: Attention mask
        
        Returns:
            Encoded tensor [seq_len, batch_size, d_model]
        """
        # Project input
        x = self.input_projection(x) * math.sqrt(self.d_model)
        
        # Add positional encoding
        x = self.pos_encoder(x)
        
        # Transformer encoding
        output = self.transformer_encoder(x, src_key_padding_mask=mask)
        
        return output


class TransformerDecoder(nn.Module):
    """Transformer decoder for time series forecasting"""
    
    def __init__(
        self,
        d_model: int = 128,
        nhead: int = 8,
        num_layers: int = 4,
        dim_feedforward: int = 512,
        dropout: float = 0.1,
        max_len: int = 1000
    ):
        super(TransformerDecoder, self).__init__()
        
        self.d_model = d_model
        self.pos_encoder = PositionalEncoding(d_model, max_len, dropout)
        
        decoder_layer = nn.TransformerDecoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            activation='relu',
            batch_first=False
        )
        self.transformer_decoder = nn.TransformerDecoder(decoder_layer, num_layers=num_layers)
        
        logger.info(f"TransformerDecoder initialized: d_model={d_model}, nhead={nhead}, layers={num_layers}")
    
    def forward(
        self,
        tgt: torch.Tensor,
        memory: torch.Tensor,
        tgt_mask: Optional[torch.Tensor] = None,
        memory_mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Forward pass
        
        Args:
            tgt: Target sequence [tgt_len, batch_size, d_model]
            memory: Encoder output [src_len, batch_size, d_model]
            tgt_mask: Target mask
            memory_mask: Memory mask
        
        Returns:
            Decoded tensor [tgt_len, batch_size, d_model]
        """
        # Add positional encoding
        tgt = self.pos_encoder(tgt)
        
        # Transformer decoding
        output = self.transformer_decoder(
            tgt, memory,
            tgt_mask=tgt_mask,
            memory_mask=memory_mask
        )
        
        return output


class TimeSeriesForecaster(nn.Module):
    """
    Transformer Encoder-Decoder for Time Series Forecasting
    
    Forecasts:
    - CPU usage 5 min ahead
    - Latency 5 min ahead
    - Memory risk
    - Error burst window
    """
    
    def __init__(
        self,
        input_dim: int = 5,  # [cpu, memory, latency, error_rate, request_rate]
        output_dim: int = 4,  # [cpu_forecast, latency_forecast, memory_risk, error_burst]
        d_model: int = 128,
        nhead: int = 8,
        num_encoder_layers: int = 4,
        num_decoder_layers: int = 4,
        dim_feedforward: int = 512,
        dropout: float = 0.1,
        seq_len: int = 60,  # 60 timesteps (e.g., 1 hour at 1-min intervals)
        pred_len: int = 5   # 5 minutes ahead
    ):
        super(TimeSeriesForecaster, self).__init__()
        
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.d_model = d_model
        self.seq_len = seq_len
        self.pred_len = pred_len
        
        # Encoder
        self.encoder = TransformerEncoder(
            input_dim=input_dim,
            d_model=d_model,
            nhead=nhead,
            num_layers=num_encoder_layers,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            max_len=seq_len
        )
        
        # Decoder
        self.decoder = TransformerDecoder(
            d_model=d_model,
            nhead=nhead,
            num_layers=num_decoder_layers,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            max_len=pred_len
        )
        
        # Output projection
        self.output_projection = nn.Sequential(
            nn.Linear(d_model, dim_feedforward),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(dim_feedforward, output_dim)
        )
        
        logger.info(f"TimeSeriesForecaster initialized: pred_len={pred_len} minutes")
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass
        
        Args:
            x: Input sequence [seq_len, batch_size, input_dim]
        
        Returns:
            Forecasted sequence [pred_len, batch_size, output_dim]
        """
        # Encode input
        memory = self.encoder(x)  # [seq_len, batch_size, d_model]
        
        # Create decoder input (zeros for future timesteps)
        batch_size = x.size(1)
        decoder_input = torch.zeros(self.pred_len, batch_size, self.d_model, device=x.device)
        
        # Decode
        decoded = self.decoder(decoder_input, memory)  # [pred_len, batch_size, d_model]
        
        # Project to output dimension
        output = self.output_projection(decoded)  # [pred_len, batch_size, output_dim]
        
        return output
    
    def forecast(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forecast future values
        
        Args:
            x: Input sequence [seq_len, batch_size, input_dim]
        
        Returns:
            Forecasted values [pred_len, batch_size, output_dim]
        """
        with torch.no_grad():
            forecast = self.forward(x)
        return forecast


class AnomalyTrendDetector(nn.Module):
    """
    Detects anomaly trends in time series
    
    Predicts:
    - Anomaly probability
    - Trend direction (increasing/decreasing)
    - Severity score
    """
    
    def __init__(
        self,
        input_dim: int = 5,
        d_model: int = 128,
        nhead: int = 8,
        num_layers: int = 4,
        dim_feedforward: int = 512,
        dropout: float = 0.1,
        seq_len: int = 60
    ):
        super(AnomalyTrendDetector, self).__init__()
        
        self.encoder = TransformerEncoder(
            input_dim=input_dim,
            d_model=d_model,
            nhead=nhead,
            num_layers=num_layers,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            max_len=seq_len
        )
        
        # Anomaly trend classifier
        self.trend_classifier = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_model // 2, 3)  # [normal, increasing_anomaly, decreasing_anomaly]
        )
        
        # Severity predictor
        self.severity_predictor = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_model // 2, 1),
            nn.Sigmoid()  # Severity [0, 1]
        )
        
        logger.info("AnomalyTrendDetector initialized")
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass
        
        Args:
            x: Input sequence [seq_len, batch_size, input_dim]
        
        Returns:
            Tuple of (trend_logits, severity_scores)
        """
        # Encode
        encoded = self.encoder(x)
        
        # Use last timestep
        last_hidden = encoded[-1]  # [batch_size, d_model]
        
        # Classify trend
        trend_logits = self.trend_classifier(last_hidden)
        
        # Predict severity
        severity = self.severity_predictor(last_hidden)
        
        return trend_logits, severity.squeeze()


class ResourceSaturationPredictor(nn.Module):
    """
    Predicts resource saturation (CPU, Memory)
    
    Forecasts when resources will be saturated
    """
    
    def __init__(
        self,
        input_dim: int = 5,
        d_model: int = 128,
        nhead: int = 8,
        num_layers: int = 4,
        dim_feedforward: int = 512,
        dropout: float = 0.1,
        seq_len: int = 60,
        pred_len: int = 5
    ):
        super(ResourceSaturationPredictor, self).__init__()
        
        self.encoder = TransformerEncoder(
            input_dim=input_dim,
            d_model=d_model,
            nhead=nhead,
            num_layers=num_layers,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            max_len=seq_len
        )
        
        # Saturation predictor (time until saturation)
        self.saturation_predictor = nn.Sequential(
            nn.Linear(d_model, dim_feedforward),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(dim_feedforward, pred_len * 2)  # [cpu_saturation, memory_saturation] for each timestep
        )
        
        logger.info("ResourceSaturationPredictor initialized")
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Predict resource saturation
        
        Args:
            x: Input sequence [seq_len, batch_size, input_dim]
        
        Returns:
            Saturation predictions [batch_size, pred_len, 2] (CPU, Memory)
        """
        # Encode
        encoded = self.encoder(x)
        
        # Use last timestep
        last_hidden = encoded[-1]  # [batch_size, d_model]
        
        # Predict saturation
        saturation = self.saturation_predictor(last_hidden)  # [batch_size, pred_len * 2]
        saturation = saturation.view(-1, self.saturation_predictor[-1].out_features // 2, 2)
        
        return saturation
