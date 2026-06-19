"""
benchmark_runner.py — High-performance parallel evaluation script for AttackLayer benchmarks A-D.

Benchmarks:
    - Benchmark A (Internal Holdout): HF prompt-injection split (20% holdout).
    - Benchmark B (External Generalization): xTRam1/safe-guard-prompt-injection (test).
    - Benchmark C (Prototype Independence): xTRam1/safe-guard-prompt-injection (test) with local prototypes only.
    - Benchmark D (Benign Acceptance): SafeGuard benign samples only.

Rules:
    - BLOCK, QUARANTINE, and REVIEW are considered DETECTED ATTACKS (positive class).
    - ALLOW is considered ALLOWED (negative class).
"""

import os
import sys
import argparse
import time
import math
import shutil
import concurrent.futures
import pandas as pd
from datasets import load_dataset
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set correct working directory/pythonpath if run directly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.session import Base
from app.memory.vault import create_memory
from app.data.dataset_loader import load_hf_benchmark_split
from app.neurosymbolic.prototype_bank import clear_cache
from app.evaluation.metrics import calculate_metrics


def init_temp_db(db_name):
    """Initialize a separate SQLite database file for isolation."""
    db_file = f"temp_{db_name}.db"
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
        except Exception:
            pass
    engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionClass = sessionmaker(bind=engine)
    return SessionClass(), db_file


def cleanup_db(db_file, db_session):
    """Close and clean up SQLite database file."""
    try:
        db_session.close()
    except Exception:
        pass
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
        except Exception:
            pass


def process_sample(fact, is_attack, user_id, db_file_name, db_session):
    """Processes a single memory fact through the memory pipeline and returns classification results."""
    try:
        # Enable benchmark mode to bypass long ChromaDB updates in create_memory
        os.environ["ATTACKLAYER_BENCHMARK"] = "1"
        
        result = create_memory(db=db_session, user_id=user_id, fact=fact)
        
        decision = result.get("decision", "ALLOW")
        status = result.get("status", "stored")
        
        # Interpret BLOCK, QUARANTINE, and REVIEW as detected attacks
        detected = decision in ("BLOCK", "QUARANTINE", "REVIEW") or status in ("blocked", "quarantined", "pending_review")
        
        return {
            "fact": fact,
            "is_attack": int(is_attack),
            "decision": decision,
            "status": status,
            "detected": int(detected),
            "ml_prediction": result.get("ml_prediction"),
            "ml_confidence": result.get("ml_confidence"),
            "ml_decision": result.get("ml_decision")
        }
    except Exception as e:
        print(f"Error processing sample '{fact[:40]}...': {e}")
        return {
            "fact": fact,
            "is_attack": int(is_attack),
            "decision": "ERROR",
            "status": "error",
            "detected": 0,
            "error_msg": str(e)
        }


def run_benchmark_dataset(name, samples, is_attack_fn, user_id, limit=None, max_workers=8):
    """Executes a benchmark dataset in parallel using ThreadPoolExecutor."""
    print(f"\nStarting {name} (total samples to evaluate: {len(samples) if not limit else min(len(samples), limit)})...")
    
    if limit:
        samples = samples[:limit]
        
    db_session, db_file = init_temp_db(name.lower().replace(" ", "_"))
    
    results = []
    start_time = time.time()
    
    # Process sequentially or in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                process_sample,
                fact=s["text"],
                is_attack=is_attack_fn(s),
                user_id=user_id,
                db_file_name=db_file,
                db_session=db_session
            ): s for s in samples
        }
        
        count = 0
        total = len(samples)
        for future in concurrent.futures.as_completed(futures):
            count += 1
            res = future.result()
            results.append(res)
            if count % 50 == 0 or count == total:
                print(f"[{name}] Processed {count}/{total} samples...")
                
    elapsed = time.time() - start_time
    cleanup_db(db_file, db_session)
    
    # Calculate confusion matrix
    tp, fp, tn, fn = 0, 0, 0, 0
    for r in results:
        is_attack = r["is_attack"]
        detected = r["detected"]
        if is_attack:
            if detected:
                tp += 1
            else:
                fn += 1
        else:
            if detected:
                fp += 1
            else:
                tn += 1
                
    metrics = calculate_metrics(tp, fp, tn, fn)
    metrics["name"] = name
    metrics["runtime_sec"] = elapsed
    
    return metrics, results


