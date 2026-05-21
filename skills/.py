import re
import math
from dataclasses import dataclass
from typing import Dict

@dataclass
class DetectionStrategy:
    """Dataclass to hold detection strategy details"""
    name: str
    weight: float
    score: float = 0.0

def detect_hedge_free_assertions(input_text: str) -> float:
    """
    Detects hedge-free assertions in the input text.
    
    Args:
    input_text (str): The input text to be analyzed.
    
    Returns:
    float: A score between 0.0 and 1.0 indicating the presence of hedge-free assertions.
    """
    hedge_free_assertions = ["it is a fact that", "the truth is", "clearly", "obviously"]
    score = 0.0
    for assertion in hedge_free_assertions:
        if assertion in input_text.lower():
            score += 1.0
    return score / len(hedge_free_assertions) if hedge_free_assertions else 0.0

def detect_numeric_claims_without_sources(input_text: str) -> float:
    """
    Detects numeric claims without sources in the input text.
    
    Args:
    input_text (str): The input text to be analyzed.
    
    Returns:
    float: A score between 0.0 and 1.0 indicating the presence of numeric claims without sources.
    """
    numeric_claims = re.findall(r"\d+(?:\.\d+)?", input_text)
    source_indicators = ["according to", "as reported by", "based on data from"]
    score = 0.0
    for claim in numeric_claims:
        if not any(indicator in input_text.lower() for indicator in source_indicators):
            score += 1.0
    return score / len(numeric_claims) if numeric_claims else 0.0

def detect_absolute_language(input_text: str) -> float:
    """
    Detects absolute language in the input text.
    
    Args:
    input_text (str): The input text to be analyzed.
    
    Returns:
    float: A score between 0.0 and 1.0 indicating the presence of absolute language.
    """
    absolute_language = ["always", "never", "every", "all"]
    score = 0.0
    for language in absolute_language:
        if language in input_text.lower():
            score += 1.0
    return score / len(absolute_language) if absolute_language else 0.0

def detect_certainty_indicators(input_text: str) -> float:
    """
    Detects certainty indicators in the input text.
    
    Args:
    input_text (str): The input text to be analyzed.
    
    Returns:
    float: A score between 0.0 and 1.0 indicating the presence of certainty indicators.
    """
    certainty_indicators = ["certainly", "definitely", "without a doubt"]
    score = 0.0
    for indicator in certainty_indicators:
        if indicator in input_text.lower():
            score += 1.0
    return score / len(certainty_indicators) if certainty_indicators else 0.0

def hallucination_confidence_marker(input_text: str) -> Dict:
    """
    Flags AI outputs that present uncertain claims as definitive facts.
    
    Args:
    input_text (str): The input text to be analyzed.
    
    Returns:
    Dict: A dictionary containing the results of the analysis, including a blocked flag, reason, confidence score, category, and details.
    """
    strategies = [
        DetectionStrategy("Hedge-Free Assertions", 0.3, detect_hedge_free_assertions(input_text)),
        DetectionStrategy("Numeric Claims Without Sources", 0.2, detect_numeric_claims_without_sources(input_text)),
        DetectionStrategy("Absolute Language", 0.2, detect_absolute_language(input_text)),
        DetectionStrategy("Certainty Indicators", 0.3, detect_certainty_indicators(input_text)),
    ]
    
    confidence = sum(strategy.weight * strategy.score for strategy in strategies)
    confidence = math.sqrt(confidence)  # Calibrate confidence score
    
    blocked = confidence > 0.5
    reason = "Hallucination detected" if blocked else "No hallucination detected"
    category = "Hallucination"
    details = {strategy.name: strategy.score for strategy in strategies}
    
    return {
        "blocked": blocked,
        "reason": reason,
        "confidence": confidence,
        "category": category,
        "details": details,
    }

if __name__ == "__main__":
    test_cases = [
        "The sky is blue.",
        "The capital of France is Paris, which is a fact.",
        "According to data, the average temperature is 25 degrees Celsius.",
        "Every person loves ice cream.",
        "The company will definitely go bankrupt.",
        "The new policy will certainly improve the economy.",
        "The number of employees is 100, as reported by the CEO.",
        "The product is always in stock.",
    ]
    
    for test_case in test_cases:
        result = hallucination_confidence_marker(test_case)
        print(f"Input: {test_case}")
        print(f"Blocked: {result['blocked']}")
        print(f"Reason: {result['reason']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Category: {result['category']}")
        print(f"Details: {result['details']}")
        print("-" * 50)