"""Generate reports and export monitoring data."""

import json
import csv
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class MetricsReporter:
    """Generate reports and export monitoring data."""
    
    def __init__(self, output_dir: str = './reports'):
        """Initialize the reporter.
        
        Args:
            output_dir: Directory for report output
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def export_to_json(self, data: Dict, filename: Optional[str] = None) -> str:
        """Export data to JSON file.
        
        Args:
            data: Data to export
            filename: Output filename (auto-generated if None)
        
        Returns:
            Path to exported file
        """
        if filename is None:
            filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.output_dir / filename
        
        try:
            # Convert datetime objects to strings
            data_copy = self._serialize_datetime(data)
            
            with open(filepath, 'w') as f:
                json.dump(data_copy, f, indent=2)
            
            logger.info(f"Data exported to {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            raise
    
    def export_to_csv(self, data: List[Dict], filename: Optional[str] = None) -> str:
        """Export metrics to CSV file.
        
        Args:
            data: List of metric dictionaries
            filename: Output filename (auto-generated if None)
        
        Returns:
            Path to exported file
        """
        if filename is None:
            filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = self.output_dir / filename
        
        try:
            if not data:
                logger.warning("No data to export to CSV")
                return str(filepath)
            
            # Get all unique keys from all dictionaries
            fieldnames = set()
            for record in data:
                fieldnames.update(record.keys())
            fieldnames = sorted(list(fieldnames))
            
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for record in data:
                    # Convert datetime to string
                    row = {}
                    for key, value in record.items():
                        if isinstance(value, datetime):
                            row[key] = value.isoformat()
                        else:
                            row[key] = value
                    writer.writerow(row)
            
            logger.info(f"Data exported to {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            raise
    
    def generate_summary_report(self, metrics_summary: Dict, alerts: List[Dict]) -> str:
        """Generate a text summary report.
        
        Args:
            metrics_summary: Summary statistics for metrics
            alerts: List of recent alerts
        
        Returns:
            Report content as string
        """
        report = []
        report.append("="*60)
        report.append("NETWORK MONITORING SUMMARY REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("="*60)
        report.append("")
        
        # Metrics Summary
        report.append("METRICS SUMMARY")
        report.append("-"*60)
        for metric, stats in metrics_summary.items():
            if isinstance(stats, dict):
                report.append(f"\n{metric}:")
                for key, value in stats.items():
                    if isinstance(value, float):
                        report.append(f"  {key}: {value:.2f}")
                    else:
                        report.append(f"  {key}: {value}")
        
        report.append("")
        report.append("RECENT ALERTS")
        report.append("-"*60)
        if alerts:
            for alert in alerts[-10:]:
                report.append(f"  [{alert.get('severity', 'N/A')}] {alert.get('title', 'N/A')}")
                report.append(f"    Message: {alert.get('message', 'N/A')}")
                report.append(f"    Time: {alert.get('timestamp', 'N/A')}")
                report.append("")
        else:
            report.append("  No recent alerts")
        
        report.append("")
        report.append("="*60)
        
        return "\n".join(report)
    
    def _serialize_datetime(self, obj):
        """Recursively convert datetime objects to strings.
        
        Args:
            obj: Object to serialize
        
        Returns:
            Serialized object
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: self._serialize_datetime(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._serialize_datetime(item) for item in obj]
        return obj
