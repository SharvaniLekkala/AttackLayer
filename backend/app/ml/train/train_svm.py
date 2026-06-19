import os
import joblib
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
from sklearn.calibration import CalibratedClassifierCV
from app.ml.utils import load_split_data

def main():
    print("--- Training SVM ---")
    X_train, X_val, X_test, y_train, y_val, y_test = load_split_data()
    
    # Define parameters to search
    param_grid = {
        'C': [0.1, 1.0, 10.0, 100.0],
        'gamma': ['scale', 'auto', 0.001, 0.01, 0.1]
    }
    
    print("Performing grid search...")
    grid = GridSearchCV(SVC(class_weight='balanced'), param_grid, cv=5, scoring='f1')
    grid.fit(X_train, y_train)
    
    best_svc = grid.best_estimator_
    print(f"Best parameters found: {grid.best_params_}")
    
    print("Calibrating classifier...")
    model = CalibratedClassifierCV(estimator=best_svc, cv=5)
    model.fit(X_train, y_train)
    
    # Save the model
    models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, "svm.pkl")
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    main()
