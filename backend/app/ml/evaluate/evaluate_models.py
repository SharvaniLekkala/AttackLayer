import os
import pickle
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import (
    roc_auc_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_curve,
)

# Ensure backend path is in PYTHONPATH when run as module
from app.ml.utils import load_split_data

# Helper to load sklearn-like models
def load_pickle_model(path):
    import joblib
    return joblib.load(path)

# Helper to load PyTorch MLP
def load_torch_model(path, input_dim=None):
    import torch
    # Simple MLP matching the training architecture
    class SimpleMLP(torch.nn.Module):
        def __init__(self, input_dim, hidden_dim=128, dropout_rate=0.3):
            super().__init__()
            self.network = torch.nn.Sequential(
                torch.nn.Linear(input_dim, hidden_dim),
                torch.nn.ReLU(),
                torch.nn.BatchNorm1d(hidden_dim),
                torch.nn.Dropout(dropout_rate),
                torch.nn.Linear(hidden_dim, hidden_dim // 2),
                torch.nn.ReLU(),
                torch.nn.BatchNorm1d(hidden_dim // 2),
                torch.nn.Dropout(dropout_rate),
                torch.nn.Linear(hidden_dim // 2, 2),
            )
        def forward(self, x):
            return self.network(x)
    state = torch.load(path, map_location='cpu')
    if input_dim is None:
        # Infer input dimension from first layer weight shape
        first_weight = next(iter(state.values()))
        input_dim = first_weight.shape[1]
    model = SimpleMLP(input_dim)
    model.load_state_dict(state)
    model.eval()
    return model

# Helper to load TabNet model
def load_tabnet_model(path):
    from pytorch_tabnet.tab_model import TabNetClassifier
    model = TabNetClassifier()
    model.load_model(path)
    return model

def evaluate_model(model, X_test, y_test, model_type):
    if model_type == 'torch':
        import torch
        with torch.no_grad():
            outputs = model(torch.from_numpy(X_test.astype(np.float32)))
        # outputs shape (n_samples, 2); use probability of class 1
        prob_pos = outputs[:, 1].numpy()
        preds = (prob_pos > 0.5).astype(int)
    elif model_type == 'tabnet':
        probs = model.predict_proba(X_test)[:, 1]
        preds = (probs > 0.5).astype(int)
        prob_pos = probs
    else:  # sklearn compatible
        if hasattr(model, 'predict_proba'):
            prob_pos = model.predict_proba(X_test)[:, 1]
        else:
            # fallback to decision function
            prob_pos = model.decision_function(X_test)
            prob_pos = (prob_pos - prob_pos.min()) / (prob_pos.max() - prob_pos.min())
        preds = (prob_pos > 0.5).astype(int)

    tn, fp, fn, tp = confusion_matrix(y_test, preds).ravel()
    metrics = {
        'TP': tp,
        'FP': fp,
        'TN': tn,
        'FN': fn,
        'Accuracy': accuracy_score(y_test, preds),
        'Precision': precision_score(y_test, preds, zero_division=0),
        'Recall': recall_score(y_test, preds, zero_division=0),
        'F1': f1_score(y_test, preds, zero_division=0),
        'AUC': roc_auc_score(y_test, prob_pos),
        'Specificity': tn / (tn + fp) if (tn + fp) > 0 else 0,
        'FPR': fp / (fp + tn) if (fp + tn) > 0 else 0,
    }
    return metrics, prob_pos

def main():
    # Load data splits
    X_train, X_val, X_test, y_train, y_val, y_test = load_split_data()

    # Directory where models are stored
    models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'models')
    model_paths = {
        'SVM': os.path.join(models_dir, 'svm.pkl'),
        'RandomForest': os.path.join(models_dir, 'random_forest.pkl'),
        'XGBoost': os.path.join(models_dir, 'xgboost.pkl'),
        'LightGBM': os.path.join(models_dir, 'lightgbm.pkl'),
        'MLP_sklearn': os.path.join(models_dir, 'mlp_sklearn.pkl'),
        'MLP_torch': os.path.join(models_dir, 'mlp.pth'),
        'TabNet': os.path.join(models_dir, 'tabnet.zip'),
    }

    results = []
    plt.figure(figsize=(10, 8))
    for name, path in model_paths.items():
        if not os.path.exists(path):
            print(f"Model file missing: {path}, skipping {name}")
            continue
        if name == 'MLP_torch':
            model = load_torch_model(path)
            mtype = 'torch'
        elif name == 'TabNet':
            model = load_tabnet_model(path)
            mtype = 'tabnet'
        else:
            model = load_pickle_model(path)
            mtype = 'sklearn'
        metrics, prob_pos = evaluate_model(model, X_test, y_test, mtype)
        metrics['Model'] = name
        results.append(metrics)
        # ROC curve
        fpr, tpr, _ = roc_curve(y_test, prob_pos)
        plt.plot(fpr, tpr, label=f"{name} (AUC={metrics['AUC']:.3f})")

    # Save summary table
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'reports'))
    os.makedirs(out_dir, exist_ok=True)
    summary_df = pd.DataFrame(results)
    summary_csv = os.path.join(out_dir, 'model_comparison.csv')
    summary_df.to_csv(summary_csv, index=False)
    # Excel with same sheet
    summary_excel = os.path.join(out_dir, 'model_comparison.xlsx')
    with pd.ExcelWriter(summary_excel, engine='openpyxl') as writer:
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    # Save ROC plot
    plt.plot([0, 1], [0, 1], '--', color='gray')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curves for Trained Models')
    plt.legend(loc='lower right')
    plot_path = os.path.join(out_dir, 'roc_curves.png')
    plt.tight_layout()
    plt.savefig(plot_path)
    print(f"Evaluation complete. Summary saved to {summary_csv} and {summary_excel}. ROC plot saved to {plot_path}.")

if __name__ == '__main__':
    main()
