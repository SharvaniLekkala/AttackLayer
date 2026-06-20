import numpy as np
from sklearn.ensemble import IsolationForest

def detect_outliers(X: np.ndarray, contamination: float = 0.05, random_state: int = 42) -> np.ndarray:
    """
    Detect outliers in the embeddings using Isolation Forest.
    Returns a boolean mask where True means clean sample and False means outlier.
    """
    print(f"Running outlier detection on {X.shape[0]} samples with contamination={contamination}...")
    # Initialize Isolation Forest
    iso_forest = IsolationForest(
        contamination=contamination, 
        random_state=random_state, 
        n_jobs=-1
    )
    
    # Fit and predict. 1 for inliers, -1 for outliers.
    preds = iso_forest.fit_predict(X)
    
    clean_mask = (preds == 1)
    num_outliers = np.sum(preds == -1)
    print(f"Outlier detection complete. Found {num_outliers} outliers.")
    
    return clean_mask

def filter_outliers(X: np.ndarray, y: np.ndarray = None, contamination: float = 0.05) -> tuple:
    """
    Filter out outliers from embeddings and optionally labels.
    Returns: (X_clean, y_clean) or just X_clean.
    """
    mask = detect_outliers(X, contamination=contamination)
    X_clean = X[mask]
    
    if y is not None:
        y_clean = y[mask]
        return X_clean, y_clean
        
    return X_clean, None

if __name__ == "__main__":
    # Test IsolationForest with dummy embeddings
    dummy_inliers = np.random.normal(loc=0.0, scale=0.5, size=(100, 768))
    dummy_outliers = np.random.normal(loc=5.0, scale=1.0, size=(5, 768))
    X_test = np.vstack([dummy_inliers, dummy_outliers])
    
    mask = detect_outliers(X_test, contamination=0.05)
    # Check if outliers were flagged
    assert np.sum(~mask) == 6 or np.sum(~mask) == 5, f"Unexpected number of outliers detected: {np.sum(~mask)}"
    print("Outlier detector test passed successfully!")
