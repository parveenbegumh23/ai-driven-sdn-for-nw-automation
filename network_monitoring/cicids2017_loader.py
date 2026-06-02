"""CICIDS2017 Dataset Loader and Preprocessor."""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import pickle

logger = logging.getLogger(__name__)


class CICIDS2017Loader:
    """Load and preprocess CICIDS2017 network intrusion dataset."""
    
    # CICIDS2017 features (80 features)
    FEATURE_NAMES = [
        'Dst Port', 'Protocol', 'Timestamp', 'Flow Duration', 'Total Fwd Packets',
        'Total Backward Packets', 'Total Length of Fwd Packets', 'Total Length of Bwd Packets',
        'Fwd Packet Length Max', 'Fwd Packet Length Min', 'Fwd Packet Length Mean',
        'Fwd Packet Length Std', 'Bwd Packet Length Max', 'Bwd Packet Length Min',
        'Bwd Packet Length Mean', 'Bwd Packet Length Std', 'Flow Bytes/s', 'Flow Packets/s',
        'Flow IAT Mean', 'Flow IAT Std', 'Flow IAT Max', 'Flow IAT Min',
        'Fwd IAT Total', 'Fwd IAT Mean', 'Fwd IAT Std', 'Fwd IAT Max', 'Fwd IAT Min',
        'Bwd IAT Total', 'Bwd IAT Mean', 'Bwd IAT Std', 'Bwd IAT Max', 'Bwd IAT Min',
        'Fwd PSH Flags', 'Bwd PSH Flags', 'Fwd URG Flags', 'Bwd URG Flags',
        'Fwd Header Length', 'Bwd Header Length', 'Fwd Packets/s', 'Bwd Packets/s',
        'Min Packet Length', 'Max Packet Length', 'Packet Length Mean', 'Packet Length Std',
        'Packet Length Variance', 'FIN Flag Count', 'SYN Flag Count', 'RST Flag Count',
        'PSH Flag Count', 'ACK Flag Count', 'URG Flag Count', 'CWE Flag Count',
        'ECE Flag Count', 'Down/Up Ratio', 'Average Packet Size', 'Avg Fwd Segment Size',
        'Avg Bwd Segment Size', 'Fwd Header Length.1', 'Fwd Avg Bytes/Bulk', 'Fwd Avg Packets/Bulk',
        'Fwd Avg Bulk Rate', 'Bwd Avg Bytes/Bulk', 'Bwd Avg Packets/Bulk', 'Bwd Avg Bulk Rate',
        'Subflow Fwd Packets', 'Subflow Fwd Bytes', 'Subflow Bwd Packets', 'Subflow Bwd Bytes',
        'Init Win bytes Fwd', 'Init Win bytes Bwd', 'Fwd Act Data Pkts', 'Fwd Seg Size Min',
        'Active Mean', 'Active Std', 'Active Max', 'Active Min', 'Idle Mean', 'Idle Std',
        'Idle Max', 'Idle Min', 'Label'
    ]
    
    ATTACK_CATEGORIES = {
        'BENIGN': 0,
        'FTP-Patator': 1,
        'SSH-Patator': 2,
        'DoS Hulk': 3,
        'DoS GoldenEye': 4,
        'DoS Slowhttptest': 5,
        'DoS Slowloris': 6,
        'Heartbleed': 7,
        'Web Attack – Brute Force': 8,
        'Web Attack – XSS': 9,
        'Web Attack – SQL Injection': 10,
        'Infiltration': 11,
        'Bot': 12
    }
    
    def __init__(self, dataset_dir: str = './datasets'):
        """Initialize CICIDS2017 loader.
        
        Args:
            dataset_dir: Directory containing CICIDS2017 dataset files
        """
        self.dataset_dir = Path(dataset_dir)
        self.dataset_dir.mkdir(parents=True, exist_ok=True)
        
        self.data = None
        self.processed_data = None
        self.feature_scaler = None
        self.label_encoder = None
        self.metadata = {}
    
    def load_dataset(self, filename: str = 'MachineLearningCSV_Processed.csv') -> pd.DataFrame:
        """Load CICIDS2017 dataset from CSV.
        
        Args:
            filename: CSV filename in dataset directory
            
        Returns:
            Loaded DataFrame
        """
        filepath = self.dataset_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(
                f"Dataset not found: {filepath}\n"
                f"Please download CICIDS2017 from: "
                f"https://www.unb.ca/cic/datasets/ids-2017.html"
            )
        
        logger.info(f"Loading CICIDS2017 dataset from {filepath}...")
        
        # Try different encoding options
        try:
            self.data = pd.read_csv(filepath)
        except UnicodeDecodeError:
            self.data = pd.read_csv(filepath, encoding='latin-1')
        
        logger.info(f"Dataset loaded: {len(self.data)} rows, {len(self.data.columns)} columns")
        self._log_dataset_info()
        
        return self.data
    
    def _log_dataset_info(self) -> None:
        """Log dataset information."""
        if self.data is None:
            return
        
        logger.info(f"Dataset shape: {self.data.shape}")
        logger.info(f"Missing values: {self.data.isnull().sum().sum()}")
        
        # Look for label column
        label_cols = [col for col in self.data.columns if 'label' in col.lower()]
        if label_cols:
            label_col = label_cols[0]
            logger.info(f"Attack label distribution:\n{self.data[label_col].value_counts()}")
    
    def preprocess(
        self,
        drop_columns: Optional[List[str]] = None,
        test_split: float = 0.2,
        random_state: int = 42
    ) -> Dict:
        """Preprocess CICIDS2017 dataset.
        
        Args:
            drop_columns: Columns to drop
            test_split: Test set proportion
            random_state: Random seed
            
        Returns:
            Dictionary with processed data
        """
        if self.data is None:
            raise ValueError("No dataset loaded. Call load_dataset() first.")
        
        logger.info("Starting preprocessing...")
        
        df = self.data.copy()
        
        # Default columns to drop (timestamps, IPs, non-numeric)
        if drop_columns is None:
            drop_columns = ['Timestamp', 'Src IP', 'Dst IP']
        
        # Drop unnecessary columns
        for col in drop_columns:
            if col in df.columns:
                df = df.drop(col, axis=1)
                logger.info(f"Dropped column: {col}")
        
        # Find label column
        label_cols = [col for col in df.columns if 'label' in col.lower()]
        label_col = label_cols[0] if label_cols else None
        
        # Handle missing values
        df = df.fillna(0)
        
        # Remove infinite values
        df = df.replace([np.inf, -np.inf], 0)
        
        logger.info(f"Handled missing values")
        
        # Convert categorical columns to numeric
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        if label_col:
            categorical_cols = [c for c in categorical_cols if c != label_col]
        
        logger.info(f"Categorical columns: {categorical_cols}")
        
        for col in categorical_cols:
            if col in df.columns:
                unique_vals = df[col].unique()
                mapping = {val: idx for idx, val in enumerate(unique_vals)}
                df[col] = df[col].map(mapping)
                logger.info(f"Encoded {col}: {len(mapping)} unique values")
        
        # Separate features and labels
        if label_col:
            X = df.drop(label_col, axis=1)
            y = df[label_col]
        else:
            X = df
            y = None
        
        logger.info(f"Features shape: {X.shape}")
        
        # Create binary label (0=benign, 1=attack)
        if y is not None:
            y_binary = (y != 'BENIGN').astype(int) if isinstance(y.iloc[0], str) else (y != 0).astype(int)
            
            # Create category labels
            y_category = y.copy()
            if isinstance(y_category.iloc[0], str):
                y_category = y_category.map(self.ATTACK_CATEGORIES)
                y_category = y_category.fillna(0).astype(int)
        else:
            y_binary = None
            y_category = None
        
        # Split data
        split_idx = int(len(df) * (1 - test_split))
        X_train = X[:split_idx]
        X_test = X[split_idx:]
        
        if y_binary is not None:
            y_train_binary = y_binary[:split_idx]
            y_test_binary = y_binary[split_idx:]
        else:
            y_train_binary = y_test_binary = None
        
        if y_category is not None:
            y_train_category = y_category[:split_idx]
            y_test_category = y_category[split_idx:]
        else:
            y_train_category = y_test_category = None
        
        logger.info(f"Train set: {len(X_train)} samples")
        logger.info(f"Test set: {len(X_test)} samples")
        
        # Normalize features
        X_train_normalized, scaler_params = self._normalize_features(X_train)
        X_test_normalized = self._apply_normalization(X_test, scaler_params)
        
        self.processed_data = {
            'X_train': X_train_normalized,
            'X_test': X_test_normalized,
            'y_train_binary': y_train_binary,
            'y_test_binary': y_test_binary,
            'y_train_category': y_train_category,
            'y_test_category': y_test_category,
            'feature_names': X.columns.tolist(),
            'scaler_params': scaler_params,
            'num_train': len(X_train),
            'num_test': len(X_test),
            'num_features': len(X.columns)
        }
        
        logger.info("Preprocessing complete")
        return self.processed_data
    
    def _normalize_features(
        self,
        X: pd.DataFrame
    ) -> Tuple[np.ndarray, Dict]:
        """Normalize features using min-max scaling.
        
        Args:
            X: Feature DataFrame
            
        Returns:
            Tuple of (normalized_array, scaling_params)
        """
        X_array = X.values.astype(float)
        
        min_vals = np.nanmin(X_array, axis=0)
        max_vals = np.nanmax(X_array, axis=0)
        
        # Avoid division by zero
        range_vals = max_vals - min_vals
        range_vals[range_vals == 0] = 1
        
        X_normalized = (X_array - min_vals) / range_vals
        X_normalized = np.nan_to_num(X_normalized, nan=0.0, posinf=0.0, neginf=0.0)
        
        params = {
            'min': min_vals.tolist(),
            'max': max_vals.tolist(),
            'range': range_vals.tolist()
        }
        
        return X_normalized, params
    
    def _apply_normalization(
        self,
        X: pd.DataFrame,
        scaler_params: Dict
    ) -> np.ndarray:
        """Apply pre-computed normalization.
        
        Args:
            X: Feature DataFrame
            scaler_params: Scaling parameters
            
        Returns:
            Normalized array
        """
        X_array = X.values.astype(float)
        
        min_vals = np.array(scaler_params['min'])
        range_vals = np.array(scaler_params['range'])
        
        result = (X_array - min_vals) / range_vals
        return np.nan_to_num(result, nan=0.0, posinf=0.0, neginf=0.0)
    
    def get_statistics(self) -> Dict:
        """Get dataset statistics.
        
        Returns:
            Dictionary with statistics
        """
        if self.data is None:
            return {}
        
        stats = {
            'total_samples': len(self.data),
            'total_features': len(self.data.columns),
            'feature_columns': self.data.columns.tolist()
        }
        
        label_cols = [col for col in self.data.columns if 'label' in col.lower()]
        if label_cols:
            label_col = label_cols[0]
            stats['class_distribution'] = self.data[label_col].value_counts().to_dict()
        
        return stats
    
    def save_processed_data(self, filename: str = 'cicids2017_processed.pkl') -> str:
        """Save processed data.
        
        Args:
            filename: Output filename
            
        Returns:
            Path to saved file
        """
        if self.processed_data is None:
            raise ValueError("No processed data. Call preprocess() first.")
        
        filepath = self.dataset_dir / filename
        
        with open(filepath, 'wb') as f:
            pickle.dump(self.processed_data, f)
        
        logger.info(f"Processed data saved to {filepath}")
        return str(filepath)
    
    def load_processed_data(self, filename: str = 'cicids2017_processed.pkl') -> Dict:
        """Load processed data.
        
        Args:
            filename: Input filename
            
        Returns:
            Processed data dictionary
        """
        filepath = self.dataset_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Processed data not found: {filepath}")
        
        with open(filepath, 'rb') as f:
            self.processed_data = pickle.load(f)
        
        logger.info(f"Processed data loaded from {filepath}")
        return self.processed_data
