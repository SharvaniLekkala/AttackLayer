import os
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.calibration import CalibratedClassifierCV
from app.ml.utils import load_split_data

def main():
    print("--- Training XGBoost ---")
    X_train, X_val, X_test, y_train, y_val, y_test = load_split_data()
    
    # Calculate scale_pos_weight for class imbalance
    num_neg = (y_train == 0).sum()
    num_pos = (y_train == 1).sum()
    scale_pos_weight = num_neg / num_pos
    
    param_grid = {
        'learning_rate': [0.01, 0.1, 0.2],
        'max_depth': [3, 6, 10],
        'n_estimators': [50, 100, 200]
    }
    
    print("Performing grid search...")
    # Use CPU explicitly
    grid = GridSearchCV(XGBClassifier(scale_pos_weight=scale_pos_weight, random_state=42, n_jobs=-1, tree_method='hist', device='cpu'), param_grid, cv=5, scoring='f1')
    grid.fit(X_train, y_train)
    
    best_xgb = grid.best_estimator_
    print(f"Best parameters found: {grid.best_params_}")
    
    print("Calibrating classifier...")
    model = CalibratedClassifierCV(estimator=best_xgb, cv=5)
    model.fit(X_train, y_train)
    
    models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, "xgboost.pkl")
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    main()
