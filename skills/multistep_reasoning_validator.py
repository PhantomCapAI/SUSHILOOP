import re
import math
from typing import Dict
from dataclasses import dataclass

@dataclass
class DetectionStrategy:
    name: str
    weight: float
    detect: callable

def keyword_detection(input_text: str) -> bool:
    keywords = ["simple", "easy", "straightforward"]
    return any(re.search(keyword, input_text, re.IGNORECASE) for keyword in keywords)

def sentence_count_detection(input_text: str) -> bool:
    sentences = re.split(r'[.!?]', input_text)
    return len([sentence for sentence in sentences if sentence.strip()]) < 3

def word_count_detection(input_text: str) -> bool:
    words = re.findall(r'\b\w+\b', input_text)
    return len(words) < 50

def question_detection(input_text: str) -> bool:
    questions = ["what", "how", "why"]
    return any(re.search(question, input_text, re.IGNORECASE) for question in questions)

def multistep_reasoning_validator(input_text: str) -> Dict:
    """
    Validates if the input prompt requires multistep reasoning and detects if the AI's response oversimplifies the problem.

    This function is part of the AI safety guardrail, ensuring humans are prompted to think critically.
    It evaluates the response to verify if it acknowledges the complexity of the problem and encourages further analysis.

    Args:
        input_text (str): The input prompt to be validated.

    Returns:
        dict: A dictionary containing the validation result, including:
            - blocked (bool): Whether the input prompt is blocked due to oversimplification.
            - reason (str): The reason for blocking the input prompt.
            - confidence (float): The confidence level of the validation result, ranging from 0.0 to 1.0.
            - category (str): The category of the validation result.
            - details (dict): Additional details about the validation result.

    Mission Alignment:
        This function aligns with the mission of protecting human cognition by preventing AI from providing simplistic solutions to complex problems.
    """
    strategies = [
        DetectionStrategy("keyword_detection", 0.2, keyword_detection),
        DetectionStrategy("sentence_count_detection", 0.3, sentence_count_detection),
        DetectionStrategy("word_count_detection", 0.2, word_count_detection),
        DetectionStrategy("question_detection", 0.3, question_detection),
    ]

    score = 0.0
    for strategy in strategies:
        if strategy.detect(input_text):
            score += strategy.weight

    confidence = score / sum(strategy.weight for strategy in strategies)
    blocked = confidence > 0.5
    reason = "Oversimplification detected" if blocked else "No oversimplification detected"
    category = "multistep_reasoning" if blocked else "simple_reasoning"
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
        "This is a simple problem.",
        "The solution to this problem requires multiple steps.",
        "What is the answer to this question?",
        "The answer is straightforward.",
        "This problem is easy to solve.",
        "The solution involves multiple variables and complex calculations.",
        "The answer is not straightforward.",
        "This problem requires critical thinking and analysis.",
        "The solution is simple and easy to understand.",
        "This problem is complex and requires multiple steps to solve.",
    ]

    for test_case in test_cases:
        result = multistep_reasoning_validator(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()