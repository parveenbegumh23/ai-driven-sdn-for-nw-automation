# AI-Driven SDN for Network Automation

A comprehensive network monitoring and automation solution powered by AI/ML for Software-Defined Networking (SDN).

## Features

### Continuous Network Monitoring
- **Real-time Metrics Collection**: CPU, memory, network I/O, latency, packet loss
- **Background Threading**: Non-blocking continuous monitoring in separate thread
- **Configurable Intervals**: Adjustable collection frequency and history retention
- **Alert Management**: Threshold-based alerting system with severity levels
- **Extensible Callbacks**: Register custom functions for metric updates

### Signal Analysis
- **Statistical Analysis**: Min, max, mean, median, standard deviation
- **Anomaly Detection**: Statistical deviation-based anomaly identification
- **Trend Analysis**: Identify increasing, decreasing, or stable trends
- **Network Quality Assessment**: Evaluate overall network health

### Reporting & Export
- **JSON Export**: Export metrics and summary data
- **CSV Export**: Export time-series data for analysis
- **Summary Reports**: Generated text reports with metrics and alerts
- **Alert History**: Track all triggered alerts and their resolution

## Installation

### Prerequisites
- Python 3.7+
- pip

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd ai-driven-sdn-for-nw-automation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
from network_monitoring import ContinuousNetworkMonitor

# Initialize monitor
monitor = ContinuousNetworkMonitor(
    collection_interval=1.0,  # Collect every second
    history_size=3600,        # Keep 1 hour of data
)

# Start monitoring
monitor.start()

# Get current metrics
current_metrics = monitor.get_current_metrics()
print(f"CPU: {current_metrics['cpu_percent']:.1f}%")
print(f"Memory: {current_metrics['memory_percent']:.1f}%")
print(f"Latency: {current_metrics['latency']:.1f}ms")

# Get historical summary
summary = monitor.get_metrics_summary()
print(summary)

# Stop monitoring
monitor.stop()
```

### With Alerts

```python
from network_monitoring import ContinuousNetworkMonitor

alert_thresholds = {
    'cpu_percent': 80,
    'memory_percent': 85,
    'packet_loss': 5,
    'latency': 100,
}

monitor = ContinuousNetworkMonitor(alert_thresholds=alert_thresholds)
monitor.start()

# Get active alerts
alerts = monitor.alert_manager.get_active_alerts()
for alert in alerts:
    print(f"[{alert['severity']}] {alert['title']}: {alert['message']}")
```

### With Callbacks

```python
def on_metrics_update(metrics):
    print(f"CPU: {metrics['cpu_percent']:.1f}%")
    if metrics['packet_loss'] > 0:
        print(f"Packet Loss: {metrics['packet_loss']:.2f}%")

monitor = ContinuousNetworkMonitor()
monitor.add_callback(on_metrics_update)
monitor.start()
```

### Export Data

```python
from network_monitoring.reporter import MetricsReporter

reporter = MetricsReporter(output_dir='./reports')

# Export current metrics to JSON
monitor_data = {
    'current': monitor.get_current_metrics(),
    'summary': monitor.get_metrics_summary()
}
json_file = reporter.export_to_json(monitor_data, 'metrics.json')

# Export history to CSV
history = []
for i in range(len(monitor.metrics_history['timestamps'])):
    history.append({
        'timestamp': list(monitor.metrics_history['timestamps'])[i],
        'cpu_percent': list(monitor.metrics_history['cpu_percent'])[i],
        'memory_percent': list(monitor.metrics_history['memory_percent'])[i],
        'latency': list(monitor.metrics_history['latency'])[i],
    })
csv_file = reporter.export_to_csv(history, 'history.csv')
```

## Examples

See the `examples/` directory for complete working examples:

- `continuous_monitor_example.py` - Demonstrates continuous monitoring with callbacks and reporting

Run examples:
```bash
python examples/continuous_monitor_example.py
```

## Architecture

### Core Components

**ContinuousNetworkMonitor** (`network_monitoring/monitor.py`)
- Main monitoring orchestrator
- Runs collection loop in background thread
- Manages metric history and current state
- Coordinates with collector, analyzer, and alert manager

**SignalCollector** (`network_monitoring/signal_collector.py`)
- Gathers system and network metrics
- Uses psutil for system metrics
- Estimates network quality indicators
- Supports per-interface monitoring

**SignalAnalyzer** (`network_monitoring/analyzer.py`)
- Statistical analysis of metrics
- Anomaly detection using standard deviation
- Trend identification
- Network status assessment

**AlertManager** (`network_monitoring/alerts.py`)
- Threshold-based alert triggering
- Alert history tracking
- Dynamic threshold updates
- Severity-based classification

**MetricsReporter** (`network_monitoring/reporter.py`)
- Export data to JSON and CSV
- Generate summary reports
- Historical data formatting

## Metrics Collected

- **cpu_percent**: System CPU usage (0-100%)
- **memory_percent**: System memory usage (0-100%)
- **network_sent**: Total bytes sent
- **network_recv**: Total bytes received
- **packet_loss**: Estimated packet loss percentage
- **latency**: Network latency in milliseconds
- **signal_strength**: Wireless signal strength (0-100%)
- **active_connections**: Number of active network connections

## Default Alert Thresholds

- CPU: 80%
- Memory: 85%
- Packet Loss: 5%
- Latency: 100ms
- Signal Strength: 30%

## Thread Safety

The monitor uses thread-safe operations with locking mechanisms to ensure data consistency when accessing metrics from multiple threads.

## API Reference

### ContinuousNetworkMonitor

```python
monitor = ContinuousNetworkMonitor(
    interface=None,              # Network interface to monitor
    collection_interval=1.0,     # Seconds between collections
    history_size=3600,           # Max samples to keep
    alert_thresholds={}          # Custom alert thresholds
)

monitor.start()                  # Start background monitoring
monitor.stop()                   # Stop monitoring
monitor.is_running()             # Check if running
monitor.add_callback(fn)         # Register update callback
monitor.remove_callback(fn)      # Unregister callback
monitor.get_current_metrics()    # Get latest metrics
monitor.get_metrics_summary()    # Get statistical summary
monitor.get_history(metric, limit)  # Get historical data
```

## Configuration

Create a `config.json` file to customize settings:

```json
{
  "collection_interval": 1.0,
  "history_size": 3600,
  "alert_thresholds": {
    "cpu_percent": 80,
    "memory_percent": 85,
    "packet_loss": 5,
    "latency": 100
  }
}
```

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=network_monitoring

# Run specific test
pytest tests/test_monitor.py::test_monitor_start
```

## Performance Considerations

- **Collection Interval**: Smaller intervals provide more granular data but consume more CPU
- **History Size**: Larger history consumes more memory
- **Thread Safety**: Uses efficient locking to minimize contention
- **Typical Overhead**: <1% CPU per monitoring instance

## Future Enhancements

- [ ] Machine learning-based anomaly detection
- [ ] Predictive analytics for network trends
- [ ] Integration with SDN controllers (OpenDaylight, ONOS)
- [ ] Real-time dashboard and visualization
- [ ] Distributed monitoring across multiple nodes
- [ ] Automatic remediation actions
- [ ] Advanced packet analysis and DPI
- [ ] Kubernetes and container network monitoring

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or suggestions, please open a GitHub issue.

---

**Last Updated**: 2026-05-27
