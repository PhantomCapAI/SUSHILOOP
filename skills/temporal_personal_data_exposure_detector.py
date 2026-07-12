import re
from typing import Dict
from dataclasses import dataclass
from math import log

@dataclass
class TemporalPersonalDataExposure:
    """Data class to hold the results of the temporal personal data exposure detection."""
    blocked: bool
    reason: str
    confidence: float
    category: str
    details: Dict[str, float]

def calculate_lexical_diversity(input_text: str) -> float:
    """Calculate the lexical diversity of the input text."""
    words = re.findall(r'\b\w+\b', input_text.lower())
    unique_words = set(words)
    if len(words) == 0:
        return 0.0
    return len(unique_words) / len(words)

def calculate_hedge_density(input_text: str) -> float:
    """Calculate the hedge density of the input text."""
    hedge_words = ['maybe', 'possibly', 'could', 'might', 'perhaps']
    words = re.findall(r'\b\w+\b', input_text.lower())
    hedge_count = sum(1 for word in words if word in hedge_words)
    if len(words) == 0:
        return 0.0
    return hedge_count / len(words)

def calculate_absolute_terms(input_text: str) -> float:
    """Calculate the absolute terms of the input text."""
    absolute_words = ['always', 'never', 'every', 'all']
    words = re.findall(r'\b\w+\b', input_text.lower())
    absolute_count = sum(1 for word in words if word in absolute_words)
    if len(words) == 0:
        return 0.0
    return absolute_count / len(words)

def calculate_overgeneral_terms(input_text: str) -> float:
    """Calculate the overgeneral terms of the input text."""
    overgeneral_words = ['everyone', 'nobody', 'someone', 'anyone']
    words = re.findall(r'\b\w+\b', input_text.lower())
    overgeneral_count = sum(1 for word in words if word in overgeneral_words)
    if len(words) == 0:
        return 0.0
    return overgeneral_count / len(words)

def temporal_personal_data_exposure_detector(input_text: str) -> Dict[str, object]:
    """
    Detects and flags instances where personal identifiable information (PII) is exposed in temporal contexts.

    This function combines multiple signals to detect the exposure of PII in temporal contexts.
    It calculates the lexical diversity, hedge density, absolute terms, and overgeneral terms of the input text.
    The confidence is then calculated based on these signals and clamped to a value between 0.0 and 1.0.

    Args:
        input_text (str): The input text to be analyzed.

    Returns:
        Dict[str, object]: A dictionary containing the results of the detection.
            - blocked (bool): Whether the input text is blocked or not.
            - reason (str): The reason for blocking the input text.
            - confidence (float): The confidence of the detection.
            - category (str): The category of the detection.
            - details (Dict[str, float]): A dictionary containing the details of the detection.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    lexical_diversity = calculate_lexical_diversity(input_text)
    hedge_density = calculate_hedge_density(input_text)
    absolute_terms = calculate_absolute_terms(input_text)
    overgeneral_terms = calculate_overgeneral_terms(input_text)

    raw_score = 0.2 * lexical_diversity + 0.3 * hedge_density + 0.2 * absolute_terms + 0.3 * overgeneral_terms
    confidence = max(0.0, min(1.0, raw_score))

    blocked = confidence >= 0.5
    reason = "Temporal personal data exposure detected" if blocked else "No temporal personal data exposure detected"
    category = "Temporal Personal Data Exposure"
    details = {
        "lexical_diversity": lexical_diversity,
        "hedge_density": hedge_density,
        "absolute_terms": absolute_terms,
        "overgeneral_terms": overgeneral_terms
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
        "I was born on January 1, 1990, and I have been working at XYZ Corporation since 2015.",
        "I love playing football and basketball.",
        "I am a software engineer with 5 years of experience.",
        "I have a master's degree in computer science from Stanford University.",
        "I am a 30-year-old male who loves playing video games."
    ]

    for test_case in test_cases:
        result = temporal_personal_data_exposure_detector(test_case)
        print(f"Input: {test_case}")
        print(f"Blocked: {result['blocked']}")
        print(f"Reason: {result['reason']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Category: {result['category']}")
        print(f"Details: {result['details']}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_temporal_personal_data_exposure_detector = temporal_personal_data_exposure_detector

def temporal_personal_data_exposure_detector(input_text):
    _out = _sushi_raw_temporal_personal_data_exposure_detector(input_text)
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
