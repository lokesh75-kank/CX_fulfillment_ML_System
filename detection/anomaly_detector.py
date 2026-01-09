"""
Anomaly Detection Engine

Implements multiple anomaly detection algorithms:
- Z-score based detection
- EWMA (Exponentially Weighted Moving Average)
- Simple Bayesian change point detection
"""

from typing import List, Dict, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats


class AnomalyDetector:
    """Detects anomalies in time series metrics"""
    
    def __init__(self, z_score_threshold: float = 2.5, 
                 ewma_alpha: float = 0.3,
                 ewma_threshold: float = 2.0):
        """
        Initialize anomaly detector
        
        Args:
            z_score_threshold: Threshold for Z-score detection (default: 2.5)
            ewma_alpha: Smoothing factor for EWMA (0-1, default: 0.3)
            ewma_threshold: Threshold for EWMA deviation (default: 2.0)
        """
        self.z_score_threshold = z_score_threshold
        self.ewma_alpha = ewma_alpha
        self.ewma_threshold = ewma_threshold
    
    def detect_z_score(self, values: List[float], 
                      window_size: int = 30) -> List[bool]:
        """
        Detect anomalies using Z-score method
        
        Args:
            values: List of metric values
            window_size: Size of rolling window for mean/std calculation
        
        Returns:
            List of boolean flags (True = anomaly)
        """
        if len(values) < window_size:
            return [False] * len(values)
        
        anomalies = []
        values_array = np.array(values)
        
        for i in range(len(values)):
            if i < window_size:
                # Not enough history, use all available data
                window = values_array[:i+1]
            else:
                # Use rolling window
                window = values_array[i-window_size+1:i+1]
            
            if len(window) < 2:
                anomalies.append(False)
                continue
            
            mean = np.mean(window)
            std = np.std(window)
            
            if std == 0:
                anomalies.append(False)
                continue
            
            z_score = abs((values[i] - mean) / std)
            anomalies.append(z_score > self.z_score_threshold)
        
        return anomalies
    
    def detect_ewma(self, values: List[float]) -> Tuple[List[float], List[bool]]:
        """
        Detect anomalies using EWMA (Exponentially Weighted Moving Average)
        
        Args:
            values: List of metric values
        
        Returns:
            Tuple of (ewma_values, anomaly_flags)
        """
        if len(values) == 0:
            return [], []
        
        ewma_values = []
        anomalies = []
        values_array = np.array(values)
        
        # Initialize with first value
        ewma = values[0]
        ewma_values.append(ewma)
        anomalies.append(False)  # First value can't be anomaly
        
        for i in range(1, len(values)):
            # Update EWMA
            ewma = self.ewma_alpha * values[i] + (1 - self.ewma_alpha) * ewma
            ewma_values.append(ewma)
            
            # Calculate deviation
            if i < 10:  # Need some history for std
                anomalies.append(False)
                continue
            
            # Calculate rolling std of residuals
            residuals = values_array[:i+1] - np.array(ewma_values)
            std_residual = np.std(residuals[-10:])  # Last 10 residuals
            
            if std_residual == 0:
                anomalies.append(False)
                continue
            
            # Check if current deviation is significant
            deviation = abs(values[i] - ewma) / std_residual
            anomalies.append(deviation > self.ewma_threshold)
        
        return ewma_values, anomalies
    
    def detect_bayesian_change_point(self, values: List[float],
                                    min_segment_size: int = 5) -> List[int]:
        """
        Simple Bayesian change point detection
        
        Detects points where the distribution of values changes significantly.
        
        Args:
            values: List of metric values
            min_segment_size: Minimum size of segments
        
        Returns:
            List of indices where change points occur
        """
        if len(values) < 2 * min_segment_size:
            return []
        
        change_points = []
        values_array = np.array(values)
        
        for i in range(min_segment_size, len(values) - min_segment_size):
            # Split into two segments
            segment1 = values_array[:i]
            segment2 = values_array[i:]
            
            if len(segment1) < min_segment_size or len(segment2) < min_segment_size:
                continue
            
            # Calculate means and stds
            mean1, std1 = np.mean(segment1), np.std(segment1)
            mean2, std2 = np.mean(segment2), np.std(segment2)
            
            if std1 == 0 or std2 == 0:
                continue
            
            # Simple likelihood ratio test
            # Compare if means are significantly different
            pooled_std = np.sqrt((std1**2 + std2**2) / 2)
            if pooled_std == 0:
                continue
            
            t_stat = abs(mean1 - mean2) / pooled_std
            
            # Threshold for change point (simplified)
            if t_stat > 2.0:  # Significant difference
                change_points.append(i)
        
        return change_points
    
    def detect_anomalies(self, time_series: pd.DataFrame,
                       metric_column: str,
                       time_column: str = 'timestamp',
                       method: str = 'z_score') -> pd.DataFrame:
        """
        Detect anomalies in a time series DataFrame
        
        Args:
            time_series: DataFrame with time series data
            metric_column: Name of column with metric values
            time_column: Name of column with timestamps
            method: Detection method ('z_score', 'ewma', 'bayesian', or 'combined')
        
        Returns:
            DataFrame with anomaly flags added
        """
        result = time_series.copy()
        
        # Sort by time
        result = result.sort_values(time_column)
        values = result[metric_column].tolist()
        
        if method == 'z_score':
            anomalies = self.detect_z_score(values)
            result['anomaly'] = anomalies
            result['anomaly_method'] = 'z_score'
        
        elif method == 'ewma':
            ewma_values, anomalies = self.detect_ewma(values)
            result['anomaly'] = anomalies
            result['ewma_value'] = ewma_values
            result['anomaly_method'] = 'ewma'
        
        elif method == 'bayesian':
            change_points = self.detect_bayesian_change_point(values)
            anomalies = [False] * len(values)
            for cp in change_points:
                anomalies[cp] = True
            result['anomaly'] = anomalies
            result['anomaly_method'] = 'bayesian'
        
        elif method == 'combined':
            # Use multiple methods and flag if any detects anomaly
            z_anomalies = self.detect_z_score(values)
            _, ewma_anomalies = self.detect_ewma(values)
            bayesian_cps = self.detect_bayesian_change_point(values)
            bayesian_anomalies = [False] * len(values)
            for cp in bayesian_cps:
                bayesian_anomalies[cp] = True
            
            # Anomaly if at least 2 methods agree
            combined = [
                sum([z, e, b]) >= 2 
                for z, e, b in zip(z_anomalies, ewma_anomalies, bayesian_anomalies)
            ]
            result['anomaly'] = combined
            result['anomaly_method'] = 'combined'
        
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return result
    
    def detect_metric_anomalies(self, metrics_df: pd.DataFrame,
                               metric_name: str,
                               time_column: str = 'timestamp') -> List[Dict]:
        """
        Detect anomalies for a specific metric and return incident candidates
        
        Args:
            metrics_df: DataFrame with metrics over time
            metric_name: Name of metric column to check
            time_column: Name of timestamp column
        
        Returns:
            List of anomaly events with details
        """
        anomalies_df = self.detect_anomalies(
            metrics_df,
            metric_column=metric_name,
            time_column=time_column,
            method='combined'
        )
        
        # Extract anomaly events
        anomaly_events = []
        anomaly_rows = anomalies_df[anomalies_df['anomaly'] == True]
        
        for _, row in anomaly_rows.iterrows():
            anomaly_events.append({
                'timestamp': row[time_column],
                'metric': metric_name,
                'value': row[metric_name],
                'method': row.get('anomaly_method', 'combined'),
                'severity': self._calculate_severity(row[metric_name], metrics_df[metric_name])
            })
        
        return anomaly_events
    
    def _calculate_severity(self, value: float, all_values: pd.Series) -> str:
        """Calculate severity of anomaly"""
        percentile = stats.percentileofscore(all_values, value)
        
        if percentile < 5:
            return 'HIGH'
        elif percentile < 10:
            return 'MEDIUM'
        else:
            return 'LOW'

