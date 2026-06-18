from app.database.session import SessionLocal
from app.memory.vault import create_memory

from app.data.dataset_loader import (
    load_hf_benchmark_split
)

import math 
def run_hf_benchmark():

    db = SessionLocal()

    corpus = load_hf_benchmark_split()

    total = 0
    blocked = 0
    quarantined = 0
    stored = 0
    attack_detected = 0
    attack_missed = 0

    safe_blocked = 0
    safe_allowed = 0
    
    print("\n========== HF DATASET EVALUATION ==========\n")

    for attack_type, samples in corpus.items():

        attack_total = 0
        attack_blocked = 0
        attack_quarantined = 0
        attack_stored = 0

        for sample in samples:

            result = create_memory(
                db=db,
                user_id="hf_benchmark",
                fact=sample,
            )

            status = result["status"]

            total += 1
            attack_total += 1

            is_attack = attack_type != "SAFE"

            if status == "blocked":

                blocked += 1
                attack_blocked += 1

                if is_attack:
                    attack_detected += 1
                else:
                    safe_blocked += 1

            elif status == "quarantined":

                quarantined += 1
                attack_quarantined += 1

                if is_attack:
                    attack_detected += 1
                else:
                    safe_blocked += 1

            else:

                stored += 1
                attack_stored += 1

                if is_attack:
                    attack_missed += 1
                else:
                    safe_allowed += 1

        detection_rate = (
            attack_blocked +
            attack_quarantined
        ) / attack_total

        attack_success_rate = (
            attack_stored
        ) / attack_total

        print(f"\n{attack_type}")
        print("-" * 40)
        print(f"Samples: {attack_total}")
        print(f"Blocked: {attack_blocked}")
        print(f"Quarantined: {attack_quarantined}")
        print(f"Stored: {attack_stored}")
        print(
            f"Detection Rate: "
            f"{detection_rate:.4f}"
        )
        print(
            f"Attack Success Rate: "
            f"{attack_success_rate:.4f}"
        )

    dr = (
        blocked +
        quarantined
    ) / total

    psr = (
        stored
    ) / total

    des = 1 - psr

    print("\n")
    print("=" * 50)
    print("FINAL RESULTS")
    print("=" * 50)

    print(f"Dataset Size: {total}")
    print(f"Blocked: {blocked}")
    print(f"Quarantined: {quarantined}")
    print(f"Stored: {stored}")

    print("\nRESEARCH METRICS\n")

    print(f"Detection Rate (DR): {dr:.4f}")
    print(f"Poisoning Success Rate (PSR): {psr:.4f}")
    print(f"Defense Effectiveness: {des:.4f}")
    print("\n========== CONFUSION MATRIX ==========\n")

    print(f"TP (Detected Attacks): {attack_detected}")
    print(f"FN (Missed Attacks): {attack_missed}")
    print(f"FP (Blocked Safe Samples): {safe_blocked}")
    print(f"TN (Allowed Safe Samples): {safe_allowed}")

    print("\n========== EXTRA METRICS ==========\n")

    tp = attack_detected
    fn = attack_missed
    fp = safe_blocked
    tn = safe_allowed

    accuracy = (
        (tp + tn) / (tp + tn + fp + fn)
        if (tp + tn + fp + fn)
        else 0
    )

    precision = (
        tp / (tp + fp)
        if (tp + fp)
        else 0
    )

    recall = (
        tp / (tp + fn)
        if (tp + fn)
        else 0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall)
        else 0
    )

    fpr = (
        fp / (fp + tn)
        if (fp + tn)
        else 0
    )
    specificity = (
    tn / (tn + fp)
    if (tn + fp)
    else 0
)

    psr = (
        fn / (tp + fn)
        if (tp + fn)
        else 0
    )

    defense_effectiveness = 1 - psr
    balanced_accuracy = (
    recall + specificity
) / 2
    mcc_denominator = math.sqrt(
        (tp + fp)
        * (tp + fn)
        * (tn + fp)
        * (tn + fn)
    )

    mcc = (
        (tp * tn) - (fp * fn)
    ) / mcc_denominator if mcc_denominator else 0
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall / Detection Rate: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print(f"Specificity: {specificity:.4f}")
    print(f"Balanced Accuracy: {balanced_accuracy:.4f}")
    print(f"MCC: {mcc:.4f}")

    print()

    print(f"False Positive Rate (FPR): {fpr:.4f}")
    print(f"Poisoning Success Rate (PSR): {psr:.4f}")
    print(f"Defense Effectiveness: {defense_effectiveness:.4f}")
    
    db.close()
    

if __name__ == "__main__":
    run_hf_benchmark()