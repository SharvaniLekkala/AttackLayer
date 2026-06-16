import pandas as pd

from app.security.attack_registry import classify_security

CATEGORY_MAP = {
    "benign": "SAFE",
    "instruction_override": "PROMPT_INJECTION",
    "prompt_injection": "PROMPT_INJECTION",
    "secret_leakage": "SYSTEM_PROMPT_EXTRACTION",
    "role_hijacking": "ROLE_HIJACKING",
    "data_exfiltration": "DELAYED_POISONING",
    "integrity_tampering": "FALSE_FACT_INJECTION",
}

df = pd.read_json(
    "hf://datasets/vgudur/memory-poisoning-attack-corpus/data/train.jsonl",
    lines=True,
)

correct = 0
total = len(df)

errors = []

for _, row in df.iterrows():

    expected = CATEGORY_MAP[row["category"]]

    result = classify_security(row["text"])

    predicted = result["attack_type"]

    if predicted == expected:
        correct += 1
    else:
        errors.append({
            "expected": expected,
            "predicted": predicted,
            "technique": row["technique"],
            "severity": row["severity"],
            "text": row["text"][:150]
        })

accuracy = correct / total

print()
print("Total:", total)
print("Correct:", correct)
print("Accuracy:", round(accuracy * 100, 2), "%")
print()

print("====== FAILURES ======")

for e in errors:
    print()
    print("Expected :", e["expected"])
    print("Predicted:", e["predicted"])
    print("Technique:", e["technique"])
    print("Severity :", e["severity"])
    print("Text     :", e["text"])