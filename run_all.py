#!/usr/bin/env python3
"""
Main runner script for all network monitoring and signal analysis programs.
This script demonstrates all the monitoring and analysis capabilities.
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_signal_monitor_demo():
    """Run the signal monitoring demo."""
    print("\n" + "="*70)
    print("RUNNING: Network Signal Monitor Demo")
    print("="*70)
    
    try:
        from network_signal_monitoring.monitor import NetworkSignalMonitor
        
        # Create monitor
        monitor = NetworkSignalMonitor(interface="eth0", interval=1.0)
        monitor.start()
        
        print("\n✓ NetworkSignalMonitor initialized and started")
        print("  Interface: eth0")
        print("  Collection interval: 1.0 seconds")
        
        # Collect some metrics
        print("\nCollecting metrics...")
        for i in range(5):
            metrics = monitor.collect_metrics()
            print(f"  [{i+1}] Signal: {metrics['signal_strength']:.1f}% | "
                  f"Latency: {metrics['latency']:.1f}ms | "
                  f"Bandwidth: {metrics['bandwidth']:.1f}Mbps | "
                  f"Packet Loss: {metrics['packet_loss']:.2f}%")
        
        # Get summary
        summary = monitor.get_metrics_summary(count=5)
        print(f"\n✓ Collected {len(summary)} metrics")
        
        monitor.stop()
        print("✓ Monitor stopped successfully")
        
        return True
    except Exception as e:
        logger.error(f"Error running signal monitor demo: {e}", exc_info=True)
        return False


def run_signal_analyzer_demo():
    """Run the signal analyzer demo."""
    print("\n" + "="*70)
    print("RUNNING: Signal Analyzer Demo")
    print("="*70)
    
    try:
        from network_signal_monitoring.analyzer import SignalAnalyzer
        import random
        
        # Create analyzer
        analyzer = SignalAnalyzer(threshold=2.0)
        print("\n✓ SignalAnalyzer initialized with threshold: 2.0")
        
        # Generate sample data
        print("\nGenerating sample metrics data...")
        metrics_data = [random.uniform(50, 100) for _ in range(20)]
        print(f"  Generated {len(metrics_data)} sample values")
        print(f"  Range: {min(metrics_data):.2f} - {max(metrics_data):.2f}")
        
        # Analyze
        print("\nRunning analysis...")
        analysis = analyzer.analyze(metrics_data)
        
        print(f"  Status: {analysis['status']}")
        print(f"  Mean: {analysis['mean']:.2f}")
        print(f"  Min: {analysis['min']:.2f}")
        print(f"  Max: {analysis['max']:.2f}")
        print(f"  Std Dev: {analysis.get('std_dev', 'N/A')}")
        print(f"  Anomalies detected: {len(analysis['anomalies'])}")
        
        # Test trend detection
        print("\nDetecting trends...")
        trend = analyzer.detect_trend(metrics_data)
        print(f"  Trend: {trend}")
        
        # Test quality score
        print("\nCalculating quality score...")
        test_metrics = {
            'latency': 45.5,
            'packet_loss': 0.5,
            'signal_strength': 85
        }
        score = analyzer.get_quality_score(test_metrics)
        print(f"  Quality Score: {score:.2f}/100")
        
        return True
    except Exception as e:
        logger.error(f"Error running signal analyzer demo: {e}", exc_info=True)
        return False


def run_continuous_monitor_demo():
    """Run the continuous network monitoring demo."""
    print("\n" + "="*70)
    print("RUNNING: Continuous Network Monitoring Demo")
    print("="*70)
    
    try:
        from network_monitoring import ContinuousNetworkMonitor
        from network_monitoring.reporter import MetricsReporter
        import time
        
        # Initialize monitor
        alert_thresholds = {
            'cpu_percent': 75,
            'memory_percent': 80,
            'packet_loss': 3,
            'latency': 80,
        }
        
        monitor = ContinuousNetworkMonitor(
            collection_interval=1.0,
            history_size=100,
            alert_thresholds=alert_thresholds
        )
        
        print("\n✓ ContinuousNetworkMonitor initialized")
        print(f"  Collection interval: 1.0 seconds")
        print(f"  History size: 100 samples")
        print(f"  Alert thresholds: CPU=75%, Memory=80%, PacketLoss=3%, Latency=80ms")
        
        # Add callback
        def on_metrics(metrics):
            pass  # Silent callback
        
        monitor.add_callback(on_metrics)
        monitor.start()
        
        print("\n✓ Monitoring started")
        print("  Collecting metrics for 5 seconds...")
        
        for i in range(5):
            time.sleep(1)
            current = monitor.get_current_metrics()
            if current:
                print(f"  [{i+1}] CPU: {current.get('cpu_percent', 0):.1f}% | "
                      f"Memory: {current.get('memory_percent', 0):.1f}% | "
                      f"Latency: {current.get('latency', 0):.1f}ms")
        
        # Get summary
        summary = monitor.get_metrics_summary()
        print(f"\n✓ Metrics summary collected ({len(summary)} metrics)")
        for metric, stats in list(summary.items())[:3]:
            if isinstance(stats, dict):
                print(f"  {metric}: mean={stats.get('mean', 0):.2f}, "
                      f"min={stats.get('min', 0):.2f}, max={stats.get('max', 0):.2f}")
        
        # Get active alerts
        alerts = monitor.alert_manager.get_active_alerts()
        print(f"\n✓ Active alerts: {len(alerts)}")
        for alert in alerts[:3]:
            print(f"  - [{alert['severity']}] {alert['title']}")
        
        # Export data
        reporter = MetricsReporter(output_dir='./reports')
        print("\n✓ Reporter initialized")
        
        # Export summary
        try:
            json_file = reporter.export_to_json({'summary': summary}, 'demo_summary.json')
            print(f"  ✓ Data exported to JSON: {json_file}")
        except Exception as e:
            logger.debug(f"JSON export skipped: {e}")
        
        monitor.stop()
        print("\n✓ Monitoring stopped successfully")
        
        return True
    except Exception as e:
        logger.error(f"Error running continuous monitor demo: {e}", exc_info=True)
        return False


def main():
    """Run all demonstrations."""
    print("\n" + "="*70)
    print("AI-DRIVEN SDN FOR NETWORK AUTOMATION")
    print("Running All Programs/Demonstrations")
    print("="*70)
    
    results = []
    
    # Run demos
    results.append(("Signal Monitor Demo", run_signal_monitor_demo()))
    results.append(("Signal Analyzer Demo", run_signal_analyzer_demo()))
    results.append(("Continuous Monitor Demo", run_continuous_monitor_demo()))
    
    # Summary
    print("\n" + "="*70)
    print("EXECUTION SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {name}")
    
    print("\n" + "-"*70)
    print(f"Total: {passed}/{total} tests passed")
    print("-"*70)
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
