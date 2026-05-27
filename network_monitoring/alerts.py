"""Alert management for network monitoring."""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AlertManager:
    """Manages alerts for network monitoring thresholds."""
    
    DEFAULT_THRESHOLDS = {
        'cpu_percent': 80,
        'memory_percent': 85,
        'packet_loss': 5,
        'latency': 100,
        'signal_strength': 30,
        'network_bandwidth': 900,  # Mbps
    }
    
    def __init__(self, custom_thresholds: Optional[Dict[str, float]] = None):
        """Initialize the alert manager.
        
        Args:
            custom_thresholds: Custom threshold values
        """
        self.thresholds = {**self.DEFAULT_THRESHOLDS}
        if custom_thresholds:
            self.thresholds.update(custom_thresholds)
        
        self.active_alerts: Dict[str, Dict] = {}
        self.alert_history: List[Dict] = []
    
    def check_alerts(self, metrics: Dict) -> List[Dict]:
        """Check metrics against alert thresholds.
        
        Args:
            metrics: Current metrics dictionary
        
        Returns:
            List of triggered alerts
        """
        triggered_alerts = []
        timestamp = datetime.now()
        
        # Check CPU
        if metrics.get('cpu_percent', 0) > self.thresholds['cpu_percent']:
            alert = self._create_alert(
                'cpu_high',
                'High CPU Usage',
                f"CPU at {metrics.get('cpu_percent', 0):.1f}%",
                'warning',
                timestamp
            )
            triggered_alerts.append(alert)
        
        # Check Memory
        if metrics.get('memory_percent', 0) > self.thresholds['memory_percent']:
            alert = self._create_alert(
                'memory_high',
                'High Memory Usage',
                f"Memory at {metrics.get('memory_percent', 0):.1f}%",
                'warning',
                timestamp
            )
            triggered_alerts.append(alert)
        
        # Check Packet Loss
        if metrics.get('packet_loss', 0) > self.thresholds['packet_loss']:
            alert = self._create_alert(
                'packet_loss_high',
                'Elevated Packet Loss',
                f"Packet loss at {metrics.get('packet_loss', 0):.2f}%",
                'critical',
                timestamp
            )
            triggered_alerts.append(alert)
        
        # Check Latency
        if metrics.get('latency', 0) > self.thresholds['latency']:
            alert = self._create_alert(
                'latency_high',
                'High Latency',
                f"Latency at {metrics.get('latency', 0):.1f}ms",
                'warning',
                timestamp
            )
            triggered_alerts.append(alert)
        
        # Check Signal Strength
        if metrics.get('signal_strength', 0) < self.thresholds['signal_strength']:
            alert = self._create_alert(
                'signal_weak',
                'Weak Signal Strength',
                f"Signal at {metrics.get('signal_strength', 0):.1f}%",
                'warning',
                timestamp
            )
            triggered_alerts.append(alert)
        
        # Update active alerts
        for alert in triggered_alerts:
            alert_id = alert['alert_id']
            self.active_alerts[alert_id] = alert
            self.alert_history.append(alert)
            logger.warning(f"Alert triggered: {alert['title']} - {alert['message']}")
        
        # Clear resolved alerts
        self._clear_resolved_alerts(triggered_alerts, timestamp)
        
        return triggered_alerts
    
    def _create_alert(self, alert_id: str, title: str, message: str, severity: str, timestamp: datetime) -> Dict:
        """Create an alert dictionary.
        
        Args:
            alert_id: Unique alert identifier
            title: Alert title
            message: Alert message
            severity: Alert severity (info, warning, critical)
            timestamp: Alert timestamp
        
        Returns:
            Alert dictionary
        """
        return {
            'alert_id': alert_id,
            'title': title,
            'message': message,
            'severity': severity,
            'timestamp': timestamp,
            'resolved': False
        }
    
    def _clear_resolved_alerts(self, current_alerts: List[Dict], timestamp: datetime) -> None:
        """Clear alerts that are no longer triggered.
        
        Args:
            current_alerts: List of currently triggered alerts
            timestamp: Current timestamp
        """
        current_alert_ids = {alert['alert_id'] for alert in current_alerts}
        
        for alert_id in list(self.active_alerts.keys()):
            if alert_id not in current_alert_ids:
                alert = self.active_alerts.pop(alert_id)
                alert['resolved'] = True
                alert['resolved_at'] = timestamp
                logger.info(f"Alert resolved: {alert['title']}")
    
    def get_active_alerts(self) -> List[Dict]:
        """Get all currently active alerts.
        
        Returns:
            List of active alerts
        """
        return list(self.active_alerts.values())
    
    def get_alert_history(self, limit: int = 100) -> List[Dict]:
        """Get alert history.
        
        Args:
            limit: Maximum number of alerts to return
        
        Returns:
            List of historical alerts
        """
        return self.alert_history[-limit:]
    
    def update_threshold(self, metric: str, value: float) -> None:
        """Update a threshold value.
        
        Args:
            metric: Metric name
            value: New threshold value
        """
        if metric in self.thresholds:
            old_value = self.thresholds[metric]
            self.thresholds[metric] = value
            logger.info(f"Threshold updated: {metric} from {old_value} to {value}")
        else:
            logger.warning(f"Unknown metric for threshold update: {metric}")
    
    def get_thresholds(self) -> Dict[str, float]:
        """Get current threshold configuration.
        
        Returns:
            Dictionary of current thresholds
        """
        return self.thresholds.copy()
