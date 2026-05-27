"""Continuous Network Signal Monitor for real-time monitoring."""

import threading
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Callable
from collections import deque
from .signal_collector import SignalCollector
from .analyzer import SignalAnalyzer
from .alerts import AlertManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ContinuousNetworkMonitor:
    """Continuously monitors network signals and performance metrics.
    
    This class runs in a separate thread to continuously collect and analyze
    network metrics without blocking the main application.
    """
    
    def __init__(
        self,
        interface: str = None,
        collection_interval: float = 1.0,
        history_size: int = 3600,
        alert_thresholds: Optional[Dict[str, float]] = None
    ):
        """Initialize the continuous network monitor.
        
        Args:
            interface: Network interface to monitor (None for all)
            collection_interval: Seconds between collections (default: 1.0)
            history_size: Maximum number of samples to keep (default: 3600)
            alert_thresholds: Dict of metric thresholds for alerts
        """
        self.interface = interface
        self.collection_interval = collection_interval
        self.history_size = history_size
        
        self.collector = SignalCollector(interface)
        self.analyzer = SignalAnalyzer()
        self.alert_manager = AlertManager(alert_thresholds or {})
        
        # Thread management
        self._monitor_thread: Optional[threading.Thread] = None
        self._is_running = False
        self._lock = threading.Lock()
        
        # Data storage
        self.metrics_history: Dict[str, deque] = {
            'timestamps': deque(maxlen=history_size),
            'cpu_percent': deque(maxlen=history_size),
            'memory_percent': deque(maxlen=history_size),
            'network_sent': deque(maxlen=history_size),
            'network_recv': deque(maxlen=history_size),
            'packet_loss': deque(maxlen=history_size),
            'latency': deque(maxlen=history_size),
            'signal_strength': deque(maxlen=history_size),
        }
        
        # Current metrics
        self.current_metrics: Dict = {}
        
        # Callbacks
        self._callbacks: List[Callable] = []
        
        logger.info(f"ContinuousNetworkMonitor initialized for interface: {interface}")
    
    def add_callback(self, callback: Callable) -> None:
        """Add a callback function to be called on each metric collection.
        
        Args:
            callback: Function that takes metrics dict as argument
        """
        self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable) -> None:
        """Remove a callback function.
        
        Args:
            callback: Callback function to remove
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def start(self) -> None:
        """Start continuous monitoring in a background thread."""
        if self._is_running:
            logger.warning("Monitor is already running")
            return
        
        with self._lock:
            self._is_running = True
            self._monitor_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self._monitor_thread.start()
        
        logger.info("Network monitoring started")
    
    def stop(self) -> None:
        """Stop continuous monitoring."""
        if not self._is_running:
            logger.warning("Monitor is not running")
            return
        
        with self._lock:
            self._is_running = False
        
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        
        logger.info("Network monitoring stopped")
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop running in background thread."""
        while self._is_running:
            try:
                # Collect metrics
                metrics = self.collector.collect()
                timestamp = datetime.now()
                
                with self._lock:
                    # Store in history
                    self.metrics_history['timestamps'].append(timestamp)
                    self.metrics_history['cpu_percent'].append(metrics.get('cpu_percent', 0))
                    self.metrics_history['memory_percent'].append(metrics.get('memory_percent', 0))
                    self.metrics_history['network_sent'].append(metrics.get('network_sent', 0))
                    self.metrics_history['network_recv'].append(metrics.get('network_recv', 0))
                    self.metrics_history['packet_loss'].append(metrics.get('packet_loss', 0))
                    self.metrics_history['latency'].append(metrics.get('latency', 0))
                    self.metrics_history['signal_strength'].append(metrics.get('signal_strength', 0))
                    
                    # Update current metrics
                    self.current_metrics = {
                        'timestamp': timestamp,
                        **metrics
                    }
                
                # Analyze metrics and detect anomalies
                analysis = self.analyzer.analyze(self.current_metrics)
                
                # Check for alerts
                alerts = self.alert_manager.check_alerts(self.current_metrics)
                if alerts:
                    logger.warning(f"Alerts triggered: {alerts}")
                
                # Call registered callbacks
                for callback in self._callbacks:
                    try:
                        callback(self.current_metrics)
                    except Exception as e:
                        logger.error(f"Callback error: {e}")
                
                # Sleep before next collection
                time.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.collection_interval)
    
    def get_current_metrics(self) -> Dict:
        """Get the current network metrics.
        
        Returns:
            Dictionary of current metrics
        """
        with self._lock:
            return self.current_metrics.copy()
    
    def get_metrics_summary(self) -> Dict:
        """Get statistical summary of collected metrics.
        
        Returns:
            Dictionary with min, max, mean, and std for each metric
        """
        with self._lock:
            summary = {}
            for metric_name, data in self.metrics_history.items():
                if metric_name != 'timestamps' and len(data) > 0:
                    summary[metric_name] = self.analyzer.calculate_statistics(
                        list(data)
                    )
            return summary
    
    def get_history(self, metric: str, limit: int = 100) -> List:
        """Get historical data for a specific metric.
        
        Args:
            metric: Metric name
            limit: Maximum number of samples to return
        
        Returns:
            List of metric values
        """
        with self._lock:
            if metric in self.metrics_history:
                data = list(self.metrics_history[metric])
                return data[-limit:] if len(data) > limit else data
        return []
    
    def is_running(self) -> bool:
        """Check if monitoring is active.
        
        Returns:
            True if monitoring is running
        """
        return self._is_running
