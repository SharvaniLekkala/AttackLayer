import os
import joblib
import numpy as np
import pandas as pd
import ollama

from sklearn.svm import SVC


print("[1/5] Loading dataset")

df = pd.read_csv(
    "data/final_dataset.csv"
)

texts = df["text"].tolist()
labels = df["label"].tolist()


# ----------------------------------------
# Embeddings
# ----------------------------------------

if (
    os.path.exists("data/embeddings.npy")
    and
    os.path.exists("data/labels.npy")
):

    print("[2/5] Loading cached embeddings")

    X = np.load(
        "data/embeddings.npy"
    )

    y = np.load(
        "data/labels.npy"
    )

else:

    X = []
    y = []

    print("[2/5] Creating embeddings")

    for i, text in enumerate(texts):

        response = ollama.embeddings(
            model="nomic-embed-text",
            prompt=str(text)
        )

        X.append(
            response["embedding"]
        )

        y.append(
            labels[i]
        )

    X = np.array(X)
    y = np.array(y)

    np.save(
        "data/embeddings.npy",
        X
    )

    np.save(
        "data/labels.npy",
        y
    )


print("[3/5] Training Cost-Sensitive SVM")

from sklearn.svm import SVC
from sklearn.calibration import CalibratedClassifierCV

base_svm = SVC(
    class_weight="balanced"
)

model = CalibratedClassifierCV(
    estimator=base_svm,
    cv=5
)

model.fit(
    X,
    y
)

os.makedirs(
    "models",
    exist_ok=True
)

print("[4/5] Saving model")

joblib.dump(
    model,
    "models/final_svm_model.pkl"
)

print("[5/5] Done")

print()
print(
    "Saved to models/final_svm_model.pkl"
)