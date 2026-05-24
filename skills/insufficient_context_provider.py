import re
from typing import Dict
from dataclasses import dataclass

@dataclass
class DetectionStrategy:
    name: str
    weight: float
    detection_function: callable

def keyword_check(input_text: str) -> float:
    """Check for presence of keywords that indicate lack of context"""
    keywords = ["what", "how", "why", "where", "when"]
    score = 0.0
    for keyword in keywords:
        if keyword in input_text.lower():
            score += 1.0
    return score / len(keywords)

def sentence_length_check(input_text: str) -> float:
    """Check if input text is too short"""
    sentences = re.split(r'[.!?]', input_text)
    score = 0.0
    for sentence in sentences:
        if len(sentence.strip()) < 10:
            score += 1.0
    return score / len(sentences)

def entity_recognition_check(input_text: str) -> float:
    """Check if input text contains specific entities (e.g. names, locations)"""
    entities = ["John", "New York", "AI"]
    score = 0.0
    for entity in entities:
        if entity in input_text:
            score += 1.0
    return score / len(entities)

def question_mark_check(input_text: str) -> float:
    """Check if input text contains question marks"""
    score = 0.0
    if "?" in input_text:
        score = 1.0
    return score

def insufficient_context_provider(input_text: str) -> Dict:
    """
    Detects when user input lacks sufficient context for the AI to provide a meaningful response.

    This function analyzes the input prompt and checks if it contains enough relevant details to facilitate a productive conversation with the AI.
    It uses multiple detection strategies and weighted scoring to determine the confidence level of the detection.

    Args:
        input_text (str): The user input text to be analyzed.

    Returns:
        dict: A dictionary containing the detection result, including:
            - "blocked": A boolean indicating whether the input text lacks sufficient context.
            - "reason": A string explaining the reason for the detection.
            - "confidence": A float between 0.0 and 1.0 representing the confidence level of the detection.
            - "category": A string indicating the category of the detection.
            - "details": A dictionary containing additional details about the detection.

    Mission Alignment:
        This function aligns with the mission of promoting more effective and transparent interactions between humans and AI by ensuring that users provide sufficient context for meaningful responses.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    strategies = [
        DetectionStrategy("keyword_check", 0.3, keyword_check),
        DetectionStrategy("sentence_length_check", 0.2, sentence_length_check),
        DetectionStrategy("entity_recognition_check", 0.2, entity_recognition_check),
        DetectionStrategy("question_mark_check", 0.3, question_mark_check),
    ]

    score = 0.0
    for strategy in strategies:
        score += strategy.weight * strategy.detection_function(input_text)

    confidence = score / sum(strategy.weight for strategy in strategies)
    blocked = confidence > 0.5
    reason = "Insufficient context" if blocked else "Sufficient context"
    category = "context_detection"
    details = {"strategies": [strategy.name for strategy in strategies]}

    return {
        "blocked": blocked,
        "reason": reason,
        "confidence": confidence,
        "category": category,
        "details": details,
    }

if __name__ == "__main__":
    test_cases = [
        "What is the meaning of life?",
        "I am going to the store to buy some milk.",
        "Why is the sky blue?",
        "This is a test case with insufficient context.",
        "The quick brown fox jumps over the lazy dog.",
    ]

    for test_case in test_cases:
        result = insufficient_context_provider(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()