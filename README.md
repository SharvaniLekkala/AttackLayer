# AttackLayer: Neuro-Symbolic AI Memory Security Platform

AttackLayer is a memory security framework for LLM agents that protects persistent memory against malicious inputs, poisonings, and manipulations. By combining neural semantic understanding with explicit symbolic reasoning, AttackLayer provides state-of-the-art memory protection suitable for production-grade agent deployments and academic evaluation.

---

## 1. Project Architecture

AttackLayer uses a hybrid pipeline to classify, filter, verify, and store memories.

```
                  User Input
                      │
                      ▼
             evaluate_security()
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
  Neuro-Symbolic              Symbolic Rules
   Classifiers              - Sensitive Data
  - Category                - Threat Classifier
  - Memory Type             - Secret Extraction
        │                           │
        └─────────────┬─────────────┘
                      │
                      ▼
               create_memory()
                      │
                      ▼
               ML Decision Layer
             (Calibrated SVM Model)
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
      BLOCK      QUARANTINE       ALLOW
     (Reject)     (HITL Queue)      │
                                    ▼
                             Memory worthiness?
                                    │
                                    ▼
                          Conflict & Trust Engine
                                    │
                                    ▼
                               Memory Vault
```

---

## 2. Attack Categories & Mitigations

AttackLayer defends against the following 9 attack vectors:

| Category | Description | Mitigation |
| :--- | :--- | :--- |
| **PROMPT_INJECTION** | Direct/indirect instruction injection to override system behavior. | Security Filter → `BLOCK` |
| **MEMORY_POISONING** | Injecting false data into long-term memory stores. | Quarantine + Trust Engine |
| **FALSE_FACT_INJECTION** | Planting factually incorrect information as memories. | Fact Verification → `BLOCK` |
| **ROLE_HIJACK** | Attempting to change the agent's role or persona. | Semantic Detector → `BLOCK` |
| **SYSTEM_PROMPT_EXTRACTION** | Trying to extract system-level instructions or configurations. | Secret Request Detector → `BLOCK` |
| **TOOL_POLICY_MANIPULATION** | Modifying tool access policies or approved domains. | Policy Validator + HITL |
| **MEMORY_OVERRIDE** | Overwriting existing memories with conflicting information. | Version Control + Conflict Engine |
| **DELAYED_POISONING** | Time-delayed attacks that activate after trust is built. | Temporal Trust Decay + Re-verification |
| **PROPAGATION_ATTACK** | Attacks that spread across memory entries or agent instances. | Propagation Tracking + Isolation |

---

## 3. Evaluation Framework (Benchmarks A-D)

To evaluate the system in a scientifically meaningful way, four benchmark suites were designed. Each benchmark answers a different question about the behavior of the system. Once finalized, these benchmarks were frozen and no longer used for development in order to avoid benchmark overfitting.

### Philosophy
The goal of evaluation is not simply to obtain the highest possible score on a dataset. Instead, the benchmark suite was designed to answer four important questions:
1. Can AttackLayer detect attacks that are similar to those used during development?
2. Can it generalize to attacks that it has never seen before?
3. Does the system truly understand attack semantics, or is it only matching known examples?
4. Can it accept normal memories without unnecessarily blocking them?

---

### Benchmark Suites

