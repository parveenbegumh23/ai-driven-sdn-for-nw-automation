# UNSW-NB15 Dataset Integration Guide

## Overview
This guide explains how to use the UNSW-NB15 network intrusion dataset with the AI-driven SDN project.

## What is UNSW-NB15?

**UNSW-NB15** is a comprehensive benchmark dataset for network intrusion detection systems, developed by the Cyber Security Lab at UNSW Sydney.

### Dataset Characteristics:
- **45 features** per network flow
- **2.5 million** labeled records
- **10 attack categories** + Normal traffic
- Real network traffic patterns
- Balanced class distribution

### Attack Categories:
1. **Normal** - Legitimate traffic
2. **Generic** - Attacks without specific target
3. **Exploits** - Exploitation of vulnerabilities
4. **Fuzzers** - Fuzzing attacks
5. **DoS** - Denial of Service attacks
6. **Reconnaissance** - Network scanning/probing
7. **Analysis** - Web app attacks
8. **Backdoor** - Backdoor access attempts
9. **Shellcode** - Shellcode injection
10. **Worms** - Self-propagating malware

## Dataset Download

### Step 1: Download the Dataset

Visit: https://www.unsw.adfa.edu.au/unsw-canberra-cyber/cybersecurity-datasets/

Download the CSV files:
- `UNSW-NB15_1.csv` (1 of 4 files)
- `UNSW-NB15_2.csv`
- `UNSW-NB15_3.csv`
- `UNSW-NB15_4.csv`

Or use a single combined file if available.

### Step 2: Place Files in Dataset Directory

```bash
# Create datasets directory
mkdir -p datasets

# Copy downloaded CSV files
cp UNSW-NB15_*.csv datasets/
```

Your directory structure should look like:
```
ai-driven-sdn-for-nw-automation/
├── datasets/
│   ├── UNSW-NB15_1.csv
│   ├── UNSW-NB15_2.csv
│   ├── UNSW-NB15_3.csv
│   └── UNSW-NB15_4.csv
├── models/
├── network_monitoring/
└── ...
```

## Usage Instructions

### 1. Load and Explore Dataset

```python
from network_monitoring.unsw_dataset_loader import UNSWDatasetLoader

# Initialize loader
loader = UNSWDatasetLoader(dataset_dir='./datasets')

# Load dataset
df = loader.load_dataset('UNSW-NB15_1.csv')

# Get statistics
stats = loader.get_statistics()
print(f"Total samples: {stats['total_samples']}")
print(f"Attack categories: {stats['attack_categories']}")
```

### 2. Preprocess Dataset

```python
# Preprocess data
processed_data = loader.preprocess(
    drop_columns=['srcip', 'dstip', 'Stime', 'Ltime'],
    test_split=0.2
)

print(f"Training samples: {processed_data['num_train']}")
print(f"Testing samples: {processed_data['num_test']}")
print(f"Features: {processed_data['num_features']}")
```

### 3. Train Models

```bash
# Run the training script
python train_unsw_model.py
```

This will:
1. Load UNSW-NB15 dataset
2. Preprocess and normalize features
3. Train binary classifier (Normal vs Attack)
4. Train multi-class classifier (10 attack types)
5. Train anomaly detector
6. Save models to `./models/`

**Output:**
```
[STEP 1] Loading UNSW-NB15 Dataset
[STEP 2] Preprocessing Dataset
[STEP 3] Training Binary Classifier
[STEP 4] Training Multi-class Classifier
[STEP 5] Training Anomaly Detector
[STEP 6] Saving Models

Models saved:
  - rf_binary.pkl (Random Forest)
  - gb_binary.pkl (Gradient Boosting)
  - rf_multiclass.pkl (Attack classification)
  - anomaly_detector.pkl (Isolation Forest)
```

### 4. Run Real-Time Detection

```bash
# Run real-time intrusion detection
python examples/unsw_detection_example.py
```

**Features:**
- Binary classification (Attack/Normal)
- Attack type identification
- Anomaly scoring
- Real-time alerting
- Live metrics display

### 5. Integrate with Network Monitoring

