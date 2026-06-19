import os
import shutil
import numpy as np
from pytorch_tabnet.tab_model import TabNetClassifier
import torch
from app.ml.utils import load_split_data

def main():
    print("--- Training TabNet ---")
    X_train, X_val, X_test, y_train, y_val, y_test = load_split_data()
    
    # Grid search hyperparameters
    n_d_options = [8, 16]
    n_a_options = [8, 16]
    lr_options = [0.01, 0.02, 0.05]
    
    best_val_auc = -1
    best_params = {}
    best_model = None
    
    print("Performing parameter search for TabNet on CPU...")
    
    for nd in n_d_options:
        for na in n_a_options:
            for lr in lr_options:
                print(f"Trying n_d={nd}, n_a={na}, lr={lr}...")
                clf = TabNetClassifier(
                    n_d=nd, 
                    n_a=na, 
                    optimizer_params=dict(lr=lr),
                    verbose=0,
                    device_name='cpu'
                )
                
                # TabNet fits with train and validation sets
                clf.fit(
                    X_train=X_train, y_train=y_train,
                    eval_set=[(X_val, y_val)],
                    eval_name=['val'],
                    eval_metric=['auc'],
                    max_epochs=50,
                    patience=10,
                    batch_size=128,
                    virtual_batch_size=16,
                    num_workers=0,
                    drop_last=False
                )
                
                val_auc = clf.best_cost
                if val_auc > best_val_auc:
                    best_val_auc = val_auc
                    best_params = {'n_d': nd, 'n_a': na, 'lr': lr}
                    best_model = clf
                    
    print(f"Best TabNet params: {best_params} with Validation AUC: {best_val_auc:.4f}")
    
    # Save model
    models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
    os.makedirs(models_dir, exist_ok=True)
    
    # TabNet saves as a zip, so we save to models/tabnet (which writes tabnet.zip)
    save_path = os.path.join(models_dir, "tabnet")
    # If the file already exists, pytorch-tabnet might fail or overwrite.
    # TabNetClassifier.save_model appends '.zip' internally, let's call it:
    saved_filepath = best_model.save_model(save_path)
    print(f"TabNet model saved to {saved_filepath}")

if __name__ == "__main__":
    main()
