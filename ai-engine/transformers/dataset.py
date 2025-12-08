"""
Dataset for Transformer Models
Prepare sliding-window sequences from metrics
"""

import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
from typing import List, Tuple, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class SlidingWindowDataset(Dataset):
    """
    Dataset with sliding-window sequences from metrics
    
    Prepares sequences for:
    - Workload forecasting
    - Anomaly detection
    - Resource saturation prediction
    """
    
    def __init__(
        self,
        data: np.ndarray,
        seq_len: int = 60,  # Input sequence length (e.g., 60 minutes)
        pred_len: int = 5,  # Prediction length (5 minutes ahead)
        stride: int = 1,
        normalize: bool = True,
        feature_names: Optional[List[str]] = None
    ):
        """
        Initialize sliding window dataset
        
        Args:
            data: Time series data [time_steps, features]
            seq_len: Input sequence length
            pred_len: Prediction length
            stride: Stride for sliding window
            normalize: Whether to normalize data
            feature_names: Names of features (for reference)
        """
        self.data = data
        self.seq_len = seq_len
        self.pred_len = pred_len
        self.stride = stride
        self.normalize = normalize
        self.feature_names = feature_names or ['cpu', 'memory', 'latency', 'error_rate', 'request_rate']
        
        # Normalize data
        if normalize:
            self.mean = np.mean(data, axis=0, keepdims=True)
            self.std = np.std(data, axis=0, keepdims=True) + 1e-8
            self.data = (data - self.mean) / self.std
        else:
            self.mean = np.zeros((1, data.shape[1]))
            self.std = np.ones((1, data.shape[1]))
        
        # Create samples
        self.samples = self._create_samples()
        
        logger.info(f"SlidingWindowDataset created: {len(self.samples)} samples, seq_len={seq_len}, pred_len={pred_len}")
    
    def _create_samples(self) -> List[Tuple[int, int, int]]:
        """Create sample indices (start, input_end, target_end)"""
        samples = []
        total_len = len(self.data)
        
        for i in range(0, total_len - self.seq_len - self.pred_len + 1, self.stride):
            input_end = i + self.seq_len
            target_end = input_end + self.pred_len
            samples.append((i, input_end, target_end))
        
        return samples
    
    def __len__(self) -> int:
        return len(self.samples)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """
        Get a sample
        
        Returns:
            Dictionary with input and target tensors
        """
        start_idx, input_end, target_end = self.samples[idx]
        
        # Input sequence
        input_seq = self.data[start_idx:input_end]
        input_tensor = torch.FloatTensor(input_seq)  # [seq_len, features]
        
        # Target sequence (future values)
        target_seq = self.data[input_end:target_end]
        target_tensor = torch.FloatTensor(target_seq)  # [pred_len, features]
        
        return {
            'input': input_tensor,
            'target': target_tensor
        }
    
    def denormalize(self, data: np.ndarray) -> np.ndarray:
        """Denormalize data"""
        if self.normalize:
            return data * self.std + self.mean
        return data


class MetricsDataset(Dataset):
    """
    Dataset specifically for cloud metrics
    
    Features: [cpu, memory, latency, error_rate, request_rate]
    Targets: [cpu_forecast, latency_forecast, memory_risk, error_burst]
    """
    
    def __init__(
        self,
        metrics: Dict[str, np.ndarray],
        seq_len: int = 60,
        pred_len: int = 5,
        stride: int = 1,
        normalize: bool = True
    ):
        """
        Initialize metrics dataset
        
        Args:
            metrics: Dictionary of metric_name -> time_series
            seq_len: Input sequence length
            pred_len: Prediction length
            stride: Stride for sliding window
            normalize: Whether to normalize
        """
        # Combine metrics into array
        feature_names = ['cpu', 'memory', 'latency', 'error_rate', 'request_rate']
        data_list = []
        
        for name in feature_names:
            if name in metrics:
                data_list.append(metrics[name])
            else:
                # Fill with zeros if missing
                max_len = max(len(v) for v in metrics.values()) if metrics else 0
                data_list.append(np.zeros(max_len))
        
        self.data = np.column_stack(data_list)  # [time_steps, features]
        self.feature_names = feature_names
        self.seq_len = seq_len
        self.pred_len = pred_len
        self.stride = stride
        self.normalize = normalize
        
        # Normalize
        if normalize:
            self.mean = np.mean(self.data, axis=0, keepdims=True)
            self.std = np.std(self.data, axis=0, keepdims=True) + 1e-8
            self.data = (self.data - self.mean) / self.std
        else:
            self.mean = np.zeros((1, self.data.shape[1]))
            self.std = np.ones((1, self.data.shape[1]))
        
        # Create samples
        self.samples = []
        total_len = len(self.data)
        for i in range(0, total_len - seq_len - pred_len + 1, stride):
            self.samples.append((i, i + seq_len, i + seq_len + pred_len))
        
        logger.info(f"MetricsDataset created: {len(self.samples)} samples")
    
    def __len__(self) -> int:
        return len(self.samples)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """Get a sample"""
        start_idx, input_end, target_end = self.samples[idx]
        
        # Input: [cpu, memory, latency, error_rate, request_rate]
        input_seq = self.data[start_idx:input_end]
        input_tensor = torch.FloatTensor(input_seq)  # [seq_len, 5]
        
        # Target: Extract specific metrics for forecasting
        target_seq = self.data[input_end:target_end]
        
        # Create target: [cpu_forecast, latency_forecast, memory_risk, error_burst]
        # cpu_forecast: CPU values
        # latency_forecast: Latency values
        # memory_risk: Memory saturation risk (1 if memory > threshold, else 0)
        # error_burst: Error burst indicator (1 if error_rate > threshold, else 0)
        
        cpu_forecast = target_seq[:, 0]  # CPU
        latency_forecast = target_seq[:, 2]  # Latency
        memory_risk = (target_seq[:, 1] > 0.8).astype(float)  # Memory risk (threshold 0.8)
        error_burst = (target_seq[:, 3] > 0.1).astype(float)  # Error burst (threshold 0.1)
        
        # Stack targets
        target = np.column_stack([cpu_forecast, latency_forecast, memory_risk, error_burst])
        target_tensor = torch.FloatTensor(target)  # [pred_len, 4]
        
        return {
            'input': input_tensor,
            'target': target_tensor
        }
    
    def denormalize(self, data: np.ndarray) -> np.ndarray:
        """Denormalize data"""
        if self.normalize:
            return data * self.std + self.mean
        return data


def create_dataloader(
    dataset: Dataset,
    batch_size: int = 32,
    shuffle: bool = True,
    num_workers: int = 0
) -> DataLoader:
    """
    Create DataLoader for dataset
    
    Args:
        dataset: Dataset instance
        batch_size: Batch size
        shuffle: Whether to shuffle
        num_workers: Number of worker processes
    
    Returns:
        DataLoader
    """
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=True
    )
