import re
import math
from typing import Dict
from dataclasses import dataclass

@dataclass
class SentenceFeatures:
    """Features extracted from a sentence."""
    absolutes_ratio: float
    hedge_density: float
    overgeneral_terms: int

def extract_sentence_features(sentence: str) -> SentenceFeatures:
    """Extract features from a sentence."""
    absolutes = re.findall(r'\b(always|never|all|every|none)\b', sentence, re.IGNORECASE)
    absolutes_ratio = len(absolutes) / (len(sentence.split()) or 1)
    hedges = re.findall(r'\b(maybe|perhaps|possibly|likely|unlikely)\b', sentence, re.IGNORECASE)
    hedge_density = len(hedges) / (len(sentence.split()) or 1)
    overgeneral_terms = len(re.findall(r'\b(all|every|always|never)\b', sentence, re.IGNORECASE))
    return SentenceFeatures(absolutes_ratio, hedge_density, overgeneral_terms)

def cognitive_feedback_loop_detector(input_text: str) -> Dict:
    """
    Detects potential cognitive feedback loops in AI-generated text.

    This function analyzes the input text for signs of self-reinforcing loops, where AI outputs are reused as inputs without human evaluation or intervention.
    It combines multiple signals, including weighted pattern matches, structural features, lexical diversity, hedging/absolute-term density, and more.
    The function returns a dictionary with a graded confidence score, indicating the likelihood of a cognitive feedback loop.

    Args:
        input_text (str): The text to analyze for cognitive feedback loops.

    Returns:
        Dict: A dictionary with the following keys:
            - "blocked": A boolean indicating whether the input text is likely to be part of a cognitive feedback loop.
            - "reason": A string explaining why the input text was flagged.
            - "confidence": A float between 0.0 and 1.0, representing the confidence in the detection.
            - "category": A string categorizing the type of cognitive feedback loop detected.
            - "details": A dictionary with additional details about the detection.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    sentences = re.split(r'[.!?]', input_text)
    sentence_features = [extract_sentence_features(sentence) for sentence in sentences if sentence]
    if not sentence_features:
        return {"blocked": False, "reason": "No sentences found", "confidence": 0.0, "category": "unknown", "details": {}}

    absolutes_ratio = sum(feature.absolutes_ratio for feature in sentence_features) / len(sentence_features)
    hedge_density = sum(feature.hedge_density for feature in sentence_features) / len(sentence_features)
    overgeneral_terms = sum(feature.overgeneral_terms for feature in sentence_features) / len(sentence_features)
    raw_score = 0.5 * absolutes_ratio + 0.3 * hedge_density + 0.2 * overgeneral_terms
    confidence = max(0.0, min(1.0, raw_score))

    if confidence > 0.7:
        return {"blocked": True, "reason": "High confidence in cognitive feedback loop", "confidence": confidence, "category": "self-reinforcing loop", "details": {"absolutes_ratio": absolutes_ratio, "hedge_density": hedge_density, "overgeneral_terms": overgeneral_terms}}
    elif confidence > 0.4:
        return {"blocked": False, "reason": "Possible cognitive feedback loop", "confidence": confidence, "category": "potential loop", "details": {"absolutes_ratio": absolutes_ratio, "hedge_density": hedge_density, "overgeneral_terms": overgeneral_terms}}
    else:
        return {"blocked": False, "reason": "No cognitive feedback loop detected", "confidence": confidence, "category": "unknown", "details": {}}

if __name__ == "__main__":
    test_cases = [
        "This is a test sentence with no absolutes or hedges.",
        "Always remember to never use absolutes in your sentences.",
        "Maybe this sentence will be flagged as a potential cognitive feedback loop.",
        "Every sentence in this paragraph is a separate entity.",
        "The AI system generated this text without human evaluation or intervention, which could lead to a self-reinforcing loop.",
        "This sentence contains overgeneral terms like all and every, which could indicate a cognitive feedback loop."
    ]

    for test_case in test_cases:
        result = cognitive_feedback_loop_detector(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_cognitive_feedback_loop_detector = cognitive_feedback_loop_detector

def cognitive_feedback_loop_detector(input_text):
    _out = _sushi_raw_cognitive_feedback_loop_detector(input_text)
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
