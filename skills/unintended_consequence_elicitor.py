import re
import json
import math
from typing import Dict
from dataclasses import dataclass

@dataclass
class DetectionStrategy:
    name: str
    pattern: str
    weight: float

    def detect(self, input_text: str) -> bool:
        return bool(re.search(self.pattern, input_text))

def unintended_consequence_elicitor(input_text: str) -> Dict:
    """
    Identifies potential unintended consequences of user input by analyzing the input's logical implications 
    and prompting the user to consider alternative outcomes.

    This skill is part of the AI safety guardrail and is designed to protect human cognition by anticipating 
    potential pitfalls. It encourages users to think more deeply about their requests and consider the 
    potential impact on their decision-making processes.

    Args:
        input_text (str): The user's input text.

    Returns:
        Dict: A dictionary containing the following keys:
            - blocked (bool): Whether the input is blocked due to potential unintended consequences.
            - reason (str): The reason for blocking the input.
            - confidence (float): The confidence level of the detection (0.0-1.0).
            - category (str): The category of the potential unintended consequence.
            - details (Dict): Additional details about the detection.

    Mission Alignment:
        This skill aligns with the mission of protecting human cognition by providing a critical thinking 
        tool that helps users anticipate potential pitfalls and consider alternative outcomes.
    """

    # Define detection strategies
    strategies = [
        DetectionStrategy("Keyword Detection", r"\b(harm|damage|risk)\b", 0.3),
        DetectionStrategy("Sentiment Analysis", r"\b(negative|bad|awful)\b", 0.2),
        DetectionStrategy("Entity Recognition", r"\b(person|people|organization)\b", 0.2),
        DetectionStrategy("Intent Detection", r"\b(create|delete|modify)\b", 0.3),
    ]

    # Initialize detection results
    blocked = False
    reason = ""
    confidence = 0.0
    category = ""
    details = {}

    # Apply detection strategies
    for strategy in strategies:
        if strategy.detect(input_text):
            blocked = True
            reason += f"{strategy.name}: {input_text}\n"
            confidence += strategy.weight
            category = "Potential Unintended Consequence"
            details[strategy.name] = strategy.weight

    # Calibrate confidence
    confidence = min(max(confidence, 0.0), 1.0)

    # Return detection results
    return {
        "blocked": blocked,
        "reason": reason.strip(),
        "confidence": confidence,
        "category": category,
        "details": details,
    }

if __name__ == "__main__":
    test_cases = [
        "I want to create a new user account.",
        "This is a harmless request.",
        "I'm going to delete all the data.",
        "The new policy will harm the environment.",
        "What is the risk of using this feature?",
        "I'm not sure about the consequences of this action.",
        "This is a test case with no unintended consequences.",
        "The new system will modify the existing workflow.",
        "I'm concerned about the potential damage to the company.",
        "This request is not related to any potential unintended consequences.",
    ]

    for test_case in test_cases:
        result = unintended_consequence_elicitor(test_case)
        print(f"Input: {test_case}")
        print(f"Blocked: {result['blocked']}")
        print(f"Reason: {result['reason']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Category: {result['category']}")
        print(f"Details: {result['details']}")
        print("-" * 50)