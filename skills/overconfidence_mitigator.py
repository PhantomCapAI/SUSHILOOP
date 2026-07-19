import re
from typing import Dict
from dataclasses import dataclass
from math import log

@dataclass
class OverconfidenceSignals:
    """Dataclass to hold overconfidence signals."""
    absolutes_ratio: float
    hedge_density: float
    overgeneral_terms: float
    sentence_count: int
    word_count: int

def calculate_absolutes_ratio(input_text: str) -> float:
    """Calculate the ratio of absolute terms to total words."""
    absolute_terms = re.findall(r'\b(always|never|certainly|definitely|clearly)\b', input_text, re.IGNORECASE)
    words = input_text.split()
    if not words:
        return 0.0
    return len(absolute_terms) / len(words)

def calculate_hedge_density(input_text: str) -> float:
    """Calculate the density of hedge terms."""
    hedge_terms = re.findall(r'\b(maybe|perhaps|possibly|likely|unlikely)\b', input_text, re.IGNORECASE)
    sentences = re.split(r'[.!?]', input_text)
    if not sentences:
        return 0.0
    return len(hedge_terms) / len(sentences)

def calculate_overgeneral_terms(input_text: str) -> float:
    """Calculate the frequency of overgeneral terms."""
    overgeneral_terms = re.findall(r'\b(everyone|everything|all|none|no one)\b', input_text, re.IGNORECASE)
    words = input_text.split()
    if not words:
        return 0.0
    return len(overgeneral_terms) / len(words)

def calculate_overconfidence_signals(input_text: str) -> OverconfidenceSignals:
    """Calculate overconfidence signals."""
    absolutes_ratio = calculate_absolutes_ratio(input_text)
    hedge_density = calculate_hedge_density(input_text)
    overgeneral_terms = calculate_overgeneral_terms(input_text)
    sentence_count = len(re.split(r'[.!?]', input_text))
    word_count = len(input_text.split())
    return OverconfidenceSignals(absolutes_ratio, hedge_density, overgeneral_terms, sentence_count, word_count)

def overconfidence_mitigator(input_text: str) -> Dict[str, object]:
    """
    Detects and flags instances where AI-generated responses exhibit overly confident language.

    Args:
    input_text (str): The input text to be evaluated.

    Returns:
    Dict[str, object]: A dictionary containing the evaluation results.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    signals = calculate_overconfidence_signals(input_text)
    raw_confidence = 0.5 * signals.absolutes_ratio + 0.3 * (1 - signals.hedge_density) + 0.2 * signals.overgeneral_terms
    confidence = max(0.0, min(1.0, raw_confidence))
    blocked = confidence >= 0.5
    reason = "Overly confident language detected" if blocked else "No overly confident language detected"
    category = "Overconfidence"
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
        "I am absolutely certain that this is the best solution.",
        "Maybe this solution will work, but we need to test it.",
        "Everyone will love this new feature.",
        "This is a good solution, but we should consider other options.",
        "I am never going to use this product again."
    ]
    for test_case in test_cases:
        result = overconfidence_mitigator(test_case)
        print(f"Input: {test_case}")
        print(f"Blocked: {result['blocked']}")
        print(f"Reason: {result['reason']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Category: {result['category']}")
        print(f"Details: {result['details']}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_overconfidence_mitigator = overconfidence_mitigator

def overconfidence_mitigator(input_text):
    _out = _sushi_raw_overconfidence_mitigator(input_text)
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
