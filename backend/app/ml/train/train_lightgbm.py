import os
import joblib
from lightgbm import LGBMClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.calibration import CalibratedClassifierCV
from app.ml.utils import load_split_data

def main():
    print("--- Training LightGBM ---")
    X_train, X_val, X_test, y_train, y_val, y_test = load_split_data()
    
    param_grid = {
        'num_leaves': [15, 31, 63],
        'learning_rate': [0.01, 0.05, 0.1, 0.2]
    }
    
    print("Performing grid search...")
    # Use CPU explicitly
    grid = GridSearchCV(
        LGBMClassifier(
            class_weight='balanced', 
            random_state=42, 
            n_jobs=-1, 
            verbose=-1, 
            device='cpu'
        ), 
        param_grid, 
        cv=5, 
        scoring='f1'
    )
    grid.fit(X_train, y_train)
    
    best_lgb = grid.best_estimator_
    print(f"Best parameters found: {grid.best_params_}")
    
    print("Calibrating classifier...")
    model = CalibratedClassifierCV(estimator=best_lgb, cv=5)
    model.fit(X_train, y_train)
    
    models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, "lightgbm.pkl")
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    main()
