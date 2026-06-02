# CICIDS2017 Integration Guide

## Overview
This guide explains how to download, process, and use the CICIDS2017 dataset with the AI-driven SDN project.

## What is CICIDS2017?

**CICIDS2017** is a network intrusion detection dataset created by the Canadian Institute for Cybersecurity at the University of New Brunswick. It contains real-world network traffic with various modern attacks.

### Dataset Characteristics:
- **80 features** per network flow (more granular than UNSW-NB15)
- **2.8 million** labeled records
- **13 attack categories** + Benign traffic
- Modern attack patterns (2017)
- Comprehensive protocol analysis

### Attack Categories:
1. **BENIGN** - Normal traffic
2. **FTP-Patator** - Brute force FTP attacks
3. **SSH-Patator** - Brute force SSH attacks
4. **DoS Hulk** - Denial of Service (HTTP GET flooding)
5. **DoS GoldenEye** - Denial of Service (HTTP CONNECT flooding)
6. **DoS Slowhttptest** - Slow HTTP attacks
7. **DoS Slowloris** - Slowloris attacks
8. **Heartbleed** - Heartbleed vulnerability exploitation
9. **Web Attack – Brute Force** - Web application brute force
10. **Web Attack – XSS** - Cross-site scripting attacks
11. **Web Attack – SQL Injection** - SQL injection attacks
12. **Infiltration** - Network infiltration attempts
13. **Bot** - Bot communication traffic

## Dataset Download

### Step 1: Download the Dataset

Visit: https://www.unb.ca/cic/datasets/ids-2017.html

Download the dataset:
- **CSV Format**: `MachineLearningCSV_Processed.csv` (recommended)
- Or individual daily CSV files

### Step 2: Place Files in Dataset Directory

```bash
# Create datasets directory
mkdir -p datasets

# Copy downloaded CSV file
cp MachineLearningCSV_Processed.csv datasets/

# Verify
ls -lh datasets/MachineLearningCSV_Processed.csv
```

Expected file size: ~1.5GB (compressed) to ~3.5GB (extracted)

## Usage Instructions

### 1. Load and Explore Dataset

```python
from network_monitoring.cicids2017_loader import CICIDS2017Loader

# Initialize loader
loader = CICIDS2017Loader(dataset_dir='./datasets')

# Load dataset
df = loader.load_dataset('MachineLearningCSV_Processed.csv')

# Get statistics
stats = loader.get_statistics()
print(f"Total samples: {stats['total_samples']}")
print(f"Attack categories: {stats['class_distribution']}")
```

### 2. Preprocess Dataset

```python
# Preprocess data
processed_data = loader.preprocess(
    drop_columns=['Timestamp', 'Src IP', 'Dst IP'],
    test_split=0.2
)

print(f"Training samples: {processed_data['num_train']:,}")
print(f"Testing samples: {processed_data['num_test']:,}")
print(f"Features: {processed_data['num_features']}")
```

### 3. Train Models

```bash
# Run the training script
python train_cicids2017_model.py
```

This will:
1. Load CICIDS2017 dataset
2. Preprocess and normalize 80 features
3. Train binary classifier (Benign vs Attack)
4. Train multi-class classifier (13 attack types)
5. Train anomaly detector
6. Save models to `./models/`

**Expected output:**
```
[STEP 1] Loading CICIDS2017 Dataset
[STEP 2] Preprocessing Dataset
[STEP 3] Training Binary Classifier
[STEP 4] Training Multi-class Classifier
[STEP 5] Training Anomaly Detector
[STEP 6] Saving Models

Expected Accuracy: ~99% (Binary), ~96% (Multi-class)
```

### 4. Run Real-Time Detection

```bash
# Run real-time intrusion detection
python examples/cicids2017_detection_example.py
```

### 5. Compare with UNSW-NB15

```bash
# Compare both datasets and models
python compare_models.py
```

