"""
generate_reports.py — Generates exact Excel comparison tables for AttackLayer benchmarks A-D and ML models.
Uses the verified metrics provided by the user.
"""

import os
import pandas as pd


def generate_all_excel_reports():
    os.makedirs("reports", exist_ok=True)

    # 1. benchmark_summary.xlsx
    bench_data = {
        "Metric": [
            "Purpose", "HF Prototypes", "Dataset", "Samples", "TP", "FN", "FP", "TN",
            "Accuracy", "Precision", "Recall", "F1 Score", "Specificity", "FPR",
            "Balanced Accuracy", "MCC", "PSR", "Defense Effectiveness", "Benign Acceptance Rate"
        ],
        "Benchmark A (Internal Holdout)": [
            "Internal Holdout", "ON", "HF Test Split", 15, 10, 2, 0, 3,
            "86.67%", "100.00%", "83.33%", "90.91%", "100.00%", "0.00%",
            "91.67%", "0.7071", "16.67%", "83.33%", "-"
        ],
        "Benchmark B (External Generalization)": [
            "External Generalization", "ON", "SafeGuard Test", 2060, 266, 384, 10, 1400,
            "80.87%", "96.38%", "40.92%", "57.45%", "99.29%", "0.71%",
            "70.11%", "0.5486", "59.08%", "40.92%", "-"
        ],
        "Benchmark C (Prototype Independence)": [
            "Prototype Independence", "OFF", "SafeGuard Test", 2060, 149, 501, 16, 1394,
            "74.90%", "90.30%", "22.92%", "36.56%", "98.87%", "1.13%",
            "60.89%", "0.3730", "77.08%", "22.92%", "-"
        ],
        "Benchmark D (Benign Acceptance)": [
            "Benign Acceptance", "OFF", "SafeGuard Benign Only", 1410, "-", "-", 16, 1394,
            "-", "-", "-", "-", "98.87%", "1.13%",
            "-", "-", "-", "-", "98.87%"
        ]
    }
    df_bench = pd.DataFrame(bench_data)
    bench_out = os.path.join("reports", "benchmark_summary.xlsx")
    with pd.ExcelWriter(bench_out, engine="openpyxl") as writer:
        df_bench.to_excel(writer, sheet_name="Benchmark Summary", index=False)
        ws = writer.sheets["Benchmark Summary"]
        for col_idx, col in enumerate(df_bench.columns, 1):
            max_len = max(len(str(col)), df_bench[col].astype(str).str.len().max())
            ws.column_dimensions[chr(64 + col_idx) if col_idx <= 26 else "A"].width = min(max_len + 4, 40)
    print(f"[DONE] {bench_out}")

    # 2. model_comparison.xlsx
    model_data = {
        "Model": ["SVM", "Stacking", "MLP", "LR"],
        "Accuracy": [95.92, 95.92, 95.65, 94.02],
        "Precision": [100.0, 96.99, 95.32, 93.06],
        "Recall": [91.23, 94.15, 95.32, 94.15],
        "F1": [95.41, 95.55, 95.32, 93.60],
        "MCC": [0.9207, 0.9183, 0.9126, 0.8800]
    }
    df_model = pd.DataFrame(model_data)
    model_out = os.path.join("reports", "model_comparison.xlsx")
    with pd.ExcelWriter(model_out, engine="openpyxl") as writer:
        df_model.to_excel(writer, sheet_name="Model Comparison", index=False)
        ws = writer.sheets["Model Comparison"]
        for col_idx, col in enumerate(df_model.columns, 1):
            max_len = max(len(str(col)), df_model[col].astype(str).str.len().max())
            ws.column_dimensions[chr(64 + col_idx) if col_idx <= 26 else "A"].width = min(max_len + 4, 30)
    print(f"[DONE] {model_out}")

    # 3. algorithms_tested.xlsx
    algo_data = {
        "Algorithm": ["Logistic Regression", "Random Forest", "XGBoost", "LightGBM", "SVM", "MLP"],
        "Accuracy": [0.940, 0.899, 0.913, 0.913, 0.959, 0.954],
        "Precision": [0.931, 0.993, 0.960, 0.966, 1.000, 0.953],
        "Recall": [0.942, 0.789, 0.848, 0.842, 0.912, 0.947],
        "F1": [0.936, 0.879, 0.901, 0.900, 0.954, 0.950],
        "Specificity": [0.939, 0.995, 0.970, 0.975, 1.000, 0.959],
        "Balanced Accuracy": [0.940, 0.892, 0.909, 0.908, 0.956, 0.953],
        "MCC": [0.880, 0.811, 0.829, 0.830, 0.921, 0.907]
    }
    df_algo = pd.DataFrame(algo_data)
    algo_out = os.path.join("reports", "algorithms_tested.xlsx")
    with pd.ExcelWriter(algo_out, engine="openpyxl") as writer:
        df_algo.to_excel(writer, sheet_name="Algorithms Tested", index=False)
        ws = writer.sheets["Algorithms Tested"]
        for col_idx, col in enumerate(df_algo.columns, 1):
            max_len = max(len(str(col)), df_algo[col].astype(str).str.len().max())
            ws.column_dimensions[chr(64 + col_idx) if col_idx <= 26 else "A"].width = min(max_len + 4, 30)
    print(f"[DONE] {algo_out}")

    # 4. best_result.xlsx
    best_data = {
        "Metric": [
            "Model", "Accuracy", "Precision", "Recall", "F1",
            "Specificity", "FPR", "Balanced Accuracy", "MCC",
            "PSR", "Defense Effectiveness", "Recommendation Reason"
        ],
        "Value": [
            "Cost-Sensitive Calibrated SVM",
            "95.92%", "100.00%", "91.23%", "95.41%",
            "100.00%", "0.00%", "95.56%", "0.9207",
            "8.77%", "91.23%", "Precision = 100%, FPR = 0, MCC = 0.9207. Prevents false positive blocks completely."
        ]
    }
    df_best = pd.DataFrame(best_data)
    best_out = os.path.join("reports", "best_result.xlsx")
    with pd.ExcelWriter(best_out, engine="openpyxl") as writer:
        df_best.to_excel(writer, sheet_name="Best Result", index=False)
        ws = writer.sheets["Best Result"]
        ws.column_dimensions["A"].width = 25
        ws.column_dimensions["B"].width = 45
    print(f"[DONE] {best_out}")

    # 5. attack_categories.xlsx
    attacks = [
        {"Category": "PROMPT_INJECTION", "Description": "Direct/indirect instruction injection to override system behavior", "Mitigation": "Security Filter → BLOCK"},
        {"Category": "MEMORY_POISONING", "Description": "Injecting false data into long-term memory stores", "Mitigation": "Quarantine + Trust Engine"},
        {"Category": "FALSE_FACT_INJECTION", "Description": "Planting factually incorrect information as memories", "Mitigation": "Fact Verification → BLOCK"},
        {"Category": "ROLE_HIJACK", "Description": "Attempting to change the agent's role or persona", "Mitigation": "Semantic Detection → BLOCK"},
        {"Category": "SYSTEM_PROMPT_EXTRACTION", "Description": "Trying to extract system-level instructions or configurations", "Mitigation": "Secret Request Detector → BLOCK"},
        {"Category": "TOOL_POLICY_MANIPULATION", "Description": "Modifying tool access policies or approved domains", "Mitigation": "Policy Validator + HITL"},
        {"Category": "MEMORY_OVERRIDE", "Description": "Overwriting existing memories with conflicting information", "Mitigation": "Version Control + Conflict Engine"},
        {"Category": "DELAYED_POISONING", "Description": "Time-delayed attacks that activate after trust is built", "Mitigation": "Temporal Trust Decay + Re-verification"},
        {"Category": "PROPAGATION_ATTACK", "Description": "Attacks that spread across memory entries or agent instances", "Mitigation": "Propagation Tracking + Isolation"},
    ]
    df_attack = pd.DataFrame(attacks)
    attack_out = os.path.join("reports", "attack_categories.xlsx")
    with pd.ExcelWriter(attack_out, engine="openpyxl") as writer:
        df_attack.to_excel(writer, sheet_name="Attack Categories", index=False)
        ws = writer.sheets["Attack Categories"]
        ws.column_dimensions["A"].width = 30
        ws.column_dimensions["B"].width = 60
        ws.column_dimensions["C"].width = 40
    print(f"[DONE] {attack_out}")


if __name__ == "__main__":
    generate_all_excel_reports()
