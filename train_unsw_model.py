#!/usr/bin/env python3
"""
UNSW-NB15 Training Script for Network Intrusion Detection.
"""

import logging
import numpy as np
from pathlib import Path
from network_monitoring.unsw_dataset_loader import UNSWDatasetLoader
from network_monitoring.ml_model import NetworkPredictionModel, AnomalyDetector
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score,
    precision_score, recall_score, f1_score, roc_auc_score, roc_curve
)
import matplotlib.pyplot as plt
import seaborn as sns
import pickle

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UNSWTrainer:
    """Train models on UNSW-NB15 dataset."""
    
    def __init__(self, dataset_dir: str = './datasets', model_dir: str = './models'):
        """Initialize trainer.
        
        Args:
            dataset_dir: Directory containing datasets
            model_dir: Directory to store models
        """
        self.dataset_dir = dataset_dir
        self.model_dir = model_dir
        self.loader = UNSWDatasetLoader(dataset_dir)
        self.models = {}
        self.metrics = {}
    
    def load_and_preprocess(self, filename: str = 'UNSW-NB15_1.csv'):
        """Load and preprocess dataset.
        
        Args:
            filename: Dataset filename
            
        Returns:
            Processed data dictionary
        """
        print("\n" + "="*70)
        print("[STEP 1] Loading UNSW-NB15 Dataset")
        print("="*70)
        
        try:
            self.loader.load_dataset(filename)
            stats = self.loader.get_statistics()
            
            print(f"✓ Dataset loaded successfully")
            print(f"  Total samples: {stats['total_samples']}")
            print(f"  Total features: {stats['total_features']}")
            
            if 'binary_classes' in stats:
                print(f"  Class distribution:")
                for cls, count in stats['binary_classes'].items():
                    pct = (count / stats['total_samples']) * 100
                    print(f"    - {cls}: {count} ({pct:.1f}%)")
            
            if 'attack_categories' in stats:
                print(f"  Attack categories:")
                for cat, count in sorted(stats['attack_categories'].items(), 
                                        key=lambda x: x[1], reverse=True)[:5]:
                    print(f"    - {cat}: {count}")
        
        except FileNotFoundError as e:
            print(f"✗ Error: {e}")
            return None
        
        print("\n" + "="*70)
        print("[STEP 2] Preprocessing Dataset")
        print("="*70)
        
        processed_data = self.loader.preprocess(test_split=0.2)
        
        print(f"✓ Preprocessing complete")
        print(f"  Training samples: {processed_data['num_train']}")
        print(f"  Testing samples: {processed_data['num_test']}")
        print(f"  Features: {processed_data['num_features']}")
        
        return processed_data
    
    def train_binary_classifier(self, processed_data: dict):
        """Train binary attack/normal classifier.
        
        Args:
            processed_data: Preprocessed data dictionary
        """
        print("\n" + "="*70)
        print("[STEP 3] Training Binary Classifier (Normal vs Attack)")
        print("="*70)
        
        X_train = processed_data['X_train']
        X_test = processed_data['X_test']
        y_train = processed_data['y_train_binary']
        y_test = processed_data['y_test_binary']
        
        if y_train is None:
            print("✗ Binary labels not available in dataset")
            return
        
        # Train Random Forest
        print("\n[3a] Training Random Forest Classifier...")
        rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            n_jobs=-1,
            random_state=42
        )
        rf_model.fit(X_train, y_train)
        
        y_pred_rf = rf_model.predict(X_test)
        y_proba_rf = rf_model.predict_proba(X_test)[:, 1]
        
        rf_metrics = {
            'accuracy': accuracy_score(y_test, y_pred_rf),
            'precision': precision_score(y_test, y_pred_rf),
            'recall': recall_score(y_test, y_pred_rf),
            'f1': f1_score(y_test, y_pred_rf),
            'auc': roc_auc_score(y_test, y_proba_rf),
        }
        
        print(f"  ✓ Random Forest trained")
        print(f"    Accuracy: {rf_metrics['accuracy']:.4f}")
        print(f"    Precision: {rf_metrics['precision']:.4f}")
        print(f"    Recall: {rf_metrics['recall']:.4f}")
        print(f"    F1-Score: {rf_metrics['f1']:.4f}")
        print(f"    AUC: {rf_metrics['auc']:.4f}")
        
        self.models['rf_binary'] = rf_model
        self.metrics['rf_binary'] = rf_metrics
        
        # Train Gradient Boosting
        print("\n[3b] Training Gradient Boosting Classifier...")
        gb_model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        gb_model.fit(X_train, y_train)
        
        y_pred_gb = gb_model.predict(X_test)
        y_proba_gb = gb_model.predict_proba(X_test)[:, 1]
        
        gb_metrics = {
            'accuracy': accuracy_score(y_test, y_pred_gb),
            'precision': precision_score(y_test, y_pred_gb),
            'recall': recall_score(y_test, y_pred_gb),
            'f1': f1_score(y_test, y_pred_gb),
            'auc': roc_auc_score(y_test, y_proba_gb),
        }
        
        print(f"  ✓ Gradient Boosting trained")
        print(f"    Accuracy: {gb_metrics['accuracy']:.4f}")
        print(f"    Precision: {gb_metrics['precision']:.4f}")
        print(f"    Recall: {gb_metrics['recall']:.4f}")
        print(f"    F1-Score: {gb_metrics['f1']:.4f}")
        print(f"    AUC: {gb_metrics['auc']:.4f}")
        
        self.models['gb_binary'] = gb_model
        self.metrics['gb_binary'] = gb_metrics
        
        # Best model
        best_model_name = 'rf_binary' if rf_metrics['f1'] >= gb_metrics['f1'] else 'gb_binary'
        print(f"\n  ✓ Best model: {best_model_name}")
    
    def train_multiclass_classifier(self, processed_data: dict):
        """Train multi-class attack category classifier.
        
        Args:
            processed_data: Preprocessed data dictionary
        """
        print("\n" + "="*70)
        print("[STEP 4] Training Multi-class Classifier (Attack Categories)")
        print("="*70)
        
        X_train = processed_data['X_train']
        X_test = processed_data['X_test']
        y_train = processed_data['y_train_category']
        y_test = processed_data['y_test_category']
        
        if y_train is None:
            print("✗ Category labels not available in dataset")
            return
        
        print("\n[4a] Training Random Forest Multi-class Classifier...")
        rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            n_jobs=-1,
            random_state=42
        )
        rf_model.fit(X_train, y_train)
        
        y_pred = rf_model.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"  ✓ Multi-class Random Forest trained")
        print(f"    Accuracy: {accuracy:.4f}")
        print(f"\n  Classification Report:")
        print(classification_report(y_test, y_pred))
        
        multiclass_metrics = {
            'accuracy': accuracy,
            'model': rf_model
        }
        
        self.models['rf_multiclass'] = rf_model
        self.metrics['rf_multiclass'] = multiclass_metrics
    
    def train_anomaly_detector(self, processed_data: dict):
        """Train anomaly detector.
        
        Args:
            processed_data: Preprocessed data dictionary
        """
        print("\n" + "="*70)
        print("[STEP 5] Training Anomaly Detector")
        print("="*70)
        
        X_train = processed_data['X_train']
        X_test = processed_data['X_test']
        
        print("\n[5a] Training Isolation Forest...")
        anomaly_detector = AnomalyDetector(contamination=0.05)
        anomaly_detector.train(X_train)
        
        # Test on normal data
        normal_predictions = anomaly_detector.detect(X_test[:1000])
        anomalies = sum(1 for p in normal_predictions if p == -1)
        
        print(f"  ✓ Anomaly detector trained")
        print(f"    Anomalies detected in test set: {anomalies}/{len(normal_predictions)}")
        
        # Get anomaly scores
        anomaly_scores = anomaly_detector.get_anomaly_scores(X_test[:1000])
        print(f"    Mean anomaly score: {anomaly_scores.mean():.4f}")
        print(f"    Std anomaly score: {anomaly_scores.std():.4f}")
        
        self.models['anomaly_detector'] = anomaly_detector
        self.metrics['anomaly_detector'] = {
            'contamination': 0.05,
            'anomalies_detected': anomalies
        }
    
    def save_models(self):
        """Save all trained models."""
        print("\n" + "="*70)
        print("[STEP 6] Saving Models")
        print("="*70)
        
        model_dir = Path(self.model_dir)
        model_dir.mkdir(parents=True, exist_ok=True)
        
        for model_name, model in self.models.items():
            filepath = model_dir / f"{model_name}.pkl"
            with open(filepath, 'wb') as f:
                pickle.dump(model, f)
            print(f"  ✓ Saved: {filepath}")
        
        # Save processed dataset
        self.loader.save_processed_data('unsw_nb15_processed.pkl')
        print(f"  ✓ Saved processed dataset")
    
    def generate_report(self):
        """Generate training report."""
        print("\n" + "="*70)
        print("TRAINING SUMMARY")
        print("="*70)
        
        for model_name, metrics in self.metrics.items():
            print(f"\n{model_name}:")
            for metric_name, value in metrics.items():
                if isinstance(value, float):
                    print(f"  {metric_name}: {value:.4f}")
                else:
                    print(f"  {metric_name}: {value}")


