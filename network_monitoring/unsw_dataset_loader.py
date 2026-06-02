"""UNSW-NB15 Dataset Loader and Preprocessor."""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import pickle

logger = logging.getLogger(__name__)


class UNSWDatasetLoader:
    """Load and preprocess UNSW-NB15 network intrusion dataset."""
    
    # UNSW-NB15 features
    FEATURE_NAMES = [
        'srcip', 'sport', 'dstip', 'dsport', 'proto', 'state', 'dur',
        'sbytes', 'dbytes', 'sttl', 'dttl', 'sloss', 'dloss', 'service',
        'Sload', 'Dload', 'Spkts', 'Dpkts', 'swin', 'dwin', 'stcpb', 'dtcpb',
        'smeansz', 'dmeansz', 'trans_depth', 'res_bdy_len', 'Sjit', 'Djit',
        'Stime', 'Ltime', 'Sintpkt', 'Dintpkt', 'tcprtt', 'synack', 'ackdat',
        'is_sm_ips_ports', 'ct_state_ttl', 'ct_flw_http_mthd', 'is_ftp_login',
        'ct_ftp_cmd', 'ct_srv_src', 'ct_srv_dst', 'ct_dst_ltm', 'ct_src_ltm',
        'ct_src_dport_ltm', 'ct_dst_sport_ltm', 'ct_dst_src_ltm', 'attack_cat', 'Label'
    ]
    
    ATTACK_CATEGORIES = {
        'Normal': 0,
        'Generic': 1,
        'Exploits': 2,
        'Fuzzers': 3,
        'DoS': 4,
        'Reconnaissance': 5,
        'Analysis': 6,
        'Backdoor': 7,
        'Shellcode': 8,
        'Worms': 9
    }
    
    def __init__(self, dataset_dir: str = './datasets'):
        """Initialize UNSW-NB15 loader.
        
        Args:
            dataset_dir: Directory containing UNSW-NB15 dataset files
        """
        self.dataset_dir = Path(dataset_dir)
        self.dataset_dir.mkdir(parents=True, exist_ok=True)
        
        self.data = None
        self.processed_data = None
        self.feature_scaler = None
        self.label_encoder = None
        self.metadata = {}
    
    def load_dataset(self, filename: str = 'UNSW-NB15_1.csv') -> pd.DataFrame:
        """Load UNSW-NB15 dataset from CSV.
        
        Args:
            filename: CSV filename in dataset directory
            
        Returns:
            Loaded DataFrame
        """
        filepath = self.dataset_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(
                f"Dataset not found: {filepath}\n"
                f"Please download UNSW-NB15 from: "
                f"https://www.unsw.adfa.edu.au/unsw-canberra-cyber/cybersecurity-datasets/"
            )
        
        logger.info(f"Loading UNSW-NB15 dataset from {filepath}...")
        self.data = pd.read_csv(filepath)
        
        logger.info(f"Dataset loaded: {len(self.data)} rows, {len(self.data.columns)} columns")
        self._log_dataset_info()
        
        return self.data
    
    def _log_dataset_info(self) -> None:
        """Log dataset information."""
        if self.data is None:
            return
        
        logger.info(f"Dataset shape: {self.data.shape}")
        logger.info(f"Missing values: {self.data.isnull().sum().sum()}")
        
        if 'Label' in self.data.columns:
            logger.info(f"Class distribution:\n{self.data['Label'].value_counts()}")
        
        if 'attack_cat' in self.data.columns:
            logger.info(f"Attack categories:\n{self.data['attack_cat'].value_counts()}")
    
    def preprocess(
        self,
        drop_columns: Optional[List[str]] = None,
        test_split: float = 0.2,
        random_state: int = 42
    ) -> Dict:
        """Preprocess UNSW-NB15 dataset.
        
        Args:
            drop_columns: Columns to drop (IPs, timestamps, etc.)
            test_split: Test set proportion
            random_state: Random seed
            
        Returns:
            Dictionary with processed data
        """
        if self.data is None:
            raise ValueError("No dataset loaded. Call load_dataset() first.")
        
        logger.info("Starting preprocessing...")
        
        df = self.data.copy()
        
        # Default columns to drop
        if drop_columns is None:
            drop_columns = ['srcip', 'dstip', 'Stime', 'Ltime']
        
        # Drop unnecessary columns
        for col in drop_columns:
            if col in df.columns:
                df = df.drop(col, axis=1)
                logger.info(f"Dropped column: {col}")
        
        # Handle missing values
        df = df.fillna(0)
        logger.info(f"Handled missing values")
        
        # Convert categorical columns to numeric
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        logger.info(f"Categorical columns: {categorical_cols}")
        
        for col in categorical_cols:
            if col in df.columns:
                # Use label encoding for categorical features
                unique_vals = df[col].unique()
                mapping = {val: idx for idx, val in enumerate(unique_vals)}
                df[col] = df[col].map(mapping)
                logger.info(f"Encoded {col}: {len(mapping)} unique values")
        
        # Separate features and labels
        X = df.drop(['Label', 'attack_cat'], axis=1, errors='ignore')
        y_binary = df['Label'] if 'Label' in df.columns else None
        y_category = df['attack_cat'] if 'attack_cat' in df.columns else None
        
        logger.info(f"Features shape: {X.shape}")
        
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
        
        min_vals = X_array.min(axis=0)
        max_vals = X_array.max(axis=0)
        
        # Avoid division by zero
        range_vals = max_vals - min_vals
        range_vals[range_vals == 0] = 1
        
        X_normalized = (X_array - min_vals) / range_vals
        
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
        
        return (X_array - min_vals) / range_vals
    
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
        
        if 'Label' in self.data.columns:
            stats['binary_classes'] = {
                'Normal': int((self.data['Label'] == 0).sum()),
                'Attack': int((self.data['Label'] == 1).sum())
            }
        
        if 'attack_cat' in self.data.columns:
            stats['attack_categories'] = self.data['attack_cat'].value_counts().to_dict()
        
        return stats
    
    def save_processed_data(self, filename: str = 'unsw_processed.pkl') -> str:
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
    
    def load_processed_data(self, filename: str = 'unsw_processed.pkl') -> Dict:
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
