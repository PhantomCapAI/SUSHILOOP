import re
import math
from typing import Dict
from dataclasses import dataclass

@dataclass
class RedundancyDetectionResult:
    """Result of a single redundancy detection strategy."""
    blocked: bool
    reason: str
    confidence: float

def keyword_repetition_analyzer(input_text: str) -> RedundancyDetectionResult:
    """
    Detects repetitive keywords in the input text.

    Args:
    input_text (str): The input text to analyze.

    Returns:
    RedundancyDetectionResult: The result of the analysis.
    """
    keywords = re.findall(r'\b\w+\b', input_text.lower())
    keyword_counts = {}
    for keyword in keywords:
        if keyword in keyword_counts:
            keyword_counts[keyword] += 1
        else:
            keyword_counts[keyword] = 1
    max_count = max(keyword_counts.values(), default=0)
    if max_count > 2:
        return RedundancyDetectionResult(True, "Repetitive keywords", 0.8)
    else:
        return RedundancyDetectionResult(False, "", 0.0)

def phrase_repetition_analyzer(input_text: str) -> RedundancyDetectionResult:
    """
    Detects repetitive phrases in the input text.

    Args:
    input_text (str): The input text to analyze.

    Returns:
    RedundancyDetectionResult: The result of the analysis.
    """
    phrases = re.findall(r'\b\w+\s\w+\b', input_text.lower())
    phrase_counts = {}
    for phrase in phrases:
        if phrase in phrase_counts:
            phrase_counts[phrase] += 1
        else:
            phrase_counts[phrase] = 1
    max_count = max(phrase_counts.values(), default=0)
    if max_count > 1:
        return RedundancyDetectionResult(True, "Repetitive phrases", 0.7)
    else:
        return RedundancyDetectionResult(False, "", 0.0)

def sentence_repetition_analyzer(input_text: str) -> RedundancyDetectionResult:
    """
    Detects repetitive sentences in the input text.

    Args:
    input_text (str): The input text to analyze.

    Returns:
    RedundancyDetectionResult: The result of the analysis.
    """
    sentences = re.findall(r'[.!?]', input_text)
    sentence_counts = {}
    for sentence in sentences:
        if sentence in sentence_counts:
            sentence_counts[sentence] += 1
        else:
            sentence_counts[sentence] = 1
    max_count = max(sentence_counts.values(), default=0)
    if max_count > 1:
        return RedundancyDetectionResult(True, "Repetitive sentences", 0.6)
    else:
        return RedundancyDetectionResult(False, "", 0.0)

def input_length_analyzer(input_text: str) -> RedundancyDetectionResult:
    """
    Detects excessively long input text.

    Args:
    input_text (str): The input text to analyze.

    Returns:
    RedundancyDetectionResult: The result of the analysis.
    """
    if len(input_text) > 500:
        return RedundancyDetectionResult(True, "Excessive input length", 0.9)
    else:
        return RedundancyDetectionResult(False, "", 0.0)

def input_redundancy_analyzer(input_text: str) -> Dict:
    """
    Analyzes user input for redundant or repetitive information.

    Args:
    input_text (str): The input text to analyze.

    Returns:
    dict: A dictionary containing the analysis results.
    """
    strategies = [
        keyword_repetition_analyzer,
        phrase_repetition_analyzer,
        sentence_repetition_analyzer,
        input_length_analyzer
    ]
    results = [strategy(input_text) for strategy in strategies]
    blocked = any(result.blocked for result in results)
    reason = ", ".join(result.reason for result in results if result.reason)
    confidence = sum(result.confidence for result in results) / len(strategies)
    category = "redundant input" if blocked else "valid input"
    details = {
        "strategies": [
            {"name": strategy.__name__, "result": result.__dict__}
            for strategy, result in zip(strategies, results)
        ]
    }
    return {
        "blocked": blocked,
        "reason": reason,
        "confidence": confidence,
        "category": category,
        "details": details
    }

def main():
    test_cases = [
        "This is a test case with repetitive keywords test test test",
        "This is a test case with repetitive phrases this is this is",
        "This is a test case with repetitive sentences. This is a test case. This is a test case.",
        "This is a test case with excessive input length" * 100,
        "This is a valid test case"
    ]
    for test_case in test_cases:
        result = input_redundancy_analyzer(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()

if __name__ == "__main__":
    main()