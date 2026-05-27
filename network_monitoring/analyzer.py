"""Network signal analysis and anomaly detection."""

import logging
from typing import Dict, List, Optional
from statistics import mean, stdev, median

logger = logging.getLogger(__name__)


class SignalAnalyzer:
    """Analyzes network signals and detects anomalies."""
    
    def __init__(self, anomaly_threshold: float = 2.0):
        """Initialize the signal analyzer.
        
        Args:
            anomaly_threshold: Standard deviations for anomaly detection
        """
        self.anomaly_threshold = anomaly_threshold
    
    def analyze(self, metrics: Dict) -> Dict:
        """Analyze collected metrics for insights.
        
        Args:
            metrics: Dictionary of current metrics
        
        Returns:
            Analysis results including anomalies and insights
        """
        analysis = {
            'timestamp': metrics.get('timestamp'),
            'anomalies': [],
            'status': 'healthy',
            'severity': 'low'
        }
        
        # Check CPU
        if metrics.get('cpu_percent', 0) > 80:
            analysis['anomalies'].append({
                'metric': 'cpu_percent',
                'value': metrics['cpu_percent'],
                'issue': 'High CPU usage',
                'severity': 'warning'
            })
            analysis['severity'] = 'high'
        
        # Check Memory
        if metrics.get('memory_percent', 0) > 85:
            analysis['anomalies'].append({
                'metric': 'memory_percent',
                'value': metrics['memory_percent'],
                'issue': 'High memory usage',
                'severity': 'warning'
            })
            analysis['severity'] = 'high'
        
        # Check Packet Loss
        if metrics.get('packet_loss', 0) > 5:
            analysis['anomalies'].append({
                'metric': 'packet_loss',
                'value': metrics['packet_loss'],
                'issue': 'Elevated packet loss',
                'severity': 'critical'
            })
            analysis['severity'] = 'critical'
            analysis['status'] = 'degraded'
        
        # Check Latency
        if metrics.get('latency', 0) > 100:
            analysis['anomalies'].append({
                'metric': 'latency',
                'value': metrics['latency'],
                'issue': 'High latency',
                'severity': 'warning'
            })
            analysis['severity'] = 'high'
        
        # Check Signal Strength
        if metrics.get('signal_strength', 0) < 30:
            analysis['anomalies'].append({
                'metric': 'signal_strength',
                'value': metrics['signal_strength'],
                'issue': 'Weak signal',
                'severity': 'warning'
            })
            analysis['severity'] = 'high'
        
        return analysis
    
    def calculate_statistics(self, data: List[float]) -> Dict:
        """Calculate statistical metrics for data series.
        
        Args:
            data: List of numerical values
        
        Returns:
            Dictionary with min, max, mean, median, and std
        """
        if not data:
            return {'min': 0, 'max': 0, 'mean': 0, 'median': 0, 'std': 0}
        
        stats = {
            'min': min(data),
            'max': max(data),
            'mean': mean(data),
            'median': median(data),
            'count': len(data)
        }
        
        if len(data) > 1:
            stats['std'] = stdev(data)
        else:
            stats['std'] = 0
        
        return stats
    
    def detect_anomalies(self, data: List[float], baseline_mean: Optional[float] = None) -> List[Dict]:
        """Detect anomalies using statistical methods.
        
        Args:
            data: List of metric values
            baseline_mean: Expected mean value for comparison
        
        Returns:
            List of detected anomalies with indices and severity
        """
        if len(data) < 3:
            return []
        
        anomalies = []
        
        if baseline_mean is None:
            baseline_mean = mean(data)
        
        std_dev = stdev(data) if len(data) > 1 else 0
        
        if std_dev == 0:
            return []
        
        upper_threshold = baseline_mean + (self.anomaly_threshold * std_dev)
        lower_threshold = baseline_mean - (self.anomaly_threshold * std_dev)
        
        for idx, value in enumerate(data):
            if value > upper_threshold or value < lower_threshold:
                severity = 'high' if abs(value - baseline_mean) > (3 * std_dev) else 'medium'
                anomalies.append({
                    'index': idx,
                    'value': value,
                    'expected': baseline_mean,
                    'severity': severity,
                    'deviation': abs(value - baseline_mean) / std_dev if std_dev > 0 else 0
                })
        
        return anomalies
    
    def get_trend(self, data: List[float], window_size: int = 5) -> str:
        """Determine trend of metrics (increasing, decreasing, stable).
        
        Args:
            data: List of metric values
            window_size: Window for trend calculation
        
        Returns:
            Trend direction: 'increasing', 'decreasing', or 'stable'
        """
        if len(data) < window_size:
            return 'stable'
        
        recent = data[-window_size:]
        oldest = data[-window_size*2:-window_size] if len(data) >= window_size*2 else data[:window_size]
        
        recent_mean = mean(recent)
        oldest_mean = mean(oldest)
        
        threshold = 5  # 5% change threshold
        change_percent = ((recent_mean - oldest_mean) / oldest_mean * 100) if oldest_mean != 0 else 0
        
        if change_percent > threshold:
            return 'increasing'
        elif change_percent < -threshold:
            return 'decreasing'
        else:
            return 'stable'
