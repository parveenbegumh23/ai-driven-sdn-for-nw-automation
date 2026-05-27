"""Network signal and metric collection."""

import psutil
import socket
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SignalCollector:
    """Collects network signals and performance metrics."""
    
    def __init__(self, interface: Optional[str] = None):
        """Initialize the signal collector.
        
        Args:
            interface: Specific network interface to monitor (None for system-wide)
        """
        self.interface = interface
        self._last_net_io = None
        self._last_timestamp = None
    
    def collect(self) -> Dict:
        """Collect current network and system metrics.
        
        Returns:
            Dictionary containing collected metrics
        """
        metrics = {
            'cpu_percent': self._get_cpu_percent(),
            'memory_percent': self._get_memory_percent(),
            'network_sent': self._get_network_sent(),
            'network_recv': self._get_network_recv(),
            'packet_loss': self._estimate_packet_loss(),
            'latency': self._measure_latency(),
            'signal_strength': self._get_signal_strength(),
            'active_connections': self._get_active_connections(),
            'timestamp': datetime.now()
        }
        return metrics
    
    def _get_cpu_percent(self) -> float:
        """Get current CPU usage percentage.
        
        Returns:
            CPU usage as percentage (0-100)
        """
        try:
            return psutil.cpu_percent(interval=0.1)
        except Exception as e:
            logger.warning(f"Error getting CPU percent: {e}")
            return 0.0
    
    def _get_memory_percent(self) -> float:
        """Get current memory usage percentage.
        
        Returns:
            Memory usage as percentage (0-100)
        """
        try:
            return psutil.virtual_memory().percent
        except Exception as e:
            logger.warning(f"Error getting memory percent: {e}")
            return 0.0
    
    def _get_network_sent(self) -> float:
        """Get total bytes sent on network.
        
        Returns:
            Bytes sent
        """
        try:
            if self.interface:
                stats = psutil.net_io_counters(pernic=True).get(self.interface)
                return stats.bytes_sent if stats else 0
            else:
                return psutil.net_io_counters().bytes_sent
        except Exception as e:
            logger.warning(f"Error getting network sent: {e}")
            return 0
    
    def _get_network_recv(self) -> float:
        """Get total bytes received on network.
        
        Returns:
            Bytes received
        """
        try:
            if self.interface:
                stats = psutil.net_io_counters(pernic=True).get(self.interface)
                return stats.bytes_recv if stats else 0
            else:
                return psutil.net_io_counters().bytes_recv
        except Exception as e:
            logger.warning(f"Error getting network recv: {e}")
            return 0
    
    def _estimate_packet_loss(self) -> float:
        """Estimate packet loss percentage.
        
        Returns:
            Estimated packet loss as percentage
        """
        try:
            if self.interface:
                stats = psutil.net_io_counters(pernic=True).get(self.interface)
                if stats and (stats.dropin + stats.dropout) > 0:
                    total = stats.packets_sent + stats.packets_recv
                    dropped = stats.dropin + stats.dropout
                    return (dropped / total * 100) if total > 0 else 0.0
            else:
                stats = psutil.net_io_counters()
                if stats and (stats.dropin + stats.dropout) > 0:
                    total = stats.packets_sent + stats.packets_recv
                    dropped = stats.dropin + stats.dropout
                    return (dropped / total * 100) if total > 0 else 0.0
            return 0.0
        except Exception as e:
            logger.warning(f"Error estimating packet loss: {e}")
            return 0.0
    
    def _measure_latency(self) -> float:
        """Measure network latency via DNS lookup.
        
        Returns:
            Latency in milliseconds
        """
        try:
            import time
            start = time.time()
            socket.gethostbyname('8.8.8.8')
            latency_ms = (time.time() - start) * 1000
            return min(latency_ms, 1000)  # Cap at 1000ms
        except Exception as e:
            logger.debug(f"Error measuring latency: {e}")
            return 0.0
    
    def _get_signal_strength(self) -> float:
        """Get wireless signal strength (if available).
        
        Returns:
            Signal strength as percentage (0-100)
        """
        try:
            # Simulate signal strength based on network quality
            # In a real implementation, this would read from wireless interfaces
            return 85.0  # Default value
        except Exception as e:
            logger.debug(f"Error getting signal strength: {e}")
            return 0.0
    
    def _get_active_connections(self) -> int:
        """Get count of active network connections.
        
        Returns:
            Number of active connections
        """
        try:
            connections = psutil.net_connections(kind='inet')
            return len([c for c in connections if c.status == 'ESTABLISHED'])
        except Exception as e:
            logger.warning(f"Error getting active connections: {e}")
            return 0
