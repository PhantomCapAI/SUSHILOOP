import re
import math
from typing import Dict

def self_harm_routing_guard(input_text: str) -> Dict:
    """
    Detects distress signals in input text and ensures the path to human/professional support is surfaced.

    This function combines multiple signals to detect potential self-harm routing, including:
    - Absolute term density
    - Hedge term density
    - Overgeneralization term density
    - Sentence structure and complexity

    The function returns a dictionary with the following keys:
    - blocked: A boolean indicating whether the input text is likely to be self-harm routing
    - reason: A string describing the reason for the detection
    - confidence: A float between 0.0 and 1.0 representing the confidence in the detection
    - category: A string categorizing the type of self-harm routing detected
    - details: A dictionary with additional details about the detection

    :param input_text: The input text to be analyzed
    :return: A dictionary with the detection results
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Define absolute terms
    absolute_terms = ["always", "never", "every", "all"]

    # Define hedge terms
    hedge_terms = ["maybe", "perhaps", "possibly", "probably"]

    # Define overgeneralization terms
    overgeneral_terms = ["everyone", "nobody", "nothing", "everything"]

    # Calculate absolute term density
    absolute_term_count = sum(1 for term in absolute_terms if term in input_text.lower())
    absolute_term_ratio = absolute_term_count / (len(input_text.split()) + 1e-6)  # Guard against division by zero

    # Calculate hedge term density
    hedge_term_count = sum(1 for term in hedge_terms if term in input_text.lower())
    hedge_term_ratio = hedge_term_count / (len(input_text.split()) + 1e-6)  # Guard against division by zero

    # Calculate overgeneralization term density
    overgeneral_term_count = sum(1 for term in overgeneral_terms if term in input_text.lower())
    overgeneral_term_ratio = overgeneral_term_count / (len(input_text.split()) + 1e-6)  # Guard against division by zero

    # Calculate sentence structure and complexity
    sentences = re.split(r'[.!?]', input_text)
    sentence_count = len([sentence for sentence in sentences if sentence.strip()])
    sentence_length = sum(len(sentence.split()) for sentence in sentences) / (sentence_count + 1e-6)  # Guard against division by zero

    # Combine signals to calculate confidence
    raw_confidence = 0.4 * absolute_term_ratio + 0.3 * hedge_term_ratio + 0.2 * overgeneral_term_ratio + 0.1 * (sentence_length / (sentence_count + 1e-6))
    confidence = max(0.0, min(1.0, raw_confidence))

    # Determine blocked status based on confidence threshold
    blocked = confidence >= 0.5

    # Return detection results
    return {
        "blocked": blocked,
        "reason": "Detected potential self-harm routing" if blocked else "No self-harm routing detected",
        "confidence": confidence,
        "category": "Self-Harm Routing" if blocked else "Benign",
        "details": {
            "absolute_term_ratio": absolute_term_ratio,
            "hedge_term_ratio": hedge_term_ratio,
            "overgeneral_term_ratio": overgeneral_term_ratio,
            "sentence_length": sentence_length,
            "sentence_count": sentence_count
        }
    }

if __name__ == "__main__":
    test_cases = [
        "I'm feeling really down and I don't know what to do.",
        "I'm just having a bad day, but I'll be fine tomorrow.",
        "Everyone hates me and I'm all alone.",
        "I'm not sure what's going on, but I think I need some help.",
        "I'm feeling really overwhelmed and I don't know how to cope.",
        "I'm just tired and I need to get some rest.",
        "I'm so angry and I don't know what to do with myself.",
        "I'm feeling really sad and I just want to talk to someone."
    ]

    for test_case in test_cases:
        print(self_harm_routing_guard(test_case))

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