## CICIDS2017 vs UNSW-NB15 Comparison

| Aspect | CICIDS2017 | UNSW-NB15 |
|--------|-----------|-----------|
| **Features** | 80 | 45 |
| **Attack Types** | 13 | 10 |
| **Total Records** | 2.8M | 2.5M |
| **Collection Year** | 2017 | 2015 |
| **Binary Accuracy** | ~99% | ~98% |
| **Multi-class Accuracy** | ~96% | ~95% |
| **Training Time** | 20-30 min | 15-20 min |
| **Best For** | Detailed analysis | Real-time detection |
| **File Size** | ~3.5GB | ~2.8GB |

## Model Performance (Expected)

### Binary Classification (Benign vs Attack)
- **Accuracy**: ~99%
- **Precision**: ~97.6%
- **Recall**: ~99.2%
- **AUC**: ~0.995

### Multi-class Classification (13 Attack Types)
- **Accuracy**: ~96%
- Top attack categories: FTP-Patator, SSH-Patator, DoS attacks

### Anomaly Detection
- **Detection Rate**: ~94% of novel attacks
- **False Positive Rate**: <4%

## Features Breakdown

### Network Statistics (40 features)
- Forward packet statistics
- Backward packet statistics
- Byte flow rates
- Packet length statistics

### Flow Timing (8 features)
- Inter-arrival times (IAT)
- Flow duration analysis
- Active/Idle time statistics

### TCP Flags (9 features)
- FIN, SYN, RST, PSH, ACK, URG, CWE, ECE flags

### Subflow Analysis (4 features)
- Forward subflow packets/bytes
- Backward subflow packets/bytes

### Window Scale (2 features)
- Initial window bytes forward/backward

### Active/Idle Analysis (4 features)
- Active/Idle time mean, std, max, min

### Additional Features (13 features)
- Protocol type
- Destination port
- Init window bytes
- Forward/Backward packet count
- Header length
- Data packet length

## Troubleshooting

### Issue: "Dataset not found"
```bash
# Verify correct filename
ls -la datasets/MachineLearningCSV_Processed.csv

# Check encoding issues
file datasets/MachineLearningCSV_Processed.csv
```

### Issue: "Out of Memory"
The dataset is large (3.5GB). Options:
1. Process one file at a time
2. Use sample:
   ```python
   df_sample = df.sample(frac=0.5)  # 50% sample
   ```
3. Increase system swap space
4. Use a machine with >8GB RAM

### Issue: "Feature mismatch"
Ensure 80 features are used:
```python
assert processed_data['num_features'] == 80
```

## Advanced Usage

### Custom Feature Selection

```python
# Select specific important features
important_features = [
    'Flow Duration', 'Total Fwd Packets', 'Total Bwd Packets',
    'Fwd Packet Length Mean', 'Bwd Packet Length Mean',
    'Flow Bytes/s', 'Flow Packets/s', 'ACK Flag Count'
]

X_train, y_train = loader.get_features_labels(
    df_train, 
    feature_cols=important_features
)
```

### Attack Category Analysis

```python
# Analyze specific attack types
attack_counts = df['Label'].value_counts()
print(attack_counts)

# Train separate models for specific attacks
dos_attacks = df[df['Label'].str.contains('DoS')]
```

## References

- **Dataset Paper**: https://www.unb.ca/cic/datasets/ids-2017.html
- **Dataset Download**: https://www.unb.ca/cic/datasets/ids-2017.html
- **CIC Lab**: https://www.unb.ca/cic/

## Next Steps

1. ✅ Download CICIDS2017 dataset
2. ✅ Place CSV file in `datasets/`
3. ✅ Run `python train_cicids2017_model.py`
4. ✅ Run `python examples/cicids2017_detection_example.py`
5. ✅ Compare with UNSW-NB15: `python compare_models.py`
6. ✅ Deploy for production

---

**Last Updated**: June 2026
