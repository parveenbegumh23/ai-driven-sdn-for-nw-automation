"""Comprehensive test suite for network monitoring and analysis."""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestNetworkSignalMonitor:
    """Test cases for NetworkSignalMonitor class."""
    
    def test_monitor_initialization(self):
        """Test monitor initialization."""
        from network_signal_monitoring.monitor import NetworkSignalMonitor
        
        monitor = NetworkSignalMonitor(interface="eth0", interval=1.0)
        assert monitor.interface == "eth0"
        assert monitor.interval == 1.0
        assert monitor.is_monitoring == False
        assert len(monitor.metrics) == 0
    
    def test_monitor_start_stop(self):
        """Test monitor start and stop."""
        from network_signal_monitoring.monitor import NetworkSignalMonitor
        
        monitor = NetworkSignalMonitor()
        monitor.start()
        assert monitor.is_monitoring == True
        
        monitor.stop()
        assert monitor.is_monitoring == False
    
    def test_collect_metrics(self):
        """Test metrics collection."""
        from network_signal_monitoring.monitor import NetworkSignalMonitor
        
        monitor = NetworkSignalMonitor()
        metric = monitor.collect_metrics()
        
        assert 'timestamp' in metric
        assert 'interface' in metric
        assert 'signal_strength' in metric
        assert 'latency' in metric
        assert 'bandwidth' in metric
        assert 'packet_loss' in metric
        
        # Verify metrics are within expected ranges
        assert 0 <= metric['signal_strength'] <= 100
        assert 0 <= metric['packet_loss'] <= 100
        assert metric['latency'] >= 0
        assert metric['bandwidth'] >= 0
    
    def test_multiple_metrics_collection(self):
        """Test collecting multiple metrics."""
        from network_signal_monitoring.monitor import NetworkSignalMonitor
        
        monitor = NetworkSignalMonitor()
        
        for _ in range(5):
            monitor.collect_metrics()
        
        assert len(monitor.metrics) == 5
    
    def test_metrics_summary(self):
        """Test metrics summary retrieval."""
        from network_signal_monitoring.monitor import NetworkSignalMonitor
        
        monitor = NetworkSignalMonitor()
        
        for _ in range(3):
            monitor.collect_metrics()
        
        summary = monitor.get_metrics_summary()
        assert len(summary) == 3
        
        # Test with count limit
        summary_limited = monitor.get_metrics_summary(count=2)
        assert len(summary_limited) == 2
    
    def test_reset_metrics(self):
        """Test metrics reset."""
        from network_signal_monitoring.monitor import NetworkSignalMonitor
        
        monitor = NetworkSignalMonitor()
        monitor.collect_metrics()
        assert len(monitor.metrics) > 0
        
        monitor.reset_metrics()
        assert len(monitor.metrics) == 0


class TestSignalAnalyzer:
    """Test cases for SignalAnalyzer class."""
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        from network_signal_monitoring.analyzer import SignalAnalyzer
        
        analyzer = SignalAnalyzer(threshold=2.0)
        assert analyzer.threshold == 2.0
        assert analyzer.baseline is None
    
    def test_analyze_metrics(self):
        """Test metric analysis."""
        from network_signal_monitoring.analyzer import SignalAnalyzer
        
        analyzer = SignalAnalyzer()
        metrics_data = [50, 55, 60, 65, 70, 75, 80, 85, 90, 95]
        
        analysis = analyzer.analyze(metrics_data)
        
        assert analysis['count'] == 10
        assert analysis['min'] == 50
        assert analysis['max'] == 95
        assert 'mean' in analysis
        assert 'status' in analysis
    
    def test_analyze_insufficient_data(self):
        """Test analysis with insufficient data."""
        from network_signal_monitoring.analyzer import SignalAnalyzer
        
        analyzer = SignalAnalyzer()
        metrics_data = [50]
        
        analysis = analyzer.analyze(metrics_data)
        assert analysis['status'] == 'insufficient_data'
    
    def test_anomaly_detection(self):
        """Test anomaly detection."""
        from network_signal_monitoring.analyzer import SignalAnalyzer
        
        analyzer = SignalAnalyzer(threshold=1.0)
        # Create data with an outlier
        metrics_data = [50, 50, 50, 50, 50, 50, 50, 50, 50, 200]
        
        analysis = analyzer.analyze(metrics_data)
        assert analysis['status'] == 'anomaly_detected'
        assert len(analysis['anomalies']) > 0
    
    def test_set_baseline(self):
        """Test baseline setting."""
        from network_signal_monitoring.analyzer import SignalAnalyzer
        
        analyzer = SignalAnalyzer()
        analyzer.set_baseline(100.0)
        
        assert analyzer.baseline == 100.0
    
    def test_compare_to_baseline(self):
        """Test baseline comparison."""
        from network_signal_monitoring.analyzer import SignalAnalyzer
        
        analyzer = SignalAnalyzer()
        analyzer.set_baseline(100.0)
        
        result = analyzer.compare_to_baseline(110.0)
        
        assert result['baseline'] == 100.0
        assert result['current_value'] == 110.0
        assert 'deviation_percent' in result
    
    def test_trend_detection_increasing(self):
        """Test trend detection for increasing values."""
        from network_signal_monitoring.analyzer import SignalAnalyzer
        
        analyzer = SignalAnalyzer()
        metrics_data = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        
        trend = analyzer.detect_trend(metrics_data)
        assert trend == 'increasing'
    
    def test_trend_detection_decreasing(self):
        """Test trend detection for decreasing values."""
        from network_signal_monitoring.analyzer import SignalAnalyzer
        
        analyzer = SignalAnalyzer()
        metrics_data = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10]
        
        trend = analyzer.detect_trend(metrics_data)
        assert trend == 'decreasing'
    
    def test_trend_detection_stable(self):
        """Test trend detection for stable values."""
        from network_signal_monitoring.analyzer import SignalAnalyzer
        
        analyzer = SignalAnalyzer()
        metrics_data = [50, 50, 50, 50, 50, 50, 50, 50, 50, 50]
        
        trend = analyzer.detect_trend(metrics_data)
        assert trend == 'stable'
    
    def test_quality_score_calculation(self):
        """Test quality score calculation."""
        from network_signal_monitoring.analyzer import SignalAnalyzer
        
        analyzer = SignalAnalyzer()
        metrics = {
            'latency': 50,
            'packet_loss': 1,
            'signal_strength': 85
        }
        
        score = analyzer.get_quality_score(metrics)
        
        assert 0 <= score <= 100
        assert score > 50  # Should be good quality with these metrics
    
    def test_quality_score_poor(self):
        """Test quality score with poor metrics."""
        from network_signal_monitoring.analyzer import SignalAnalyzer
        
        analyzer = SignalAnalyzer()
        metrics = {
            'latency': 200,
            'packet_loss': 10,
            'signal_strength': 20
        }
        
        score = analyzer.get_quality_score(metrics)
        
        assert 0 <= score <= 100
        assert score < 50  # Should be poor quality


