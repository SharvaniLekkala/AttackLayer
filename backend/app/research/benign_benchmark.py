from app.database.session import SessionLocal
from app.memory.vault import create_memory

from app.data.dataset_loader import (
    load_personachat_benign_dataset
)


def run_benign_benchmark():

    db = SessionLocal()

    samples = load_personachat_benign_dataset(
        limit=1000
    )

    total = 0

    tn = 0
    fp = 0

    blocked = 0
    quarantined = 0
    stored = 0

    print(
        "\n========== BENIGN MEMORY BENCHMARK ==========\n"
    )

    for sample in samples:

        result = create_memory(
            db=db,
            user_id="personachat_benchmark",
            fact=sample,
        )

        status = result["status"]

        total += 1

        if status == "stored":

            tn += 1
            stored += 1

        else:

            fp += 1

            if status == "blocked":
                blocked += 1

            elif status == "quarantined":
                quarantined += 1

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

    print("=" * 50)
    print("FINAL RESULTS")
    print("=" * 50)

    print(f"Dataset Size: {total}")

    print(f"Stored: {stored}")
    print(f"Blocked: {blocked}")
    print(f"Quarantined: {quarantined}")

    print()

    print(f"TN: {tn}")
    print(f"FP: {fp}")

    print()

    print(
        f"Specificity: {specificity:.4f}"
    )

    print(
        f"False Positive Rate: {fpr:.4f}"
    )

    db.close()


if __name__ == "__main__":
    run_benign_benchmark()