import re
from collections import Counter
from typing import Dict
from math import log

def overly_homogeneous_perspective_detector(input_text: str) -> Dict:
    """
    Detects when AI-generated text presents a single, dominant viewpoint without 
    acknowledging potential counterarguments or alternative perspectives, 
    potentially leading to biased or one-sided information.

    This function combines multiple signals to compute a graded confidence score:
    1. Absolute term density: the ratio of absolute terms (e.g., "always", "never") 
       to the total number of words.
    2. Hedge term density: the ratio of hedge terms (e.g., "maybe", "possibly") 
       to the total number of words.
    3. Overgeneral term density: the ratio of overgeneral terms (e.g., "everyone", 
       "nobody") to the total number of words.
    4. Lexical diversity: the ratio of unique words to the total number of words.

    The confidence score is a weighted sum of these signals, clamped to the range [0, 1].

    Args:
    input_text (str): The input text to be analyzed.

    Returns:
    dict: A dictionary containing the following keys:
        - "blocked" (bool): Whether the text is blocked due to overly homogeneous perspective.
        - "reason" (str): The reason for blocking the text.
        - "confidence" (float): The confidence score, ranging from 0 to 1.
        - "category" (str): The category of the detected issue.
        - "details" (dict): Additional details about the detected issue.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Tokenize the input text into words
    words = re.findall(r'\b\w+\b', input_text.lower())

    # Compute the total number of words
    total_words = len(words)

    # Handle the zero/one case
    if total_words <= 1:
        return {
            "blocked": False,
            "reason": "Insufficient text",
            "confidence": 0.0,
            "category": "overly_homogeneous_perspective",
            "details": {}
        }

    # Compute the absolute term density
    absolute_terms = ["always", "never", "all", "none"]
    absolute_term_count = sum(1 for word in words if word in absolute_terms)
    absolute_term_density = absolute_term_count / total_words

    # Compute the hedge term density
    hedge_terms = ["maybe", "possibly", "perhaps", "could", "might"]
    hedge_term_count = sum(1 for word in words if word in hedge_terms)
    hedge_term_density = hedge_term_count / total_words

    # Compute the overgeneral term density
    overgeneral_terms = ["everyone", "nobody", "everybody", "someone", "anyone"]
    overgeneral_term_count = sum(1 for word in words if word in overgeneral_terms)
    overgeneral_term_density = overgeneral_term_count / total_words

    # Compute the lexical diversity
    unique_words = set(words)
    lexical_diversity = len(unique_words) / total_words

    # Compute the raw confidence score
    raw_confidence = 0.5 * absolute_term_density + 0.3 * (1 - hedge_term_density) + 0.2 * overgeneral_term_density

    # Clamp the confidence score to the range [0, 1]
    confidence = max(0.0, min(1.0, raw_confidence))

    # Determine whether the text is blocked
    blocked = confidence > 0.7

    # Return the result
    return {
        "blocked": blocked,
        "reason": "Overly homogeneous perspective detected" if blocked else "No issue detected",
        "confidence": confidence,
        "category": "overly_homogeneous_perspective",
        "details": {
            "absolute_term_density": absolute_term_density,
            "hedge_term_density": hedge_term_density,
            "overgeneral_term_density": overgeneral_term_density,
            "lexical_diversity": lexical_diversity
        }
    }

if __name__ == "__main__":
    test_cases = [
        "The new policy is always a good idea.",
        "Maybe the new policy is a good idea, but we should consider the potential drawbacks.",
        "Everyone loves the new policy, and nobody has any complaints.",
        "The new policy is never a good idea, and we should always reject it.",
        "The new policy is a good idea, but we should consider the potential risks and benefits.",
        "The new policy is a bad idea, and we should never implement it.",
        "The new policy is a good idea, and everyone will love it.",
        "The new policy is a bad idea, and nobody will like it.",
        "The new policy is a good idea, but we should consider the potential consequences.",
        "The new policy is a bad idea, and we should always reject it."
    ]

    for test_case in test_cases:
        result = overly_homogeneous_perspective_detector(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_overly_homogeneous_perspective_detector = overly_homogeneous_perspective_detector

def overly_homogeneous_perspective_detector(input_text):
    _out = _sushi_raw_overly_homogeneous_perspective_detector(input_text)
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
