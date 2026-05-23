import re
import json
import math
from typing import Dict
from dataclasses import dataclass
from collections import Counter

@dataclass
class DetectionStrategy:
    name: str
    weight: float
    detect: callable

def keyword_detection(input_text: str) -> float:
    """Detects suspicious keywords in input text"""
    keywords = ["bias", "stale", "incomplete"]
    matches = sum(1 for keyword in keywords if keyword in input_text.lower())
    return matches / len(keywords)

def sentiment_analysis(input_text: str) -> float:
    """Performs basic sentiment analysis on input text"""
    positive_words = ["good", "great", "excellent"]
    negative_words = ["bad", "terrible", "awful"]
    positive_matches = sum(1 for word in positive_words if word in input_text.lower())
    negative_matches = sum(1 for word in negative_words if word in input_text.lower())
    return (positive_matches - negative_matches) / (positive_matches + negative_matches + 1)

def language_complexity(input_text: str) -> float:
    """Analyzes language complexity using average sentence length"""
    sentences = re.split(r'[.!?]', input_text)
    sentence_lengths = [len(sentence.split()) for sentence in sentences if sentence]
    return sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0

def topic_modeling(input_text: str) -> float:
    """Performs basic topic modeling using word frequency"""
    words = re.findall(r'\b\w+\b', input_text.lower())
    word_counts = Counter(words)
    most_common_words = word_counts.most_common(5)
    return sum(count for word, count in most_common_words) / len(words)

def data_drift_detector(input_text: str) -> Dict:
    """
    Detects changes in input data distribution and alerts users to potential biases.

    This function analyzes the statistical properties of the input data and returns a dictionary
    with a boolean indicating whether the input data is blocked, a reason for the blockage,
    a confidence score, a category, and additional details.

    The mission of this function is to protect human cognition by identifying potential biases
    in input data and prompting users to reassess their inputs.

    :param input_text: The input text to analyze
    :return: A dictionary with the analysis results
    """
    strategies = [
        DetectionStrategy("keyword_detection", 0.3, keyword_detection),
        DetectionStrategy("sentiment_analysis", 0.2, sentiment_analysis),
        DetectionStrategy("language_complexity", 0.2, language_complexity),
        DetectionStrategy("topic_modeling", 0.3, topic_modeling),
    ]

    scores = [strategy.detect(input_text) for strategy in strategies]
    weighted_score = sum(score * strategy.weight for score, strategy in zip(scores, strategies))

    blocked = weighted_score > 0.5
    reason = "Potential bias detected" if blocked else "No bias detected"
    confidence = weighted_score
    category = "data_drift"
    details = {"strategies": {strategy.name: score for strategy, score in zip(strategies, scores)}}

    return {"blocked": blocked, "reason": reason, "confidence": confidence, "category": category, "details": details}

if __name__ == "__main__":
    test_cases = [
        "This is a great example of unbiased text.",
        "The data is stale and incomplete, which is terrible.",
        "The language is complex and difficult to understand.",
        "The topic is well-represented by the most common words.",
        "This text contains no suspicious keywords or phrases.",
        "The sentiment of this text is overwhelmingly positive.",
        "The average sentence length is relatively short.",
        "The word frequency is evenly distributed across topics.",
    ]

    for test_case in test_cases:
        result = data_drift_detector(test_case)
        print(json.dumps(result, indent=4))