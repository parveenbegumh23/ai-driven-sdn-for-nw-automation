#!/usr/bin/env python3
"""
Example: UNSW-NB15 Real-time Network Intrusion Detection.
"""

import logging
import numpy as np
import time
import pickle
from pathlib import Path
from network_monitoring import ContinuousNetworkMonitor
from network_monitoring.unsw_dataset_loader import UNSWDatasetLoader

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UNSWDetector:
    """Real-time network intrusion detection using UNSW models."""
    
    def __init__(self, model_dir: str = './models'):
        """Initialize detector.
        
        Args:
            model_dir: Directory containing trained models
        """
        self.model_dir = Path(model_dir)
        self.models = {}
        self.processed_data = None
        self.dataset_loader = UNSWDatasetLoader()
        self.load_models()
    
    def load_models(self):
        """Load trained models."""
        model_files = {
            'rf_binary': 'rf_binary.pkl',
            'gb_binary': 'gb_binary.pkl',
            'rf_multiclass': 'rf_multiclass.pkl',
            'anomaly_detector': 'anomaly_detector.pkl'
        }
        
        for model_name, filename in model_files.items():
            filepath = self.model_dir / filename
            if filepath.exists():
                with open(filepath, 'rb') as f:
                    self.models[model_name] = pickle.load(f)
                logger.info(f"Loaded model: {model_name}")
            else:
                logger.warning(f"Model not found: {filepath}")
        
        # Load processed data for scaler
        processed_file = self.model_dir.parent / 'datasets' / 'unsw_nb15_processed.pkl'
        if processed_file.exists():
            self.processed_data = self.dataset_loader.load_processed_data(
                processed_file.name
            )
            logger.info("Loaded processed data with scaler")
    
    def detect_intrusion(self, features: np.ndarray) -> dict:
        """Detect network intrusion.
        
        Args:
            features: Feature array from network metrics
            
        Returns:
            Detection results dictionary
        """
        results = {
            'timestamp': time.time(),
            'is_attack': False,
            'confidence': 0.0,
            'anomaly_score': 0.0,
            'attack_type': 'Normal'
        }
        
        # Binary classification
        if 'rf_binary' in self.models:
            model = self.models['rf_binary']
            prediction = model.predict([features])[0]
            probabilities = model.predict_proba([features])[0]
            
            results['is_attack'] = prediction == 1
            results['confidence'] = float(probabilities[1])
            
            if prediction == 1:
                logger.warning(f"INTRUSION DETECTED! Confidence: {results['confidence']:.2%}")
        
        # Multi-class classification
        if 'rf_multiclass' in self.models and results['is_attack']:
            model = self.models['rf_multiclass']
            attack_pred = model.predict([features])[0]
            attack_proba = model.predict_proba([features])[0]
            
            results['attack_type'] = str(attack_pred)
            results['attack_confidence'] = float(max(attack_proba))
        
        # Anomaly detection
        if 'anomaly_detector' in self.models:
            detector = self.models['anomaly_detector']
            anomaly_pred = detector.detect(np.array([features]))[0]
            anomaly_score = detector.get_anomaly_scores(np.array([features]))[0]
            
            results['anomaly_score'] = float(anomaly_score)
            results['is_anomalous'] = anomaly_pred == -1
        
        return results


def run_real_time_detection():
    """Run real-time network intrusion detection."""
    
    print("\n" + "="*70)
    print("UNSW-NB15 REAL-TIME NETWORK INTRUSION DETECTION")
    print("="*70)
    
    # Initialize detector
    print("\n[1] Initializing detector...")
    detector = UNSWDetector(model_dir='./models')
    
    if not detector.models:
        print("✗ No trained models found. Run 'python train_unsw_model.py' first.")
        return
    
    print(f"✓ Loaded {len(detector.models)} models")
    
    # Initialize monitor
    print("\n[2] Starting network monitor...")
    monitor = ContinuousNetworkMonitor(collection_interval=2.0)
    
    # Create detection callback
    detection_results = {
        'total': 0,
        'attacks': 0,
        'anomalies': 0,
        'alerts': []
    }
    
    def detection_callback(metrics):
        """Callback for network metrics with detection."""
        try:
            # Prepare features (same format as UNSW training)
            features = np.array([
                metrics.get('cpu_percent', 0),
                metrics.get('memory_percent', 0),
                metrics.get('network_sent', 0),
                metrics.get('network_recv', 0),
                metrics.get('packet_loss', 0),
                metrics.get('latency', 0),
                metrics.get('signal_strength', 0),
                metrics.get('active_connections', 0)
            ])
            
            # Normalize features if scaler available
            if detector.processed_data:
                scaler_params = detector.processed_data.get('scaler_params', {})
                if scaler_params:
                    min_vals = np.array(scaler_params.get('min', [0]*8))
                    range_vals = np.array(scaler_params.get('range', [1]*8))
                    features = (features - min_vals[:len(features)]) / range_vals[:len(features)]
            
            # Run detection
            result = detector.detect_intrusion(features)
            detection_results['total'] += 1
            
            if result['is_attack']:
                detection_results['attacks'] += 1
                alert = f"ALERT: Attack detected! Type: {result['attack_type']}, " \
                       f"Confidence: {result['confidence']:.2%}"
                detection_results['alerts'].append(alert)
                print(f"  ⚠️  {alert}")
            
            if result.get('is_anomalous', False):
                detection_results['anomalies'] += 1
                anomaly_alert = f"ANOMALY: Score: {result['anomaly_score']:.4f}"
                print(f"  ⚠️  {anomaly_alert}")
            
            # Log results
            logger.debug(f"Detection result: {result}")
        
        except Exception as e:
            logger.error(f"Detection error: {e}")
    
    monitor.add_callback(detection_callback)
    monitor.start()
    
    # Run detection
    print("\n[3] Running detection for 30 seconds...")
    try:
        for i in range(15):
            time.sleep(2)
            current = monitor.get_current_metrics()
            if current:
                print(f"[{i+1}] Monitoring... "
                      f"CPU: {current.get('cpu_percent', 0):.1f}% | "
                      f"Memory: {current.get('memory_percent', 0):.1f}% | "
                      f"Latency: {current.get('latency', 0):.1f}ms")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    
    monitor.stop()
    
    # Report results
    print("\n" + "="*70)
    print("DETECTION RESULTS")
    print("="*70)
    print(f"Total detections: {detection_results['total']}")
    print(f"Attacks detected: {detection_results['attacks']}")
    print(f"Anomalies detected: {detection_results['anomalies']}")
    
    if detection_results['alerts']:
        print(f"\nAlerts ({len(detection_results['alerts'])}):")
        for alert in detection_results['alerts'][:5]:
            print(f"  - {alert}")
        if len(detection_results['alerts']) > 5:
            print(f"  ... and {len(detection_results['alerts']) - 5} more")


if __name__ == '__main__':
    run_real_time_detection()
