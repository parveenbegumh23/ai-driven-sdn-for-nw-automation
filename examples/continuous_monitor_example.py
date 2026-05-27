"""Example script demonstrating continuous network monitoring."""

import time
import logging
from network_monitoring import ContinuousNetworkMonitor
from network_monitoring.reporter import MetricsReporter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def metric_callback(metrics):
    """Callback function for metrics updates.
    
    Args:
        metrics: Current metrics dictionary
    """
    logger.info(f"CPU: {metrics.get('cpu_percent', 0):.1f}% | "
                f"Memory: {metrics.get('memory_percent', 0):.1f}% | "
                f"Latency: {metrics.get('latency', 0):.1f}ms")


def main():
    """Main example function."""
    
    # Initialize monitor with custom thresholds
    alert_thresholds = {
        'cpu_percent': 75,
        'memory_percent': 80,
        'packet_loss': 3,
        'latency': 80,
    }
    
    monitor = ContinuousNetworkMonitor(
        collection_interval=2.0,  # Collect every 2 seconds
        history_size=300,  # Keep last 300 samples (10 minutes)
        alert_thresholds=alert_thresholds
    )
    
    # Add callback for metric updates
    monitor.add_callback(metric_callback)
    
    # Start monitoring
    monitor.start()
    logger.info("Started continuous network monitoring...")
    
    # Let it run for 30 seconds
    try:
        for i in range(15):
            time.sleep(2)
            
            # Print current metrics
            current = monitor.get_current_metrics()
            if current:
                print(f"\n[{i+1}] Current Metrics:")
                print(f"  CPU: {current.get('cpu_percent', 0):.1f}%")
                print(f"  Memory: {current.get('memory_percent', 0):.1f}%")
                print(f"  Sent: {current.get('network_sent', 0):.0f} bytes")
                print(f"  Received: {current.get('network_recv', 0):.0f} bytes")
                print(f"  Packet Loss: {current.get('packet_loss', 0):.2f}%")
                print(f"  Latency: {current.get('latency', 0):.1f}ms")
                print(f"  Active Connections: {current.get('active_connections', 0)}")
    
    except KeyboardInterrupt:
        logger.info("Monitoring interrupted by user")
    
    finally:
        # Stop monitoring
        monitor.stop()
        logger.info("Monitoring stopped")
        
        # Get and display summary
        summary = monitor.get_metrics_summary()
        print("\n" + "="*60)
        print("MONITORING SUMMARY")
        print("="*60)
        for metric, stats in summary.items():
            print(f"\n{metric}:")
            for key, value in stats.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.2f}")
                else:
                    print(f"  {key}: {value}")
        
        # Export data
        reporter = MetricsReporter()
        
        # Get history for export
        history_data = []
        for i in range(len(monitor.metrics_history['timestamps'])):
            history_data.append({
                'timestamp': list(monitor.metrics_history['timestamps'])[i],
                'cpu_percent': list(monitor.metrics_history['cpu_percent'])[i],
                'memory_percent': list(monitor.metrics_history['memory_percent'])[i],
                'latency': list(monitor.metrics_history['latency'])[i],
                'packet_loss': list(monitor.metrics_history['packet_loss'])[i],
            })
        
        if history_data:
            csv_file = reporter.export_to_csv(history_data)
            logger.info(f"Metrics exported to {csv_file}")
        
        # Generate and print summary report
        alerts = monitor.alert_manager.get_alert_history()
        report = reporter.generate_summary_report(summary, alerts)
        print("\n" + report)


if __name__ == "__main__":
    main()
