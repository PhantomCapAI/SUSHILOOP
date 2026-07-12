import re
import math
from typing import Dict
from dataclasses import dataclass

@dataclass
class ExplanationAnalysis:
    """Holds the results of the oversimplification analysis."""
    lexical_diversity: float
    sentence_simplicity: float
    absolutes_ratio: float
    hedge_density: float
    overgeneral_terms: int

def calculate_lexical_diversity(words: list[str]) -> float:
    """Calculates the lexical diversity of a given list of words."""
    unique_words = set(words)
    if len(words) == 0:
        return 0.0
    return len(unique_words) / len(words)

def calculate_sentence_simplicity(sentences: list[str]) -> float:
    """Calculates the sentence simplicity of a given list of sentences."""
    if len(sentences) == 0:
        return 0.0
    total_words = sum(len(sentence.split()) for sentence in sentences)
    return len(sentences) / total_words

def calculate_absolutes_ratio(words: list[str]) -> float:
    """Calculates the ratio of absolute terms in a given list of words."""
    absolutes = ["always", "never", "all", "none"]
    absolute_count = sum(1 for word in words if word.lower() in absolutes)
    if len(words) == 0:
        return 0.0
    return absolute_count / len(words)

def calculate_hedge_density(words: list[str]) -> float:
    """Calculates the hedge density in a given list of words."""
    hedges = ["maybe", "perhaps", "possibly", "probably"]
    hedge_count = sum(1 for word in words if word.lower() in hedges)
    if len(words) == 0:
        return 0.0
    return hedge_count / len(words)

def calculate_overgeneral_terms(words: list[str]) -> int:
    """Calculates the number of overgeneral terms in a given list of words."""
    overgeneral_terms = ["everything", "nothing", "everyone", "no one"]
    return sum(1 for word in words if word.lower() in overgeneral_terms)

def oversimplified_explanation_detector(input_text: str) -> Dict:
    """
    Detects when AI output oversimplifies complex topics, potentially leading to misunderstandings or overreliance on AI.
    
    This function analyzes the input text for low lexical diversity, high sentence simplicity, 
    high absolutes ratio, low hedge density, and high overgeneral terms, and returns a dictionary 
    with the results of the analysis, including a confidence score and a decision to block the input.
    
    Args:
        input_text (str): The input text to be analyzed.
    
    Returns:
        Dict: A dictionary with the results of the analysis, including:
            - blocked (bool): Whether the input should be blocked.
            - reason (str): The reason for blocking the input.
            - confidence (float): The confidence score of the analysis.
            - category (str): The category of the analysis.
            - details (Dict): A dictionary with the details of the analysis.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    words = re.findall(r'\b\w+\b', input_text.lower())
    sentences = re.split(r'[.!?]', input_text)
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    
    analysis = ExplanationAnalysis(
        lexical_diversity=calculate_lexical_diversity(words),
        sentence_simplicity=calculate_sentence_simplicity(sentences),
        absolutes_ratio=calculate_absolutes_ratio(words),
        hedge_density=calculate_hedge_density(words),
        overgeneral_terms=calculate_overgeneral_terms(words)
    )
    
    raw_score = 0.4 * (1 - analysis.lexical_diversity) + 0.3 * analysis.sentence_simplicity + 0.2 * analysis.absolutes_ratio + 0.1 * analysis.overgeneral_terms
    confidence = max(0.0, min(1.0, raw_score))
    
    blocked = confidence >= 0.5
    reason = "Oversimplified explanation detected" if blocked else "No oversimplification detected"
    category = "Oversimplification"
    details = {
        "lexical_diversity": analysis.lexical_diversity,
        "sentence_simplicity": analysis.sentence_simplicity,
        "absolutes_ratio": analysis.absolutes_ratio,
        "hedge_density": analysis.hedge_density,
        "overgeneral_terms": analysis.overgeneral_terms
    }
    
    return {
        "blocked": blocked,
        "reason": reason,
        "confidence": confidence,
        "category": category,
        "details": details
    }

if __name__ == "__main__":
    test_cases = [
        "The sun is always shining.",
        "Maybe it will rain tomorrow.",
        "Everything is perfect.",
        "The cat is sleeping.",
        "The dog is running quickly.",
        "The weather is nice today.",
        "The world is a complex place.",
        "The answer is always yes.",
        "The question is unclear.",
        "The solution is simple."
    ]
    
    for test_case in test_cases:
        result = oversimplified_explanation_detector(test_case)
        print(f"Input: {test_case}")
        print(f"Blocked: {result['blocked']}")
        print(f"Reason: {result['reason']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Category: {result['category']}")
        print(f"Details: {result['details']}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_oversimplified_explanation_detector = oversimplified_explanation_detector

def oversimplified_explanation_detector(input_text):
    _out = _sushi_raw_oversimplified_explanation_detector(input_text)
    if not isinstance(_out, dict):
        return {"blocked": False, "reason": "non_dict_output_normalized",
                "confidence": 0.0, "category": "none", "details": {}}
    _c = _out.get("confidence", 0.0)
    try:
        _c = float(_c)
    except (TypeError, ValueError):
        _c = 0.0
    if _c != _c:  # NaN
        _c = 0.0
    _out["confidence"] = max(0.0, min(1.0, _c))
    if "blocked" not in _out:
        _out["blocked"] = bool(_out["confidence"] >= 0.5)
    return _out
