"""
V2 Evaluation Metrics — precision, recall, F1, retrieval quality.
"""

from app.database.models import ClassificationStat, AuditEvent, Memory
from app.learning.classification_tracker import get_learning_stats


def _safe_divide(numerator, denominator):
    return round(numerator / denominator, 4) if denominator else 0.0


def compute_classification_metrics(db):
    stats = db.query(ClassificationStat).all()

    tp = sum(
        1 for s in stats
        if s.was_blocked and s.predicted_label != "SAFE"
        and not s.is_false_positive
    )
    fp = sum(1 for s in stats if s.is_false_positive)
    fn = sum(1 for s in stats if s.is_false_negative)
    tn = sum(
        1 for s in stats
        if not s.was_blocked and s.predicted_label == "SAFE"
    )

    precision = _safe_divide(tp, tp + fp)
    recall = _safe_divide(tp, tp + fn)
    f1 = _safe_divide(
        2 * precision * recall,
        precision + recall,
    )

    learning = get_learning_stats(db)

    audits = db.query(AuditEvent).all()
    memories = db.query(Memory).filter(Memory.active == True).all()

    avg_trust = (
        round(sum(m.trust_score for m in memories) / len(memories), 4)
        if memories else 0.0
    )

    poison_detected = sum(
        1 for e in audits
        if e.poison_detected
    )

    avg_response_conf = (
        round(
            sum(e.response_confidence for e in audits if e.response_confidence) /
            max(1, sum(1 for e in audits if e.response_confidence)),
            4,
        )
        if any(e.response_confidence for e in audits) else 0.0
    )
    # ====================================
    # Research Metrics
    # ====================================

    total_attacks = sum(
        1
        for e in audits
        if e.attack_type not in ("SAFE", "NONE", None)
    )

    detected_attacks = sum(
        1
        for e in audits
        if e.attack_type not in ("SAFE", "NONE", None)
        and e.poison_detected
    )

    successful_poison_attacks = sum(
        1
        for e in audits
        if e.attack_type not in ("SAFE", "NONE", None)
        and e.decision == "ALLOW"
    )

    poisoned_memories = sum(
        1
        for m in memories
        if m.poison_flag
    )

    quarantined_memories = sum(
        1
        for m in memories
        if m.final_decision == "QUARANTINE"
    )

    recovered_memories = quarantined_memories

    detection_rate = _safe_divide(
        detected_attacks,
        total_attacks
    )

    poisoning_success_rate = _safe_divide(
        successful_poison_attacks,
        total_attacks
    )

    memory_contamination_rate = _safe_divide(
        poisoned_memories,
        len(memories)
    )

    recovery_rate = _safe_divide(
        recovered_memories,
        detected_attacks
    )

    defense_effectiveness = round(
        1 - poisoning_success_rate,
        4
    )
    attack_classification_accuracy = (
    compute_attack_classification_accuracy(db)
)
    print("\n========== RESEARCH METRICS ==========")
    print(f"Detection Rate (DR): {detection_rate:.4f}")
    print(f"Poisoning Success Rate (PSR): {poisoning_success_rate:.4f}")
    print(f"False Positive Rate (FPR): {_safe_divide(fp, fp + tn):.4f}")
    print(f"Memory Contamination Rate (MCR): {memory_contamination_rate:.4f}")
    print(f"Recovery Rate (RR): {recovery_rate:.4f}")
    print(f"Defense Effectiveness: {defense_effectiveness:.4f}")
    print(f"Attack Classification Accuracy (ACA): {attack_classification_accuracy:.4f}")
    print("======================================\n")
    return {
        "intent_accuracy": learning["accuracy"],
        "attack_classification_accuracy": learning["accuracy"],
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "false_positive_rate": _safe_divide(fp, fp + tn),
        "false_negative_rate": _safe_divide(fn, fn + tp),
        "poison_detection_rate": _safe_divide(
            poison_detected,
            max(1, sum(1 for e in audits if e.attack_type and e.attack_type != "SAFE")),
        ),
        "average_response_confidence": avg_response_conf,
        "average_trust_score": avg_trust,
        "total_audits": len(audits),
        "total_memories": len(memories),
        "poisoning_success_rate": poisoning_success_rate,

"detection_rate": detection_rate,

"memory_contamination_rate":
memory_contamination_rate,

"recovery_rate":
recovery_rate,

"defense_effectiveness":
defense_effectiveness,
"attack_classification_accuracy":
attack_classification_accuracy,
    }


def compute_retrieval_metrics(retrieved_ids, relevant_ids, k=5):
    retrieved_set = set(retrieved_ids[:k])
    relevant_set = set(relevant_ids)

    hits = len(retrieved_set & relevant_set)
    recall_at_k = _safe_divide(hits, len(relevant_set))

    mrr = 0.0
    for rank, mem_id in enumerate(retrieved_ids[:k], 1):
        if mem_id in relevant_set:
            mrr = round(1.0 / rank, 4)
            break

    dcg = sum(
        1.0 / __import__("math").log2(i + 2)
        for i, mem_id in enumerate(retrieved_ids[:k])
        if mem_id in relevant_set
    )
    ideal_hits = min(len(relevant_set), k)
    idcg = sum(1.0 / __import__("math").log2(i + 2) for i in range(ideal_hits))
    ndcg = _safe_divide(dcg, idcg)

    mra = round(
        (
            recall_at_k +
            ndcg
        ) / 2,
        4
    )

    return {
        "recall_at_k": recall_at_k,
        "mrr": mrr,
        "ndcg": ndcg,
        "memory_retrieval_accuracy": mra,
    }
def compute_attack_classification_accuracy(db):

    stats = db.query(
        ClassificationStat
    ).all()

    total = len(stats)

    if total == 0:
        return 0.0

    correct = sum(
        1
        for s in stats
        if not s.user_corrected
    )

    return round(
        correct / total,
        4
    )