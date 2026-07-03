import re
from typing import Dict
from dataclasses import dataclass

@dataclass
class DetectionResult:
    blocked: bool
    reason: str
    confidence: float
    category: str
    details: Dict[str, float]

def calculate_absolutes_ratio(text: str) -> float:
    """
    Calculate the ratio of absolute terms (e.g. "always", "never") to total words.
    """
    absolute_terms = re.findall(r"\b(always|never|certainly|definitely)\b", text, re.IGNORECASE)
    total_words = len(re.findall(r"\b\w+\b", text))
    return len(absolute_terms) / total_words if total_words > 0 else 0.0

def calculate_hedge_density(text: str) -> float:
    """
    Calculate the density of hedging terms (e.g. "maybe", "possibly") in the text.
    """
    hedge_terms = re.findall(r"\b(maybe|possibly|perhaps|could)\b", text, re.IGNORECASE)
    total_words = len(re.findall(r"\b\w+\b", text))
    return len(hedge_terms) / total_words if total_words > 0 else 0.0

def calculate_overgeneral_terms(text: str) -> float:
    """
    Calculate the frequency of overgeneral terms (e.g. "all", "every") in the text.
    """
    overgeneral_terms = re.findall(r"\b(all|every|each|any)\b", text, re.IGNORECASE)
    total_words = len(re.findall(r"\b\w+\b", text))
    return len(overgeneral_terms) / total_words if total_words > 0 else 0.0

def overly_confident_assertion_detector(input_text: str) -> Dict:
    """
    Detect overly confident assertions in the input text.

    This function combines multiple signals to detect overly confident assertions:
    - Absolute terms ratio: the ratio of absolute terms (e.g. "always", "never") to total words.
    - Hedge density: the density of hedging terms (e.g. "maybe", "possibly") in the text.
    - Overgeneral terms: the frequency of overgeneral terms (e.g. "all", "every") in the text.

    The confidence score is a weighted sum of these signals, clamped to [0.0, 1.0].
    The `blocked` decision is based on a threshold of 0.5.

    Args:
        input_text (str): The input text to analyze.

    Returns:
        Dict: A dictionary containing the detection result:
            - blocked (bool): Whether the input text is blocked.
            - reason (str): The reason for blocking (if applicable).
            - confidence (float): The confidence score [0.0, 1.0].
            - category (str): The category of the detection (e.g. "overly confident assertion").
            - details (Dict): Additional details about the detection (e.g. signal values).
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    absolutes_ratio = calculate_absolutes_ratio(input_text)
    hedge_density = calculate_hedge_density(input_text)
    overgeneral_terms = calculate_overgeneral_terms(input_text)

    raw_score = 0.5 * absolutes_ratio + 0.3 * (1 - hedge_density) + 0.2 * overgeneral_terms
    confidence = max(0.0, min(1.0, raw_score))

    blocked = confidence >= 0.5
    reason = "Overly confident assertion detected" if blocked else "No overly confident assertion detected"
    category = "overly confident assertion"
    details = {
        "absolutes_ratio": absolutes_ratio,
        "hedge_density": hedge_density,
        "overgeneral_terms": overgeneral_terms,
    }

    return {
        "blocked": blocked,
        "reason": reason,
        "confidence": confidence,
        "category": category,
        "details": details,
    }

if __name__ == "__main__":
    test_cases = [
        "I am always right.",
        "Maybe it will work.",
        "Every person is unique.",
        "This is certainly true.",
        "It is possible that it will rain tomorrow.",
    ]

    for test_case in test_cases:
        result = overly_confident_assertion_detector(test_case)
        print(f"Input: {test_case}")
        print(f"Blocked: {result['blocked']}")
        print(f"Reason: {result['reason']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Category: {result['category']}")
        print(f"Details: {result['details']}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_overly_confident_assertion_detector = overly_confident_assertion_detector

def overly_confident_assertion_detector(input_text):
    _out = _sushi_raw_overly_confident_assertion_detector(input_text)
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
