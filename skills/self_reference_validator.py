import re
from typing import Dict
from dataclasses import dataclass
from collections import Counter
from math import log

@dataclass
class SentenceFeatures:
    """Features extracted from a sentence."""
    absolutes: int
    hedges: int
    overgeneral_terms: int
    word_count: int

def extract_sentence_features(sentence: str) -> SentenceFeatures:
    """Extract features from a sentence."""
    absolutes = len(re.findall(r'\b(always|never|all|every|none)\b', sentence, re.IGNORECASE))
    hedges = len(re.findall(r'\b(maybe|perhaps|possibly|likely|unlikely)\b', sentence, re.IGNORECASE))
    overgeneral_terms = len(re.findall(r'\b(all|every|always|never)\b', sentence, re.IGNORECASE))
    word_count = len(sentence.split())
    return SentenceFeatures(absolutes, hedges, overgeneral_terms, word_count)

def calculate_confidence(features: SentenceFeatures, sentence_count: int) -> float:
    """Calculate confidence based on sentence features."""
    if sentence_count == 0:
        return 0.0
    absolutes_ratio = features.absolutes / sentence_count if sentence_count > 0 else 0.0
    hedge_density = features.hedges / features.word_count if features.word_count > 0 else 0.0
    overgeneral_terms_ratio = features.overgeneral_terms / sentence_count if sentence_count > 0 else 0.0
    raw_score = 0.5 * absolutes_ratio + 0.3 * hedge_density + 0.2 * overgeneral_terms_ratio
    return max(0.0, min(1.0, raw_score))

def self_reference_validator(input_text: str) -> Dict:
    """
    Validates user input for self-referential statements.

    This function detects and flags instances where user input contains self-referential statements or questions,
    which can lead to infinite loops or unsolvable queries, thereby protecting human cognition from potential pitfalls of AI interactions.

    Args:
        input_text (str): The user input to be validated.

    Returns:
        Dict: A dictionary containing the validation result.
            - blocked (bool): Whether the input is blocked.
            - reason (str): The reason for blocking the input.
            - confidence (float): The confidence level of the validation result.
            - category (str): The category of the validation result.
            - details (Dict): Additional details about the validation result.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    sentences = re.split(r'[.!?]', input_text)
    sentence_features = [extract_sentence_features(sentence) for sentence in sentences if sentence.strip()]
    if not sentence_features:
        return {"blocked": False, "reason": "No self-referential statements detected", "confidence": 0.0, "category": "safe", "details": {}}

    total_absolutes = sum(feature.absolutes for feature in sentence_features)
    total_hedges = sum(feature.hedges for feature in sentence_features)
    total_overgeneral_terms = sum(feature.overgeneral_terms for feature in sentence_features)
    total_word_count = sum(feature.word_count for feature in sentence_features)
    total_sentence_count = len(sentence_features)

    features = SentenceFeatures(total_absolutes, total_hedges, total_overgeneral_terms, total_word_count)
    confidence = calculate_confidence(features, total_sentence_count)

    if confidence > 0.7:
        return {"blocked": True, "reason": "Self-referential statement detected", "confidence": confidence, "category": "unsafe", "details": {"absolutes": total_absolutes, "hedges": total_hedges, "overgeneral_terms": total_overgeneral_terms}}
    else:
        return {"blocked": False, "reason": "No self-referential statements detected", "confidence": confidence, "category": "safe", "details": {}}

if __name__ == "__main__":
    test_cases = [
        "This sentence is true.",
        "The statement is false.",
        "Maybe this sentence is true.",
        "All statements are true.",
        "This sentence is not true.",
        "The statement is possibly false.",
        "Every statement is true.",
        "The statement is always false.",
        "The statement is never true.",
    ]

    for test_case in test_cases:
        result = self_reference_validator(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_self_reference_validator = self_reference_validator

def self_reference_validator(input_text):
    _out = _sushi_raw_self_reference_validator(input_text)
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
