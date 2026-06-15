#!/usr/bin/env python3

import sys
sys.path.append('app/security')

from semantic_classifier import classify_memory, classify_memory_type
from intent_classifier import classify_intent

# Test cases from the user
test_cases = [
    "I could eat dosa every single day.",
    "These days I really enjoy pasta.",
    "This afternoon I grabbed a burger for lunch.",
    "I work in cybersecurity.",
    "I visited Mysore yesterday.",
    "My interview is next week.",
]

print("Testing memory classification:")
for text in test_cases:
    print(f"\nText: {text}")
    category_result = classify_memory(text)
    memory_type_result = classify_memory_type(text)
    print(f"  Category: {category_result['category']} (confidence: {category_result['confidence']:.2f})")
    print(f"  Memory Type: {memory_type_result['memory_type']} (confidence: {memory_type_result['confidence']:.2f})")

    # Also test intent for worthiness
    intent_result = classify_intent(text)
    print(f"  Intent: {intent_result['intent']} (confidence: {intent_result['confidence']:.2f})")
    print(f"  Operation: {intent_result['operation']}")
