from datasets import load_dataset

from app.security.security_gateway import evaluate_security

import time


def run_benchmark_d():

    start_time = time.time()

    ds = load_dataset(
        "xTRam1/safe-guard-prompt-injection",
        split="test"
    )

    # Keep only benign samples
    ds = ds.filter(
        lambda x: x["label"] == 0
    )

    print("\n========== BENCHMARK D ==========\n")
    print(f"Benign Samples: {len(ds)}")

    tn = 0
    fp = 0

    total = 0

    false_positives = []

    for row in ds:

        text = row["text"]

        result = evaluate_security(text)

        decision = result["decision"]

        detected = (
            decision == "BLOCK"
            or decision == "ALLOW_WITH_WARNING"
        )

        total += 1

        if detected:

            fp += 1

            if len(false_positives) < 50:

                false_positives.append(
                    {
                        "text": text,
                        "decision": decision,
                        "attack_type": result["attack_type"],
                        "risk_level": result["risk_level"],
                    }
                )

        else:

            tn += 1

        if total % 100 == 0:
            print(
                f"Processed {total}/{len(ds)}"
            )

    specificity = (
        tn / (tn + fp)
        if (tn + fp)
        else 0
    )

    fpr = (
        fp / (tn + fp)
        if (tn + fp)
        else 0
    )

    runtime = time.time() - start_time

    print("\n")
    print("=" * 50)
    print("FINAL RESULTS")
    print("=" * 50)

    print()

    print(f"TN (Allowed Benign): {tn}")
    print(f"FP (Blocked Benign): {fp}")

    print()

    print(
        f"Specificity: {specificity:.4f}"
    )

    print(
        f"False Positive Rate: {fpr:.4f}"
    )

    print(
        f"Benign Acceptance Rate: {specificity:.4f}"
    )

    print()
    print(f"Runtime: {runtime:.2f} sec")

    print("\n========== FIRST FALSE POSITIVES ==========\n")

    for i, sample in enumerate(false_positives, 1):

        print("=" * 80)
        print(f"FP #{i}")

        print("\nAttack Type:")
        print(sample["attack_type"])

        print("\nRisk Level:")
        print(sample["risk_level"])

        print("\nDecision:")
        print(sample["decision"])

        print("\nText:")
        print(sample["text"])

        print()


if __name__ == "__main__":
    run_benchmark_d()