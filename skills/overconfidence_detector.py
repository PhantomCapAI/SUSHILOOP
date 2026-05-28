import re
from typing import Dict
from dataclasses import dataclass
from math import log

@dataclass
class OverconfidenceSignals:
    """Dataclass to hold overconfidence signals"""
    absolutes_ratio: float
    hedge_density: float
    overgeneral_terms: float
    sentence_count: int
    word_count: int

def calculate_overconfidence_signals(input_text: str) -> OverconfidenceSignals:
    """
    Calculate overconfidence signals from input text.

    Args:
    input_text (str): The input text to analyze.

    Returns:
    OverconfidenceSignals: A dataclass containing the calculated signals.
    """
    # Split input text into sentences
    sentences = re.split(r'[.!?]', input_text)
    sentence_count = len([s for s in sentences if s.strip()])

    # Split input text into words
    words = re.findall(r'\b\w+\b', input_text)
    word_count = len(words)

    # Calculate absolutes ratio
    absolutes = re.findall(r'\b(always|never|every|all)\b', input_text, re.IGNORECASE)
    absolutes_ratio = len(absolutes) / word_count if word_count > 0 else 0.0

    # Calculate hedge density
    hedges = re.findall(r'\b(maybe|perhaps|possibly|likely|unlikely)\b', input_text, re.IGNORECASE)
    hedge_density = len(hedges) / word_count if word_count > 0 else 0.0

    # Calculate overgeneral terms
    overgeneral_terms = re.findall(r'\b(all|every|always|never)\b', input_text, re.IGNORECASE)
    overgeneral_terms_ratio = len(overgeneral_terms) / word_count if word_count > 0 else 0.0

    return OverconfidenceSignals(
        absolutes_ratio=absolutes_ratio,
        hedge_density=hedge_density,
        overgeneral_terms=overgeneral_terms_ratio,
        sentence_count=sentence_count,
        word_count=word_count
    )

def overconfidence_detector(input_text: str) -> Dict:
    """
    Detect overconfidence in AI output.

    This function analyzes the input text for phrases and tone that convey unwarranted certainty.
    It calculates a graded confidence score based on multiple signals, including absolutes ratio,
    hedge density, and overgeneral terms. The function returns a dictionary containing the
    detection result, reason, confidence score, category, and details.

    Args:
    input_text (str): The input text to analyze.

    Returns:
    Dict: A dictionary containing the detection result, reason, confidence score, category, and details.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    signals = calculate_overconfidence_signals(input_text)

    # Calculate raw confidence score
    raw_score = 0.5 * signals.absolutes_ratio + 0.3 * (1 - signals.hedge_density) + 0.2 * signals.overgeneral_terms

    # Clamp confidence score to [0.0, 1.0]
    confidence = max(0.0, min(1.0, raw_score))

    # Determine detection result and reason
    blocked = confidence > 0.7
    reason = "Overconfident language detected" if blocked else "No overconfident language detected"

    # Determine category
    category = "High" if confidence > 0.8 else "Medium" if confidence > 0.5 else "Low"

    # Create details dictionary
    details = {
        "absolutes_ratio": signals.absolutes_ratio,
        "hedge_density": signals.hedge_density,
        "overgeneral_terms": signals.overgeneral_terms,
        "sentence_count": signals.sentence_count,
        "word_count": signals.word_count
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
        "I am always right.",
        "Maybe it will work.",
        "Every time I try, it fails.",
        "This is a test.",
        "Never give up.",
        "Possibly, it could happen.",
        "All things are possible.",
        "Every day is a new chance.",
        "Always look on the bright side.",
        "Never look back."
    ]

    for test_case in test_cases:
        result = overconfidence_detector(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_overconfidence_detector = overconfidence_detector

def overconfidence_detector(input_text):
    _out = _sushi_raw_overconfidence_detector(input_text)
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
