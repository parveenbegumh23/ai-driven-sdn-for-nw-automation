"""
Signal Analyzer

Analyze network signals for anomalies and patterns.
"""

import logging
from typing import Dict, List, Optional
from statistics import mean, stdev

logger = logging.getLogger(__name__)


class SignalAnalyzer:
    """
    Analyze network signals and detect anomalies.
    
    Attributes:
        threshold (float): Anomaly threshold in standard deviations
        baseline (Optional[float]): Baseline value for comparison
    """
    
    def __init__(self, threshold: float = 2.0):
        """
        Initialize the signal analyzer.
        
        Args:
            threshold: Number of standard deviations for anomaly detection
        """
        self.threshold = threshold
        self.baseline = None
        logger.info(f"Initialized SignalAnalyzer with threshold: {threshold}")
    
    def analyze(self, metrics: List[float]) -> Dict:
        """
        Analyze metrics for anomalies and statistics.
        
        Args:
            metrics: List of metric values
            
        Returns:
            Dictionary containing analysis results
        """
        if len(metrics) < 2:
            return {
                'status': 'insufficient_data',
                'count': len(metrics)
            }
        
        analysis = {
            'count': len(metrics),
            'min': min(metrics),
            'max': max(metrics),
            'mean': mean(metrics),
            'anomalies': [],
            'status': 'normal'
        }
        
        if len(metrics) >= 3:
            std = stdev(metrics)
            analysis['std_dev'] = std
            
            # Detect anomalies
            upper_bound = analysis['mean'] + (self.threshold * std)
            lower_bound = analysis['mean'] - (self.threshold * std)
            
            for idx, value in enumerate(metrics):
                if value > upper_bound or value < lower_bound:
                    analysis['anomalies'].append({
                        'index': idx,
                        'value': value,
                        'type': 'high' if value > upper_bound else 'low'
                    })
            
            if analysis['anomalies']:
                analysis['status'] = 'anomaly_detected'
        
        return analysis
    
    def set_baseline(self, value: float) -> None:
        """
        Set baseline value for comparison.
        
        Args:
            value: Baseline value
        """
        self.baseline = value
        logger.info(f"Baseline set to: {value}")
    
    def compare_to_baseline(self, current_value: float) -> Dict:
        """
        Compare current value to baseline.
        
        Args:
            current_value: Current metric value
            
        Returns:
            Comparison results
        """
        if self.baseline is None:
            return {
                'status': 'no_baseline',
                'current_value': current_value
            }
        
        deviation = ((current_value - self.baseline) / self.baseline) * 100
        
        return {
            'baseline': self.baseline,
            'current_value': current_value,
            'deviation_percent': deviation,
            'status': 'within_threshold' if abs(deviation) < 10 else 'deviation_detected'
        }
    
    def detect_trend(self, metrics: List[float], window: int = 5) -> str:
        """
        Detect trend in metrics.
        
        Args:
            metrics: List of metric values
            window: Window size for trend calculation
            
        Returns:
            Trend direction: 'increasing', 'decreasing', or 'stable'
        """
        if len(metrics) < window:
            return 'insufficient_data'
        
        recent = metrics[-window:]
        older = metrics[-window*2:-window]
        
        recent_mean = mean(recent) if recent else 0
        older_mean = mean(older) if older else 0
        
        if older_mean == 0:
            return 'stable'
        
        change = ((recent_mean - older_mean) / older_mean) * 100
        
        if change > 5:
            return 'increasing'
        elif change < -5:
            return 'decreasing'
        else:
            return 'stable'
    
    def get_quality_score(self, metrics: Dict) -> float:
        """
        Calculate network quality score (0-100).
        
        Args:
            metrics: Metrics dictionary with signal quality parameters
            
        Returns:
            Quality score from 0 to 100
        """
        score = 100.0
        
        # Penalty for high latency
        if 'latency' in metrics:
            latency = metrics['latency']
            if latency > 100:
                score -= min((latency - 100) / 10, 30)
        
        # Penalty for packet loss
        if 'packet_loss' in metrics:
            loss = metrics['packet_loss']
            score -= min(loss * 5, 25)
        
        # Bonus for strong signal
        if 'signal_strength' in metrics:
            strength = metrics['signal_strength']
            if strength < 50:
                score -= (50 - strength) / 2
        
        return max(0, min(100, score))
