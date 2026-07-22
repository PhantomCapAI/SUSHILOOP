import re
from typing import Dict
from dataclasses import dataclass
from math import log

@dataclass
class Signal:
    name: str
    weight: float
    value: float

def calculate_absolutes_ratio(input_text: str) -> float:
    """
    Calculate the ratio of absolute terms (e.g., "always", "never") to total words.
    """
    absolute_terms = re.findall(r"\b(always|never|all|none)\b", input_text, re.IGNORECASE)
    words = re.findall(r"\b\w+\b", input_text)
    return len(absolute_terms) / max(len(words), 1)

def calculate_hedge_density(input_text: str) -> float:
    """
    Calculate the density of hedging terms (e.g., "maybe", "possibly") in the input text.
    """
    hedge_terms = re.findall(r"\b(maybe|possibly|perhaps|could|might)\b", input_text, re.IGNORECASE)
    sentences = re.findall(r"[.!?]", input_text)
    return len(hedge_terms) / max(len(sentences), 1)

def calculate_overgeneral_terms(input_text: str) -> float:
    """
    Calculate the frequency of overgeneral terms (e.g., "everyone", "nobody") in the input text.
    """
    overgeneral_terms = re.findall(r"\b(everyone|nobody|everybody|noone)\b", input_text, re.IGNORECASE)
    words = re.findall(r"\b\w+\b", input_text)
    return len(overgeneral_terms) / max(len(words), 1)

def calculate_lexical_diversity(input_text: str) -> float:
    """
    Calculate the lexical diversity of the input text, i.e., the ratio of unique words to total words.
    """
    words = re.findall(r"\b\w+\b", input_text)
    unique_words = set(words)
    return len(unique_words) / max(len(words), 1)

def self_harm_routing_guard(input_text: str) -> Dict:
    """
    Detects distress signals in the input text and returns a dictionary with the results.

    The mission of this function is to scaffold, not substitute, real support by detecting
    potential self-harm signals and providing a graded confidence score. The function combines
    multiple signals, including absolute terms ratio, hedge density, overgeneral terms frequency,
    and lexical diversity, to produce a confidence score that varies with the input text.

    Args:
        input_text (str): The input text to be analyzed.

    Returns:
        Dict: A dictionary with the following keys:
            - blocked (bool): Whether the input text is blocked based on the confidence score.
            - reason (str): A brief reason for the blocking decision.
            - confidence (float): A graded confidence score between 0.0 and 1.0.
            - category (str): The category of the detected signal (e.g., "self-harm").
            - details (Dict): Additional details about the detected signal.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    signals = [
        Signal("absolutes_ratio", 0.5, calculate_absolutes_ratio(input_text)),
        Signal("hedge_density", 0.3, calculate_hedge_density(input_text)),
        Signal("overgeneral_terms", 0.2, calculate_overgeneral_terms(input_text)),
        Signal("lexical_diversity", 0.0, calculate_lexical_diversity(input_text)),
    ]

    raw_score = sum(signal.weight * signal.value for signal in signals)
    confidence = max(0.0, min(1.0, raw_score))

    blocked = confidence >= 0.5
    reason = "Potential self-harm signal detected" if blocked else "No self-harm signal detected"
    category = "self-harm"
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
        "I'm feeling really down and I don't know what to do.",
        "I'm just having a bad day, but I'll be fine.",
        "Everyone hates me and I'm a total failure.",
        "I'm not sure what's going on, but I'm feeling a bit overwhelmed.",
        "I'm just tired and need to get some rest.",
    ]

    for test_case in test_cases:
        result = self_harm_routing_guard(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_self_harm_routing_guard = self_harm_routing_guard

def self_harm_routing_guard(input_text):
    _out = _sushi_raw_self_harm_routing_guard(input_text)
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