class TestIntegration:
    """Integration tests combining multiple components."""
    
    def test_monitor_and_analyzer_integration(self):
        """Test monitor and analyzer working together."""
        from network_signal_monitoring.monitor import NetworkSignalMonitor
        from network_signal_monitoring.analyzer import SignalAnalyzer
        
        monitor = NetworkSignalMonitor()
        analyzer = SignalAnalyzer()
        
        # Collect metrics
        for _ in range(10):
            monitor.collect_metrics()
        
        # Extract signal strengths
        signal_strengths = [m['signal_strength'] for m in monitor.metrics]
        
        # Analyze
        analysis = analyzer.analyze(signal_strengths)
        
        assert analysis['count'] == 10
        assert 'mean' in analysis
        assert 'std_dev' in analysis
    
    def test_full_workflow(self):
        """Test complete monitoring workflow."""
        from network_signal_monitoring.monitor import NetworkSignalMonitor
        from network_signal_monitoring.analyzer import SignalAnalyzer
        
        monitor = NetworkSignalMonitor(interval=0.1)
        analyzer = SignalAnalyzer()
        
        monitor.start()
        
        # Collect metrics
        for _ in range(5):
            monitor.collect_metrics()
        
        monitor.stop()
        
        # Analyze
        signal_data = [m['signal_strength'] for m in monitor.metrics]
        analysis = analyzer.analyze(signal_data)
        
        assert monitor.is_monitoring == False
        assert len(monitor.metrics) == 5
        assert analysis['status'] in ['normal', 'anomaly_detected']


class TestPerformance:
    """Performance and load tests."""
    
    def test_large_dataset_analysis(self):
        """Test analyzing large dataset."""
        from network_signal_monitoring.analyzer import SignalAnalyzer
        import random
        
        analyzer = SignalAnalyzer()
        metrics_data = [random.uniform(40, 100) for _ in range(1000)]
        
        analysis = analyzer.analyze(metrics_data)
        
        assert analysis['count'] == 1000
        assert 'mean' in analysis
        assert 'std_dev' in analysis
    
    def test_many_metrics_collection(self):
        """Test collecting many metrics."""
        from network_signal_monitoring.monitor import NetworkSignalMonitor
        
        monitor = NetworkSignalMonitor()
        
        for _ in range(100):
            monitor.collect_metrics()
        
        assert len(monitor.metrics) == 100
        summary = monitor.get_metrics_summary(count=50)
        assert len(summary) == 50


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_metric_values(self):
        """Test handling of invalid metric values."""
        from network_signal_monitoring.analyzer import SignalAnalyzer
        
        analyzer = SignalAnalyzer()
        
        # Empty list should be handled
        analysis = analyzer.analyze([])
        assert analysis['count'] == 0
    
    def test_baseline_without_comparison(self):
        """Test baseline comparison without setting baseline."""
        from network_signal_monitoring.analyzer import SignalAnalyzer
        
        analyzer = SignalAnalyzer()
        result = analyzer.compare_to_baseline(100.0)
        
        assert result['status'] == 'no_baseline'
    
    def test_trend_with_insufficient_data(self):
        """Test trend detection with insufficient data."""
        from network_signal_monitoring.analyzer import SignalAnalyzer
        
        analyzer = SignalAnalyzer()
        trend = analyzer.detect_trend([50, 60])
        
        assert trend == 'insufficient_data'


# Test execution
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
