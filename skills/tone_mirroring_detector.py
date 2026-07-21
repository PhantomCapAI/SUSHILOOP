import re
import math
from typing import Dict
from dataclasses import dataclass

@dataclass
class ToneMirroringResult:
    blocked: bool
    reason: str
    confidence: float
    category: str
    details: Dict[str, float]

def calculate_absolutes_ratio(text: str) -> float:
    """
    Calculate the ratio of absolute terms (e.g., always, never) in the text.
    """
    absolute_terms = re.findall(r'\b(always|never|all|none)\b', text, re.IGNORECASE)
    word_count = len(re.findall(r'\b\w+\b', text))
    return len(absolute_terms) / word_count if word_count > 0 else 0.0

def calculate_hedge_density(text: str) -> float:
    """
    Calculate the density of hedge terms (e.g., maybe, possibly) in the text.
    """
    hedge_terms = re.findall(r'\b(maybe|possibly|perhaps|could|might)\b', text, re.IGNORECASE)
    sentence_count = len(re.findall(r'[.!?]', text))
    return len(hedge_terms) / sentence_count if sentence_count > 0 else 0.0

def calculate_overgeneral_terms(text: str) -> float:
    """
    Calculate the ratio of overgeneral terms (e.g., everyone, nobody) in the text.
    """
    overgeneral_terms = re.findall(r'\b(everyone|nobody|everybody|noone)\b', text, re.IGNORECASE)
    word_count = len(re.findall(r'\b\w+\b', text))
    return len(overgeneral_terms) / word_count if word_count > 0 else 0.0

def tone_mirroring_detector(input_text: str) -> Dict[str, object]:
    """
    Detect tone mirroring in AI responses.

    This function combines multiple signals to detect tone mirroring, including:
    - Absolute terms ratio
    - Hedge density
    - Overgeneral terms ratio

    The confidence score is a graded value between 0.0 and 1.0, where:
    - 0.0 indicates no tone mirroring
    - 1.0 indicates strong tone mirroring

    The function returns a dictionary with the following keys:
    - blocked: a boolean indicating whether the input text is blocked
    - reason: a string explaining why the input text is blocked
    - confidence: a float between 0.0 and 1.0 indicating the confidence of tone mirroring
    - category: a string indicating the category of tone mirroring
    - details: a dictionary with detailed information about the tone mirroring signals

    :param input_text: The input text to analyze
    :return: A dictionary with the tone mirroring detection results
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    absolutes_ratio = calculate_absolutes_ratio(input_text)
    hedge_density = calculate_hedge_density(input_text)
    overgeneral_terms = calculate_overgeneral_terms(input_text)

    raw_score = 0.5 * absolutes_ratio + 0.3 * hedge_density + 0.2 * overgeneral_terms
    confidence = max(0.0, min(1.0, raw_score))

    blocked = confidence >= 0.5
    reason = "Tone mirroring detected" if blocked else "No tone mirroring detected"
    category = "Tone Mirroring"
    details = {
        "absolutes_ratio": absolutes_ratio,
        "hedge_density": hedge_density,
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
        "I always love using this product.",
        "Maybe this product is okay, but I'm not sure.",
        "Everyone hates this product, it's terrible.",
        "This product is great, but it has some minor issues.",
        "I'm not sure about this product, it's just okay."
    ]

    for test_case in test_cases:
        result = tone_mirroring_detector(test_case)
        print(f"Input: {test_case}")
        print(f"Blocked: {result['blocked']}")
        print(f"Reason: {result['reason']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Category: {result['category']}")
        print(f"Details: {result['details']}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_tone_mirroring_detector = tone_mirroring_detector

def tone_mirroring_detector(input_text):
    _out = _sushi_raw_tone_mirroring_detector(input_text)
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