def main():
    """Main training pipeline."""
    
    print("\n" + "="*70)
    print("UNSW-NB15 NETWORK INTRUSION DETECTION TRAINING")
    print("="*70)
    print("\nThis script trains ML models on the UNSW-NB15 dataset for:")
    print("  1. Binary classification (Normal vs Attack)")
    print("  2. Multi-class classification (Attack types)")
    print("  3. Anomaly detection")
    
    trainer = UNSWTrainer(dataset_dir='./datasets', model_dir='./models')
    
    # Load and preprocess
    processed_data = trainer.load_and_preprocess(filename='UNSW-NB15_1.csv')
    
    if processed_data is None:
        print("\n✗ Failed to load dataset. Please ensure UNSW-NB15 CSV files are in ./datasets/")
        return
    
    # Train models
    trainer.train_binary_classifier(processed_data)
    trainer.train_multiclass_classifier(processed_data)
    trainer.train_anomaly_detector(processed_data)
    
    # Save models
    trainer.save_models()
    
    # Generate report
    trainer.generate_report()
    
    print("\n" + "="*70)
    print("TRAINING COMPLETE")
    print("="*70)
    print("\nNext steps:")
    print("1. Use trained models with: python examples/unsw_detection_example.py")
    print("2. Integrate models into monitoring: from network_monitoring import UNSWDetector")
    print("3. Real-time detection on network traffic")


if __name__ == '__main__':
    main()