```python
from network_monitoring import ContinuousNetworkMonitor
from examples.unsw_detection_example import UNSWDetector
import numpy as np

# Initialize detector
detector = UNSWDetector()

# Initialize monitor
monitor = ContinuousNetworkMonitor()

# Create detection callback
def on_metrics(metrics):
    # Prepare features
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
    
    # Detect intrusion
    result = detector.detect_intrusion(features)
    
    if result['is_attack']:
        print(f"⚠️ ATTACK DETECTED: {result['attack_type']}")
        print(f"Confidence: {result['confidence']:.2%}")

# Add callback and start monitoring
monitor.add_callback(on_metrics)
monitor.start()
```

## Dataset Features Mapping

### Network Flow Features (UNSW-NB15 → Monitoring)

| UNSW-NB15 Feature | Monitoring Metric | Usage |
|---|---|---|
| srcip, dstip | source/dest IP | Flow identification (dropped in preprocessing) |
| sport, dsport | source/dest port | Port analysis |
| proto | protocol | Protocol classification |
| state | connection state | Connection status |
| dur | duration | Session duration |
| sbytes, dbytes | network_sent, network_recv | Data volume |
| sttl, dttl | TTL values | Routing analysis |
| packet_loss | packet_loss | Network quality |
| latency | latency | Response time |
| signal_strength | signal_strength | Wireless signal |
| active_connections | active_connections | Connection count |

## Model Performance (Expected)

### Binary Classification (Normal vs Attack)
- **Accuracy**: ~98%
- **Precision**: ~97%
- **Recall**: ~98%
- **AUC**: ~0.99

### Multi-class Classification (Attack Types)
- **Accuracy**: ~95%

### Anomaly Detection
- **Detection Rate**: ~92% of novel attacks

## Troubleshooting

### Issue: "Dataset not found"
```bash
# Verify files are in correct location
ls -la datasets/UNSW-NB15*.csv

# Check file permissions
chmod 644 datasets/UNSW-NB15*.csv
```

### Issue: "Out of memory"
- Process one file at a time
- Reduce dataset size:
  ```python
  df = loader.load_dataset()
  df_sample = df.sample(frac=0.5)  # 50% sample
  ```

### Issue: "Feature mismatch"
- Ensure consistent feature extraction
- Use processed data with scaler:
  ```python
  processed_data = loader.load_processed_data('unsw_nb15_processed.pkl')
  ```

## Advanced Usage

### Custom Feature Selection

```python
# Select specific features
feature_cols = [
    'cpu_percent', 'memory_percent', 'network_sent', 
    'network_recv', 'latency', 'packet_loss'
]

X_train, y_train = loader.get_features_labels(
    df_train, 
    feature_cols=feature_cols
)
```

### Model Evaluation

```python
from sklearn.metrics import classification_report

# Get predictions
y_pred = model.predict(X_test)

# Print report
print(classification_report(y_test, y_pred))
```

### Feature Importance Analysis

```python
import pandas as pd

# Get feature importances
importances = model.feature_importances_
feature_importance_df = pd.DataFrame({
    'feature': processed_data['feature_names'],
    'importance': importances
}).sort_values('importance', ascending=False)

print(feature_importance_df.head(10))
```

## References

- **Dataset Paper**: https://www.unsw.adfa.edu.au/unsw-canberra-cyber/cybersecurity-datasets/unsw-nb15-dataset/
- **Dataset Download**: https://www.unsw.adfa.edu.au/unsw-canberra-cyber/cybersecurity-datasets/
- **Paper Citation**: Moustafa, N., & Slay, J. (2015). UNSW-NB15: a comprehensive data set for network intrusion detection systems. IEEE Access, 3, 1040-1055.

## Next Steps

1. ✅ Download UNSW-NB15 dataset
2. ✅ Place CSV files in `datasets/`
3. ✅ Run `python train_unsw_model.py`
4. ✅ Run `python examples/unsw_detection_example.py`
5. ✅ Integrate into your network monitoring pipeline
6. ✅ Deploy for real-time intrusion detection

---

**Last Updated**: June 2026
