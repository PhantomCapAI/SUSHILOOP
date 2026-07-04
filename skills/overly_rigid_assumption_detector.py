import re
from typing import Dict
from dataclasses import dataclass
from collections import Counter

@dataclass
class DetectionResult:
    blocked: bool
    reason: str
    confidence: float
    category: str
    details: Dict

def overly_rigid_assumption_detector(input_text: str) -> Dict:
    """
    Detects overly rigid assumptions in user input by analyzing the text for signs of 
    absolute language, overgeneralization, and lack of hedging. Returns a dictionary 
    with a confidence score and other metadata.

    Mission alignment: This skill promotes critical thinking and healthy human-AI 
    collaboration by encouraging users to challenge and verify assumptions underlying 
    AI-generated responses.

    :param input_text: The user's input text to be analyzed
    :return: A dictionary with the detection result
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Preprocessing
    sentences = re.split(r'[.!?]', input_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = re.findall(r'\b\w+\b', input_text.lower())

    # Signal 1: Absolute language density
    absolutes = re.findall(r'\b(always|never|all|every|none)\b', input_text.lower())
    absolutes_ratio = len(absolutes) / len(words) if words else 0

    # Signal 2: Hedge density
    hedges = re.findall(r'\b(maybe|perhaps|possibly|probably|likely)\b', input_text.lower())
    hedge_density = len(hedges) / len(words) if words else 0

    # Signal 3: Overgeneralization terms
    overgeneral_terms = re.findall(r'\b(everyone|everything|all|any)\b', input_text.lower())
    overgeneral_terms_ratio = len(overgeneral_terms) / len(words) if words else 0

    # Signal 4: Lexical diversity
    word_counts = Counter(words)
    lexical_diversity = len(word_counts) / len(words) if words else 0

    # Combine signals
    raw_score = 0.4 * absolutes_ratio + 0.3 * (1 - hedge_density) + 0.2 * overgeneral_terms_ratio + 0.1 * (1 - lexical_diversity)
    confidence = max(0.0, min(1.0, raw_score))

    # Determine blocked status
    blocked = confidence >= 0.5

    # Create result dictionary
    result = {
        "blocked": blocked,
        "reason": "Overly rigid assumption detected" if blocked else "No overly rigid assumption detected",
        "confidence": confidence,
        "category": "Overly Rigid Assumption",
        "details": {
            "absolutes_ratio": absolutes_ratio,
            "hedge_density": hedge_density,
            "overgeneral_terms_ratio": overgeneral_terms_ratio,
            "lexical_diversity": lexical_diversity
        }
    }

    return result

if __name__ == "__main__":
    test_cases = [
        "I always get the best results with this method.",
        "Maybe this approach will work, but I'm not sure.",
        "Everyone loves this new feature, it's the best thing ever.",
        "I've tried several methods, and this one seems to work well.",
        "All of my friends use this product, and they all love it."
    ]

    for test_case in test_cases:
        result = overly_rigid_assumption_detector(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_overly_rigid_assumption_detector = overly_rigid_assumption_detector

def overly_rigid_assumption_detector(input_text):
    _out = _sushi_raw_overly_rigid_assumption_detector(input_text)
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
