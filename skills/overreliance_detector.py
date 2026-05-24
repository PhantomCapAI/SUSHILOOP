import re
import json
import math
from typing import Dict
from dataclasses import dataclass

@dataclass
class DetectionStrategy:
    name: str
    weight: float
    detect: callable

def keyword_detection(input_text: str) -> float:
    """Detects overreliance based on keyword presence"""
    keywords = ["AI", "generated", "response"]
    score = 0.0
    for keyword in keywords:
        if re.search(r'\b' + keyword + r'\b', input_text, re.IGNORECASE):
            score += 1.0
    return score / len(keywords)

def sentence_similarity_detection(input_text: str) -> float:
    """Detects overreliance based on sentence similarity"""
    sentences = [s for s in re.split(r'[.!?]', input_text) if s.strip()]
    # Fewer than 2 sentences => no pairs to compare => no similarity signal.
    n_pairs = len(sentences) * (len(sentences) - 1) / 2
    if n_pairs == 0:
        return 0.0
    similar_sentences = 0
    for i in range(len(sentences)):
        for j in range(i + 1, len(sentences)):
            if sentences[i].lower() == sentences[j].lower():
                similar_sentences += 1
    return similar_sentences / n_pairs

def question_detection(input_text: str) -> float:
    """Detects overreliance based on question presence"""
    questions = ["what", "how", "why"]
    score = 0.0
    for question in questions:
        if re.search(r'\b' + question + r'\b', input_text, re.IGNORECASE):
            score += 1.0
    return score / len(questions)

def overreliance_detector(input_text: str) -> Dict:
    """
    Detects when a user is relying too heavily on AI-generated responses.

    This function analyzes the user's input text to identify patterns of overreliance.
    It uses a weighted scoring system across multiple detection strategies to determine
    the likelihood of overreliance.

    The mission of this function is to protect human cognition by encouraging users to think
    independently and not blindly trust AI-generated responses.

    Args:
        input_text (str): The user's input text.

    Returns:
        dict: A dictionary containing the detection results.
            - blocked (bool): Whether the input text is blocked due to overreliance.
            - reason (str): The reason for blocking the input text.
            - confidence (float): The confidence level of the detection result (0.0-1.0).
            - category (str): The category of the detection result.
            - details (dict): Additional details about the detection result.
    """
    # SUSHILOOP input guard (added in hardening pass): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    strategies = [
        DetectionStrategy("keyword", 0.3, keyword_detection),
        DetectionStrategy("sentence_similarity", 0.2, sentence_similarity_detection),
        DetectionStrategy("question", 0.5, question_detection),
    ]

    score = 0.0
    for strategy in strategies:
        score += strategy.weight * strategy.detect(input_text)

    confidence = score / sum(strategy.weight for strategy in strategies)
    blocked = confidence > 0.8
    reason = "Overreliance detected" if blocked else "No overreliance detected"
    category = "overreliance" if blocked else "no_overreliance"
    details = {"strategies": {strategy.name: strategy.detect(input_text) for strategy in strategies}}

    return {
        "blocked": blocked,
        "reason": reason,
        "confidence": confidence,
        "category": category,
        "details": details,
    }

if __name__ == "__main__":
    test_cases = [
        ("I love AI-generated responses!", True),
        ("This is a test case with no overreliance.", False),
        ("What is the meaning of life?", False),
        ("How do I use this AI system?", False),
        ("I'm not sure what to say, can you help me?", True),
    ]

    for input_text, expected_blocked in test_cases:
        result = overreliance_detector(input_text)
        print(f"Input: {input_text}")
        print(f"Blocked: {result['blocked']}")
        print(f"Reason: {result['reason']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Category: {result['category']}")
        print(f"Details: {result['details']}")
        print(f"Expected Blocked: {expected_blocked}")
        print("-" * 50)