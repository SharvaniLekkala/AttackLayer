from datasets import load_dataset
from app.security.security_gateway import evaluate_security

import math
import time


def run_benchmark_b():

    start_time = time.time()

    ds = load_dataset(
        "xTRam1/safe-guard-prompt-injection",
        split="test"
    )

    print("\n========== BENCHMARK B ==========\n")
    print(f"Dataset Size: {len(ds)}")

    tp = 0
    fp = 0
    tn = 0
    fn = 0

    total = 0

    for row in ds:

        text = row["text"]
        label = row["label"]

        is_attack = label == 1

        result = evaluate_security(text)

        decision = result["decision"]

        detected = (
            decision == "BLOCK"
            or decision == "ALLOW_WITH_WARNING"
        )

        total += 1

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

        if total % 100 == 0:
            print(
                f"Processed {total}/{len(ds)}"
            )

    accuracy = (
        (tp + tn) /
        (tp + tn + fp + fn)
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
        2 * precision * recall /
        (precision + recall)
        if (precision + recall)
        else 0
    )

    specificity = (
        tn / (tn + fp)
        if (tn + fp)
        else 0
    )

    fpr = (
        fp / (fp + tn)
        if (fp + tn)
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
        (tp * tn)
        - (fp * fn)
    ) / mcc_denominator if mcc_denominator else 0

    runtime = time.time() - start_time

    print("\n")
    print("=" * 50)
    print("FINAL RESULTS")
    print("=" * 50)

    print(f"Dataset Size: {total}")

    print("\n========== CONFUSION MATRIX ==========\n")

    print(f"TP: {tp}")
    print(f"FN: {fn}")
    print(f"FP: {fp}")
    print(f"TN: {tn}")

    print("\n========== METRICS ==========\n")

    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")

    print()

    print(f"Specificity: {specificity:.4f}")
    print(f"Balanced Accuracy: {balanced_accuracy:.4f}")
    print(f"MCC: {mcc:.4f}")

    print()

    print(f"False Positive Rate: {fpr:.4f}")
    print(f"Poisoning Success Rate: {psr:.4f}")
    print(
        f"Defense Effectiveness: "
        f"{defense_effectiveness:.4f}"
    )

    print()
    print(f"Runtime: {runtime:.2f} seconds")


if __name__ == "__main__":
    run_benchmark_b()