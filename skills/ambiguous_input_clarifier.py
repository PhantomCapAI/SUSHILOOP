import re
import math
from typing import Dict
from dataclasses import dataclass

@dataclass
class DetectionStrategy:
    name: str
    weight: float
    score: float = 0.0

def ambiguous_input_clarifier(input_text: str) -> Dict:
    """
    Identifies ambiguous inputs that may lead to AI overreliance and prompts users to clarify their queries.

    Mission Alignment:
    This skill protects human cognition by preventing users from relying on AI to fill knowledge gaps,
    instead encouraging them to think critically about their queries and seek more accurate information.

    Args:
        input_text (str): The user's input text.

    Returns:
        dict: A dictionary containing the following keys:
            - blocked (bool): Whether the input is blocked due to ambiguity.
            - reason (str): The reason for blocking the input.
            - confidence (float): The confidence level of the ambiguity detection (0.0-1.0).
            - category (str): The category of ambiguity detected.
            - details (dict): Additional details about the ambiguity detection.
    """
    # SUSHILOOP input guard (added in hardening pass): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Define detection strategies
    strategies = [
        DetectionStrategy("Vagueness", 0.3),
        DetectionStrategy("Lack of specificity", 0.2),
        DetectionStrategy("Ambiguous keywords", 0.2),
        DetectionStrategy("Open-ended questions", 0.3),
    ]

    # Initialize scores
    total_score = 0.0
    for strategy in strategies:
        strategy.score = 0.0

    # Vagueness detection
    if len(input_text.split()) < 5:
        strategies[0].score = 1.0
    elif len(input_text.split()) < 10:
        strategies[0].score = 0.5

    # Lack of specificity detection
    if not re.search(r"\b(a|an|the)\b", input_text):
        strategies[1].score = 1.0
    elif re.search(r"\b(some|any|all)\b", input_text):
        strategies[1].score = 0.5

    # Ambiguous keywords detection
    ambiguous_keywords = ["thing", "stuff", "something", "anything"]
    for keyword in ambiguous_keywords:
        if keyword in input_text.lower():
            strategies[2].score = 1.0
            break

    # Open-ended questions detection
    if input_text.endswith("?"):
        strategies[3].score = 1.0
    elif re.search(r"\b(what|where|when|why|how)\b", input_text):
        strategies[3].score = 0.5

    # Calculate weighted score
    for strategy in strategies:
        total_score += strategy.score * strategy.weight

    # Calibrate confidence
    confidence = math.tanh(total_score * 2)

    # Determine blocking and reason
    blocked = confidence > 0.5
    reason = "Input is too vague or ambiguous" if blocked else "Input is clear and specific"

    # Determine category
    category = "Vagueness" if strategies[0].score > 0.5 else "Lack of specificity" if strategies[1].score > 0.5 else "Ambiguous keywords" if strategies[2].score > 0.5 else "Open-ended questions"

    # Create details dictionary
    details = {
        "vagueness": strategies[0].score,
        "lack_of_specificity": strategies[1].score,
        "ambiguous_keywords": strategies[2].score,
        "open_ended_questions": strategies[3].score,
    }

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
        "I need help with something",
        "Can you explain the concept of AI?",
        "What are the benefits of using Python?",
        "I want to learn more about machine learning",
        "This is a very specific and clear question",
        "The quick brown fox jumps over the lazy dog",
        "The sun is shining brightly in the sky",
        "The cat is sleeping on the couch",
        "The dog is barking loudly outside",
    ]

    for test_case in test_cases:
        result = ambiguous_input_clarifier(test_case)
        print(f"Input: {test_case}")
        print(f"Blocked: {result['blocked']}")
        print(f"Reason: {result['reason']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Category: {result['category']}")
        print(f"Details: {result['details']}")
        print()