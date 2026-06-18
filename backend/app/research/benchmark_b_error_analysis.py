from datasets import load_dataset

from app.security.security_gateway import evaluate_security

import json
def run_error_analysis():

    ds = load_dataset(
        "xTRam1/safe-guard-prompt-injection",
        split="test"
    )

    missed_attacks = []
    false_positives = []

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

        # False Negative
        if is_attack and not detected:

            missed_attacks.append({
                "text": text,
                "attack_type": result["attack_type"],
                "decision": decision,
                "risk_level": result["risk_level"],
                "category": result["category"],
            })

        # False Positive
        if (not is_attack) and detected:

            false_positives.append({
                "text": text,
                "attack_type": result["attack_type"],
                "decision": decision,
                "risk_level": result["risk_level"],
                "category": result["category"],
            })

        if total % 100 == 0:
            print(f"Processed {total}/{len(ds)}")

    print("\n")
    print("=" * 50)
    print("ERROR ANALYSIS")
    print("=" * 50)

    print()
    print(f"Missed Attacks (FN): {len(missed_attacks)}")
    print(f"False Positives (FP): {len(false_positives)}")

    print("\n========== FIRST 100 MISSED ATTACKS ==========\n")

    for i, attack in enumerate(missed_attacks[:100], 1):

        print("=" * 80)
        print(f"FN #{i}")
        print("=" * 80)

        print("Decision:")
        print(attack["decision"])

        print("\nAttack Type:")
        print(attack["attack_type"])

        print("\nRisk Level:")
        print(attack["risk_level"])

        print("\nCategory:")
        print(attack["category"])

        print("\nText:")
        print(attack["text"])

        print()

    print("\n========== FALSE POSITIVES ==========\n")

    for i, fp in enumerate(false_positives[:50], 1):

        print("=" * 80)
        print(f"FP #{i}")
        print("=" * 80)

        print("Decision:")
        print(fp["decision"])

        print("\nAttack Type:")
        print(fp["attack_type"])

        print("\nRisk Level:")
        print(fp["risk_level"])

        print("\nCategory:")
        print(fp["category"])

        print("\nText:")
        print(fp["text"])

        print()

    with open(
        "missed_attacks.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            missed_attacks,
            f,
            indent=2,
            ensure_ascii=False
        )


    with open(
        "false_positives.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            false_positives,
            f,
            indent=2,
            ensure_ascii=False
        )
if __name__ == "__main__":
    run_error_analysis()