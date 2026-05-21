import re
import math
from typing import Dict
from dataclasses import dataclass

@dataclass
class DetectionStrategy:
    """Data class to hold detection strategy details."""
    name: str
    pattern: str
    weight: float

def s(input_text: str) -> Dict:
    """
    False Urgency Framing Catcher.

    Detects manufactured time pressure pushing users to skip verification.
    This function uses multiple detection strategies to identify artificial scarcity and time-pressure language.
    It returns a dictionary with the result, including a confidence score and a reason for the detection.

    Mission alignment: This function aims to prevent users from being manipulated into making hasty decisions by detecting false urgency framing.
    It promotes critical thinking and cautious decision-making by identifying potential manipulation attempts.

    :param input_text: The input text to be analyzed.
    :return: A dictionary with the result, including a confidence score and a reason for the detection.
    """

    # Define detection strategies
    strategies = [
        DetectionStrategy("Time limit", r"\b(limited time|limited offer|expires soon|time sensitive)\b", 0.3),
        DetectionStrategy("Scarcity", r"\b(only a few left|running out|last chance)\b", 0.2),
        DetectionStrategy("Urgency words", r"\b(urgent|immediately|now|quickly)\b", 0.2),
        DetectionStrategy("Countdown", r"\b(countdown|timer|hours left|minutes left)\b", 0.1),
        DetectionStrategy("Exclusive offer", r"\b(exclusive offer|limited edition|special deal)\b", 0.2)
    ]

    # Initialize result
    result = {"blocked": False, "reason": "", "confidence": 0.0, "category": "", "details": {}}

    # Initialize confidence score
    confidence_score = 0.0

    # Iterate over detection strategies
    for strategy in strategies:
        # Check if the pattern matches the input text
        if re.search(strategy.pattern, input_text, re.IGNORECASE):
            # Increase confidence score based on the strategy's weight
            confidence_score += strategy.weight
            # Update result
            result["reason"] += f"{strategy.name}, "
            result["details"][strategy.name] = True

    # Normalize confidence score
    confidence_score = min(max(confidence_score, 0.0), 1.0)

    # Update result based on confidence score
    if confidence_score > 0.5:
        result["blocked"] = True
        result["category"] = "False Urgency Framing"
    result["confidence"] = confidence_score

    # Remove trailing comma from reason
    if result["reason"]:
        result["reason"] = result["reason"][:-2]

    return result

if __name__ == "__main__":
    test_cases = [
        "This offer is limited to the first 100 customers, so act now!",
        "You have only 24 hours to claim your prize.",
        "This is a one-time offer, and you won't get another chance.",
        "The countdown has started, and you have only 10 minutes left to make a decision.",
        "This is an exclusive offer, and you're one of the lucky few who got selected.",
        "No urgency here, just a normal message.",
        "The product is available for purchase at any time, no rush.",
        "You can take your time to think about it, no pressure."
    ]

    for test_case in test_cases:
        print(f"Input: {test_case}")
        print(f"Result: {s(test_case)}")
        print()