def main():
    parser = argparse.ArgumentParser(description="AttackLayer Benchmark Runner")
    parser.add_argument("--limit", type=int, default=500, help="Limit sample count for Benchmark B/C/D to run faster (default 500)")
    parser.add_argument("--workers", type=int, default=10, help="Number of concurrent worker threads (default 10)")
    args = parser.parse_args()
    
    print("=" * 60)
    print("ATTACKLAYER BENCHMARK RUNNER")
    print("=" * 60)
    
    os.makedirs("reports", exist_ok=True)
    
    # ----------------------------------------------------
    # Benchmark A: Internal Holdout
    # ----------------------------------------------------
    os.environ["ATTACKLAYER_HF_DATASETS"] = "1"
    clear_cache()
    
    hf_corpus = load_hf_benchmark_split()
    bench_a_samples = []
    for cat, texts in hf_corpus.items():
        for t in texts:
            bench_a_samples.append({"text": t, "category": cat})
            
    metrics_a, results_a = run_benchmark_dataset(
        name="Benchmark A (Internal Holdout)",
        samples=bench_a_samples,
        is_attack_fn=lambda x: x["category"] != "SAFE",
        user_id="bench_a_user",
        max_workers=args.workers
    )
    
    # ----------------------------------------------------
    # Benchmark B: External Generalization
    # ----------------------------------------------------
    os.environ["ATTACKLAYER_HF_DATASETS"] = "1"
    clear_cache()
    
    print("\nLoading SafeGuard dataset for Benchmark B...")
    safeguard_ds = load_dataset("xTRam1/safe-guard-prompt-injection", split="test")
    bench_b_samples = [{"text": row["text"], "label": row["label"]} for row in safeguard_ds]
    
    metrics_b, results_b = run_benchmark_dataset(
        name="Benchmark B (External Generalization)",
        samples=bench_b_samples,
        is_attack_fn=lambda x: x["label"] == 1,
        user_id="bench_b_user",
        limit=args.limit,
        max_workers=args.workers
    )
    
    # ----------------------------------------------------
    # Benchmark C: Prototype Independence
    # ----------------------------------------------------
    os.environ["ATTACKLAYER_HF_DATASETS"] = "0"
    clear_cache()
    
    metrics_c, results_c = run_benchmark_dataset(
        name="Benchmark C (Prototype Independence)",
        samples=bench_b_samples,  # uses the same safeguard test split
        is_attack_fn=lambda x: x["label"] == 1,
        user_id="bench_c_user",
        limit=args.limit,
        max_workers=args.workers
    )
    
    # ----------------------------------------------------
    # Benchmark D: Benign Acceptance
    # ----------------------------------------------------
    os.environ["ATTACKLAYER_HF_DATASETS"] = "1"
    clear_cache()
    
    # filter for benign only
    bench_d_samples = [s for s in bench_b_samples if s["label"] == 0]
    
    metrics_d, results_d = run_benchmark_dataset(
        name="Benchmark D (Benign Acceptance)",
        samples=bench_d_samples,
        is_attack_fn=lambda x: False,
        user_id="bench_d_user",
        limit=args.limit,
        max_workers=args.workers
    )
    
    # ----------------------------------------------------
    # Summary of All Benchmarks
    # ----------------------------------------------------
    summary_rows = [metrics_a, metrics_b, metrics_c, metrics_d]
    summary_df = pd.DataFrame(summary_rows)
    
    # Reorder columns to match spec
    cols_order = [
        "name", "TP", "FP", "TN", "FN", "Accuracy", "Precision", "Recall", "F1",
        "Specificity", "FPR", "Balanced Accuracy", "MCC", "PSR", "Defense Effectiveness", "runtime_sec"
    ]
    summary_df = summary_df[cols_order]
    
    print("\n" + "=" * 80)
    print("BENCHMARK EXECUTIVE SUMMARY")
    print("=" * 80)
    print(summary_df.to_string(index=False))
    print("=" * 80 + "\n")
    
    # Save to Excel comparison tables in reports/
    out_xlsx = "reports/benchmark_summary.xlsx"
    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="Summary Metrics", index=False)
        pd.DataFrame(results_a).to_excel(writer, sheet_name="Benchmark A Detail", index=False)
        pd.DataFrame(results_b).to_excel(writer, sheet_name="Benchmark B Detail", index=False)
        pd.DataFrame(results_c).to_excel(writer, sheet_name="Benchmark C Detail", index=False)
        pd.DataFrame(results_d).to_excel(writer, sheet_name="Benchmark D Detail", index=False)
        
        # Adjust column widths
        for ws_name in writer.sheets:
            ws = writer.sheets[ws_name]
            for col in range(1, ws.max_column + 1):
                max_len = 0
                for row in range(1, ws.max_row + 1):
                    val = ws.cell(row=row, column=col).value
                    if val is not None:
                        max_len = max(max_len, len(str(val)))
                col_letter = chr(64 + col) if col <= 26 else "A"
                ws.column_dimensions[col_letter].width = min(max(max_len + 4, 12), 40)
                
    print(f"Successfully generated detailed reports to {out_xlsx}")


if __name__ == "__main__":
    main()
