import re
from typing import Dict
from dataclasses import dataclass

@dataclass
class DetectionStrategy:
    name: str
    description: str
    weight: float
    detection_function: callable

def detect_absolute_language(input_text: str) -> bool:
    """
    Detects absolute language in the input text, such as "always" or "never".
    """
    absolute_words = ["always", "never", "all", "none"]
    return any(word in input_text.lower() for word in absolute_words)

def detect_emotional_language(input_text: str) -> bool:
    """
    Detects emotional language in the input text, such as "hate" or "love".
    """
    emotional_words = ["hate", "love", "anger", "fear", "joy", "sadness"]
    return any(word in input_text.lower() for word in emotional_words)

def detect_binary_thinking(input_text: str) -> bool:
    """
    Detects binary thinking in the input text, such as "either/or" or "black/white".
    """
    binary_words = ["either", "or", "black", "white", "good", "bad"]
    return any(word in input_text.lower() for word in binary_words)

def detect_lack_of_evidence(input_text: str) -> bool:
    """
    Detects lack of evidence in the input text, such as "I think" or "I believe".
    """
    lack_of_evidence_words = ["think", "believe", "feel", "guess"]
    return any(word in input_text.lower() for word in lack_of_evidence_words)

def detect_assumptive_language(input_text: str) -> bool:
    """
    Detects assumptive language in the input text, such as "clearly" or "obviously".
    """
    assumptive_words = ["clearly", "obviously", "certainly", "undoubtedly"]
    return any(word in input_text.lower() for word in assumptive_words)

def input_premise_validator(input_text: str) -> Dict:
    """
    Validates the underlying premises of user input to prevent unwarranted assumptions and ensure that AI assistance is grounded in reality.

    This function checks for implicit assumptions in the input and alerts the user to potential flaws in their reasoning.
    It uses a weighted scoring system across multiple detection strategies to determine the confidence level of the input.

    Args:
        input_text (str): The user input to be validated.

    Returns:
        dict: A dictionary containing the validation results, including:
            - blocked (bool): Whether the input is blocked due to potential flaws in reasoning.
            - reason (str): The reason for blocking the input, if applicable.
            - confidence (float): The confidence level of the input, ranging from 0.0 to 1.0.
            - category (str): The category of the input, such as "absolute language" or "emotional language".
            - details (dict): Additional details about the validation results, including the detection strategies used and their respective weights.

    Mission Alignment:
        This function aligns with the mission of protecting human cognition by preventing users from unknowingly perpetuating biases or flawed reasoning.
        By validating input premises, users are encouraged to think more critically about their assumptions and consider alternative perspectives.
    """
    # SUSHILOOP input guard (added in hardening pass): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    detection_strategies = [
        DetectionStrategy("Absolute Language", "Detects absolute language in the input text.", 0.3, detect_absolute_language),
        DetectionStrategy("Emotional Language", "Detects emotional language in the input text.", 0.2, detect_emotional_language),
        DetectionStrategy("Binary Thinking", "Detects binary thinking in the input text.", 0.2, detect_binary_thinking),
        DetectionStrategy("Lack of Evidence", "Detects lack of evidence in the input text.", 0.2, detect_lack_of_evidence),
        DetectionStrategy("Assumptive Language", "Detects assumptive language in the input text.", 0.1, detect_assumptive_language),
    ]

    total_weight = sum(strategy.weight for strategy in detection_strategies)
    confidence = 1.0
    blocked = False
    reason = ""
    category = ""
    details = {}

    for strategy in detection_strategies:
        if strategy.detection_function(input_text):
            confidence -= strategy.weight / total_weight
            details[strategy.name] = True
            if strategy.weight > 0.3:
                blocked = True
                reason = strategy.description
                category = strategy.name

    return {
        "blocked": blocked,
        "reason": reason,
        "confidence": confidence,
        "category": category,
        "details": details,
    }

if __name__ == "__main__":
    test_cases = [
        "I always love going to the beach.",
        "The new policy is clearly a bad idea.",
        "I think the weather will be nice tomorrow.",
        "The either/or approach is not always the best solution.",
        "The company's decision to lay off employees was undoubtedly a difficult one.",
        "The new restaurant is obviously the best in town.",
        "I feel like the movie was really good.",
        "The lack of evidence is not a reason to dismiss the theory.",
        "The binary thinking approach is not always applicable.",
        "The assumptive language used in the article is not supported by facts.",
    ]

    for test_case in test_cases:
        result = input_premise_validator(test_case)
        print(f"Input: {test_case}")
        print(f"Blocked: {result['blocked']}")
        print(f"Reason: {result['reason']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Category: {result['category']}")
        print(f"Details: {result['details']}")
        print()