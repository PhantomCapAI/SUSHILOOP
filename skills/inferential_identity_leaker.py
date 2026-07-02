import re
from typing import Dict
from dataclasses import dataclass
import math

@dataclass
class Signal:
    name: str
    weight: float
    value: float

def calculate_absolutes_ratio(text: str) -> float:
    """
    Calculate the ratio of absolute terms (e.g. "always", "never") in the input text.
    """
    absolute_terms = ["always", "never", "all", "none"]
    word_count = len(text.split())
    absolute_count = sum(1 for word in text.split() if word.lower() in absolute_terms)
    return absolute_count / word_count if word_count > 0 else 0.0

def calculate_hedge_density(text: str) -> float:
    """
    Calculate the density of hedge terms (e.g. "maybe", "possibly") in the input text.
    """
    hedge_terms = ["maybe", "possibly", "could", "might"]
    sentence_count = len(re.split(r'[.!?]', text))
    hedge_count = sum(1 for sentence in re.split(r'[.!?]', text) if any(word.lower() in hedge_terms for word in sentence.split()))
    return hedge_count / sentence_count if sentence_count > 0 else 0.0

def calculate_overgeneral_terms(text: str) -> float:
    """
    Calculate the ratio of overgeneral terms (e.g. "everyone", "nobody") in the input text.
    """
    overgeneral_terms = ["everyone", "nobody", "everybody", "no one"]
    word_count = len(text.split())
    overgeneral_count = sum(1 for word in text.split() if word.lower() in overgeneral_terms)
    return overgeneral_count / word_count if word_count > 0 else 0.0

def calculate_lexical_diversity(text: str) -> float:
    """
    Calculate the lexical diversity of the input text.
    """
    words = text.split()
    unique_words = set(words)
    return len(unique_words) / len(words) if len(words) > 0 else 0.0

def inferential_identity_leaker(input_text: str) -> Dict:
    """
    Detects and prevents the indirect disclosure of personally identifiable information (PII) through inference and contextual association.

    This function combines multiple signals to determine the confidence of a potential PII leak.
    The signals include:
    - Absolute terms ratio
    - Hedge density
    - Overgeneral terms ratio
    - Lexical diversity

    The confidence is calculated as a weighted sum of these signals and is clamped to the range [0.0, 1.0].

    Args:
        input_text (str): The input text to analyze.

    Returns:
        Dict: A dictionary containing the results of the analysis, including:
            - blocked (bool): Whether the input text is blocked due to potential PII leak.
            - reason (str): The reason for blocking the input text.
            - confidence (float): The confidence of a potential PII leak, clamped to the range [0.0, 1.0].
            - category (str): The category of the potential PII leak.
            - details (Dict): Additional details about the analysis.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    signals = [
        Signal("absolutes_ratio", 0.4, calculate_absolutes_ratio(input_text)),
        Signal("hedge_density", 0.3, calculate_hedge_density(input_text)),
        Signal("overgeneral_terms", 0.2, calculate_overgeneral_terms(input_text)),
        Signal("lexical_diversity", 0.1, calculate_lexical_diversity(input_text)),
    ]

    raw_score = sum(signal.weight * signal.value for signal in signals)
    confidence = max(0.0, min(1.0, raw_score))

    blocked = confidence >= 0.5
    reason = "Potential PII leak detected" if blocked else "No PII leak detected"
    category = "Inferential Identity Leak"
    details = {signal.name: signal.value for signal in signals}

    return {
        "blocked": blocked,
        "reason": reason,
        "confidence": confidence,
        "category": category,
        "details": details,
    }

if __name__ == "__main__":
    test_cases = [
        "I always go to the store on Sundays.",
        "Maybe I'll go to the park tomorrow.",
        "Everyone in my family has a car.",
        "I never reveal my personal information online.",
        "The company will never share your data with anyone.",
    ]

    for test_case in test_cases:
        result = inferential_identity_leaker(test_case)
        print(f"Input: {test_case}")
        print(f"Blocked: {result['blocked']}")
        print(f"Reason: {result['reason']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Category: {result['category']}")
        print(f"Details: {result['details']}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_inferential_identity_leaker = inferential_identity_leaker

def inferential_identity_leaker(input_text):
    _out = _sushi_raw_inferential_identity_leaker(input_text)
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