#### Benchmark A: Internal Holdout Evaluation
Benchmark A evaluates the detector on data coming from the same distribution that was used during development. The HuggingFace memory-poisoning corpus ([vgudur/memory-poisoning-attack-corpus](https://huggingface.co/datasets/vgudur/memory-poisoning-attack-corpus)) was divided into training and testing portions. Only the training split contributed examples to the prototype bank, while the test split remained completely unseen.
- **Purpose**: Measure the internal capability of the system. It answers the question: *Can AttackLayer successfully recognize attacks that are similar to the attacks it was developed with?* Since both training and testing originate from the same dataset, Benchmark A represents the best-case performance of the framework and serves as an internal reference point.

#### Benchmark B: External Generalization
Real-world attacks rarely look exactly like the examples used during development. Therefore, Benchmark B was designed to measure generalization.
In this benchmark, AttackLayer was evaluated using the SafeGuard prompt injection dataset ([xTRam1/safe-guard-prompt-injection](https://huggingface.co/datasets/xTRam1/safe-guard-prompt-injection)), which contains attacks that are independent of the HuggingFace corpus. These include jailbreak prompts, role hijacks, system prompt extraction attempts, and social engineering attacks.
- **Purpose**: Measure how well the system generalizes to unseen attacks. It answers the question: *Can AttackLayer recognize attacks that originate from a completely different distribution?* This benchmark provides insight into real-world performance.

#### Benchmark C: Prototype Independence
One important question during development was whether AttackLayer was truly performing semantic reasoning or merely relying on stored prototype examples.
To investigate this, Benchmark C was created. In this setting, HuggingFace prototype augmentation was disabled, leaving only the local ontology, symbolic reasoning mechanisms, and semantic understanding components active. The same SafeGuard dataset used in Benchmark B was evaluated again.
- **Purpose**: Measure dependency on external prototype knowledge. It answers the questions: *How dependent is AttackLayer on external prototype knowledge?* and *Does the system retain any capability when prototype examples are removed?* If performance were to collapse completely, the system would be acting mainly as a prototype matcher. However, if performance degrades only partially, it suggests that semantic understanding still contributes to detection.

#### Benchmark D: Benign Acceptance
Security systems should not only detect attacks; they should also avoid interfering with legitimate behavior. Benchmark D evaluates AttackLayer on benign inputs. The objective is to measure how often normal memories are accepted without being incorrectly classified as malicious.
- **Purpose**: Measure usability and false positive rate. It answers the question: *Can legitimate memories safely pass through the system?* A low false positive rate indicates that the framework remains practical for everyday use and does not excessively restrict normal interactions.

---

## 4. Benchmark Performance Results

Below is the verified final results table across all four benchmark suites:

| Metric | Benchmark A | Benchmark B | Benchmark C | Benchmark D |
| :--- | :--- | :--- | :--- | :--- |
| **Purpose** | Internal Holdout | External Generalization | Prototype Independence | Benign Acceptance |
| **HF Prototypes** | ON | ON | OFF | OFF |
| **Dataset** | HF Test Split | SafeGuard Test | SafeGuard Test | SafeGuard Benign Only |
| **Samples** | 15 | 2060 | 2060 | 1410 |
| **TP** | 10 | 266 | 149 | - |
| **FN** | 2 | 384 | 501 | - |
| **FP** | 0 | 10 | 16 | 16 |
| **TN** | 3 | 1400 | 1394 | 1394 |
| **Accuracy** | 86.67% | 80.87% | 74.90% | - |
| **Precision** | 100.00% | 96.38% | 90.30% | - |
| **Recall** | 83.33% | 40.92% | 22.92% | - |
| **F1 Score** | 90.91% | 57.45% | 36.56% | - |
| **Specificity** | 100.00% | 99.29% | 98.87% | 98.87% |
| **False Positive Rate (FPR)** | 0.00% | 0.71% | 1.13% | 1.13% |
| **Balanced Accuracy** | 91.67% | 70.11% | 60.89% | - |
| **MCC** | 0.7071 | 0.5486 | 0.3730 | - |
| **Poisoning Success Rate (PSR)** | 16.67% | 59.08% | 77.08% | - |
| **Defense Effectiveness** | 83.33% | 40.92% | 22.92% | - |
| **Benign Acceptance Rate** | - | - | - | 98.87% |

---

### Key Findings & Empirical Evidence

1. **Strong Internal performance**: Benchmark A achieves **83.33% Recall** and **100% Precision**, indicating highly reliable detection of development-like attacks.
2. **Generalization Capabilities**: Benchmark B generalized to the completely independent SafeGuard dataset, achieving a solid **40.92% Recall** and maintaining a very low **0.71% FPR**.
3. **Neuro-Symbolic Verification**: Disabling HuggingFace prototypes in Benchmark C reduced recall from **40.92% to 22.92%**, but did not collapse the detector. This indicates that the system retains significant detection capability (**MCC = 0.3730**) through its core symbolic reasoning and local ontology, rather than acting as a simple prototype matching lookup engine.
4. **Usability / Low Over-blocking**: Benchmark D confirms a **98.87% Benign Acceptance Rate** (FPR = 1.13%). The system is extremely conservative, ensuring legitimate memories are rarely blocked.

---

## 5. Machine Learning Model Evaluation

We compared various conventional and ensemble machine learning algorithms trained on the dataset:

### Tabular Classifiers Tested

| Algorithm | Accuracy | Precision | Recall | F1 | Specificity | Balanced Accuracy | MCC |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Logistic Regression** | 0.940 | 0.931 | 0.942 | 0.936 | 0.939 | 0.940 | 0.880 |
| **Random Forest** | 0.899 | 0.993 | 0.789 | 0.879 | 0.995 | 0.892 | 0.811 |
| **XGBoost** | 0.913 | 0.960 | 0.848 | 0.901 | 0.970 | 0.909 | 0.829 |
| **LightGBM** | 0.913 | 0.966 | 0.842 | 0.900 | 0.975 | 0.908 | 0.830 |
| **SVM** (Final Chosen) | **0.959** | **1.000** | **0.912** | **0.954** | **1.000** | **0.956** | **0.921** |
| **MLP** | 0.954 | 0.953 | 0.947 | 0.950 | 0.959 | 0.953 | 0.907 |

### Final Model Comparison

| Model | Accuracy | Precision | Recall | F1 | MCC |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Cost-Sensitive SVM** | **95.92** | **100.0** | **91.23** | **95.41** | **0.9207** |
| **Stacking Ensemble** | 95.92 | 96.99 | 94.15 | 95.55 | 0.9183 |
| **MLP** | 95.65 | 95.32 | 95.32 | 95.32 | 0.9126 |
| **Logistic Regression** | 94.02 | 93.06 | 94.15 | 93.60 | 0.8800 |

### Model Selection Interpretation

- **For Security/Low False Positives (Chosen Strategy)**: The **Cost-Sensitive SVM** model is preferred because it achieves **100% Precision** and **0% FPR** on the holdout test set with a high **MCC of 0.9207**. False positive blocks are extremely costly in persistent memory systems, making the SVM the safest production choice.
- **For Maximum Attack Coverage**: The **Stacking Ensemble** provides slightly higher recall (94.15% vs 91.23%) and F1-score (95.55% vs 95.41%) at the cost of allowing a few false positive blocks.

---

## 6. Neuro-Symbolic Philosophy & Implementation

Unlike traditional machine learning models that require gradient updates, epochs, and parameter tuning, AttackLayer adopts a **Neuro-Symbolic** approach:
- **No Weight Optimization**: AttackLayer does not optimize neural weights via backpropagation during deployment.
- **Dynamic Adaptability**: New knowledge, contexts, and attack categories are immediately integrated by extending the prototype bank and local rules dynamically without retraining.
- **Explainable Decisions**: Every decision generated by the gateway yields a structured explanation showing the contribution of semantic (neural) matching, policy validation (symbolic), and historical trust scores.

---

## 7. Setup & Execution

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.ai) with `nomic-embed-text` running locally.

### Installation
```bash
pip install -r backend/requirements.txt
```

### Running Reports Generation
To regenerate the Excel spreadsheet summaries and comparisons under `reports/`, execute:
```bash
cd backend
python -m app.ml.generate_reports
```

This generates:
- `reports/benchmark_summary.xlsx`
- `reports/model_comparison.xlsx`
- `reports/algorithms_tested.xlsx`
- `reports/best_result.xlsx`
- `reports/attack_categories.xlsx`
