import os
import pandas as pd

os.makedirs("data", exist_ok=True)

print("[1/5] Loading deepset dataset")

deepset_df = pd.read_csv(
    "data/ml_dataset.csv"
)

print("deepset =", len(deepset_df))

print()

print("[2/5] Loading jailbreak dataset")

jb_train = pd.read_csv(
    "data/jailbreak_dataset_train_balanced.csv"
)

jb_test = pd.read_csv(
    "data/jailbreak_dataset_test_balanced.csv"
)

jb_full = pd.read_csv(
    "data/jailbreak_dataset_full_balanced.csv"
)

jailbreak_df = pd.concat(
    [jb_train, jb_test, jb_full],
    ignore_index=True
)

print("jailbreak =", len(jailbreak_df))

print()

print("[3/5] Converting labels")

# CHANGE THESE COLUMN NAMES IF NECESSARY
jailbreak_df["label"] = (
    jailbreak_df["type"]
    .str.lower()
    .map(
        {
            "benign": 0,
            "jailbreak": 1
        }
    )
)

jailbreak_df = jailbreak_df.rename(
    columns={
        "prompt": "text"
    }
)

jailbreak_df = jailbreak_df[
    ["text", "label"]
]

print()

print("[4/5] Combining")

combined = pd.concat(
    [deepset_df, jailbreak_df],
    ignore_index=True
)

combined.drop_duplicates(
    inplace=True
)

print()

print(combined["label"].value_counts())

print()

print("[5/5] Saving")

combined.to_csv(
    "data/final_dataset.csv",
    index=False
)

print()

print("Final shape =", combined.shape)