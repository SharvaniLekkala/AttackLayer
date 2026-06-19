import os
import numpy as np
from sklearn.model_selection import train_test_split

def load_split_data(random_state=42):
    """
    Loads data/embeddings.npy and data/labels.npy, and splits them
    consistently into Train (70%), Val (15%), and Test (15%) splits
    using stratified splitting.
    """
    # Try to find data directory
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(base_dir, "data")
    
    emb_path = os.path.join(data_dir, "embeddings.npy")
    lbl_path = os.path.join(data_dir, "labels.npy")
    
    if not os.path.exists(emb_path) or not os.path.exists(lbl_path):
        raise FileNotFoundError(f"Embeddings or labels not found at {data_dir}")
        
    X = np.load(emb_path)
    y = np.load(lbl_path)
    
    # 70% train, 30% temp (which will be split 50/50 for val/test)
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, random_state=random_state, stratify=y
    )
    
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, random_state=random_state, stratify=y_temp
    )
    
    return X_train, X_val, X_test, y_train, y_val, y_test
