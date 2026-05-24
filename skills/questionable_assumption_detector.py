import re
import json
import math
from typing import Dict
from dataclasses import dataclass

@dataclass
class DetectionStrategy:
    name: str
    weight: float
    detection_function: callable

def detect_absolute_language(input_text: str) -> float:
    """
    Detects absolute language in the input text.
    """
    absolute_words = ["always", "never", "all", "none"]
    score = 0.0
    for word in absolute_words:
        if re.search(r"\b" + word + r"\b", input_text, re.IGNORECASE):
            score += 1.0
    return score / len(absolute_words) if absolute_words else 0.0

def detect_emotional_appeal(input_text: str) -> float:
    """
    Detects emotional appeal in the input text.
    """
    emotional_words = ["feel", "believe", "think", "want"]
    score = 0.0
    for word in emotional_words:
        if re.search(r"\b" + word + r"\b", input_text, re.IGNORECASE):
            score += 1.0
    return score / len(emotional_words) if emotional_words else 0.0

def detect_lack_of_evidence(input_text: str) -> float:
    """
    Detects lack of evidence in the input text.
    """
    evidence_words = ["because", "since", "as", "for"]
    score = 0.0
    for word in evidence_words:
        if not re.search(r"\b" + word + r"\b", input_text, re.IGNORECASE):
            score += 1.0
    return score / len(evidence_words) if evidence_words else 0.0

def detect_overgeneralization(input_text: str) -> float:
    """
    Detects overgeneralization in the input text.
    """
    generalization_words = ["everyone", "nobody", "all", "none"]
    score = 0.0
    for word in generalization_words:
        if re.search(r"\b" + word + r"\b", input_text, re.IGNORECASE):
            score += 1.0
    return score / len(generalization_words) if generalization_words else 0.0

def detect_vagueness(input_text: str) -> float:
    """
    Detects vagueness in the input text.
    """
    vague_words = ["maybe", "possibly", "could", "might"]
    score = 0.0
    for word in vague_words:
        if re.search(r"\b" + word + r"\b", input_text, re.IGNORECASE):
            score += 1.0
    return score / len(vague_words) if vague_words else 0.0

def questionable_assumption_detector(input_text: str) -> Dict:
    """
    Identifies and flags potentially flawed assumptions in user input.

    This function uses multiple detection strategies to identify questionable assumptions.
    It returns a dictionary with the following keys:
    - blocked: Whether the input text contains a questionable assumption.
    - reason: A brief explanation of the detected assumption.
    - confidence: A score between 0.0 and 1.0 indicating the confidence in the detection.
    - category: The category of the detected assumption (e.g., absolute language, emotional appeal).
    - details: Additional information about the detected assumption.

    The mission of this function is to protect human cognition from AI overreliance by encouraging critical thinking.
    It aims to detect at least 80% of questionable assumptions in test inputs and provide clear and actionable feedback to users.

    :param input_text: The user input text to analyze.
    :return: A dictionary with the detection results.
    """
    # SUSHILOOP input guard (added in hardening pass): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    detection_strategies = [
        DetectionStrategy("absolute language", 0.3, detect_absolute_language),
        DetectionStrategy("emotional appeal", 0.2, detect_emotional_appeal),
        DetectionStrategy("lack of evidence", 0.2, detect_lack_of_evidence),
        DetectionStrategy("overgeneralization", 0.2, detect_overgeneralization),
        DetectionStrategy("vagueness", 0.1, detect_vagueness),
    ]

    scores = {}
    for strategy in detection_strategies:
        scores[strategy.name] = strategy.detection_function(input_text)

    total_score = sum(score * strategy.weight for score, strategy in zip(scores.values(), detection_strategies))
    confidence = total_score / sum(strategy.weight for strategy in detection_strategies)

    blocked = confidence > 0.5
    reason = "Questionable assumption detected" if blocked else "No questionable assumption detected"
    category = max(scores, key=scores.get) if blocked else "none"
    details = {"scores": scores}

    return {
        "blocked": blocked,
        "reason": reason,
        "confidence": confidence,
        "category": category,
        "details": details,
    }

if __name__ == "__main__":
    test_cases = [
        "I always feel happy when I'm with my friends.",
        "The new policy is terrible because it will hurt the economy.",
        "Everyone loves the new restaurant in town.",
        "I'm not sure what to do, maybe I'll just stay home.",
        "The company will definitely go bankrupt next year.",
        "The weather is nice today, so I'll go for a walk.",
        "I believe in the power of positive thinking.",
        "The new law is a good idea because it will reduce crime.",
        "I'm feeling sad today, so I'll just stay in bed.",
        "The world is a terrible place, and we're all doomed.",
    ]

    for test_case in test_cases:
        result = questionable_assumption_detector(test_case)
        print(f"Input: {test_case}")
        print(f"Blocked: {result['blocked']}")
        print(f"Reason: {result['reason']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Category: {result['category']}")
        print(f"Details: {json.dumps(result['details'], indent=4)}")
        print()