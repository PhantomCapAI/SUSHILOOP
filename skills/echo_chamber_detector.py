import re
from typing import Dict
from dataclasses import dataclass
from collections import Counter
import math

@dataclass
class EchoChamberDetectionResult:
    blocked: bool
    reason: str
    confidence: float
    category: str
    details: Dict[str, float]

def echo_chamber_detector(input_text: str) -> Dict:
    """
    Detects and flags instances where AI-generated responses reinforce a single perspective or idea without providing alternative viewpoints.

    This function combines multiple signals to detect echo chambers, including:
    - Absolute term density: The ratio of absolute terms (e.g., "always", "never") to total words.
    - Hedge term density: The ratio of hedge terms (e.g., "maybe", "possibly") to total words.
    - Overgeneralization term density: The ratio of overgeneralization terms (e.g., "everyone", "nobody") to total words.
    - Lexical diversity: The ratio of unique words to total words.

    The confidence score is a weighted sum of these signals, clamped to the range [0.0, 1.0].
    The `blocked` flag is set to True if the confidence score exceeds a threshold of 0.5.

    Args:
        input_text (str): The input text to analyze.

    Returns:
        Dict: A dictionary containing the detection result, including `blocked`, `reason`, `confidence`, `category`, and `details`.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Tokenize the input text into words
    words = re.findall(r'\b\w+\b', input_text.lower())

    # Count the total number of words
    total_words = len(words)

    # Count the number of absolute terms
    absolute_terms = len([word for word in words if word in ["always", "never", "all", "none"]])

    # Count the number of hedge terms
    hedge_terms = len([word for word in words if word in ["maybe", "possibly", "perhaps", "could"]])

    # Count the number of overgeneralization terms
    overgeneralization_terms = len([word for word in words if word in ["everyone", "nobody", "everybody", "noone"]])

    # Calculate the absolute term density
    absolute_term_density = absolute_terms / total_words if total_words > 0 else 0.0

    # Calculate the hedge term density
    hedge_term_density = hedge_terms / total_words if total_words > 0 else 0.0

    # Calculate the overgeneralization term density
    overgeneralization_term_density = overgeneralization_terms / total_words if total_words > 0 else 0.0

    # Calculate the lexical diversity
    lexical_diversity = len(set(words)) / total_words if total_words > 0 else 0.0

    # Calculate the weighted sum of the signals
    raw_score = 0.4 * absolute_term_density + 0.3 * (1 - hedge_term_density) + 0.2 * overgeneralization_term_density + 0.1 * (1 - lexical_diversity)

    # Clamp the confidence score to the range [0.0, 1.0]
    confidence = max(0.0, min(1.0, raw_score))

    # Set the blocked flag based on the confidence score
    blocked = confidence >= 0.5

    # Create the detection result
    result = EchoChamberDetectionResult(
        blocked=blocked,
        reason="Echo chamber detected" if blocked else "No echo chamber detected",
        confidence=confidence,
        category="echo_chamber",
        details={
            "absolute_term_density": absolute_term_density,
            "hedge_term_density": hedge_term_density,
            "overgeneralization_term_density": overgeneralization_term_density,
            "lexical_diversity": lexical_diversity,
        },
    )

    # Return the detection result as a dictionary
    return {
        "blocked": result.blocked,
        "reason": result.reason,
        "confidence": result.confidence,
        "category": result.category,
        "details": result.details,
    }

if __name__ == "__main__":
    test_cases = [
        "I always think that everyone should do what I say.",
        "Maybe we should consider alternative perspectives.",
        "Nobody is perfect, but everyone can try to be better.",
        "All people are equal, and everyone deserves respect.",
        "The sun is always shining, and it's never cloudy.",
    ]

    for test_case in test_cases:
        result = echo_chamber_detector(test_case)
        print(f"Input: {test_case}")
        print(f"Blocked: {result['blocked']}")
        print(f"Reason: {result['reason']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Category: {result['category']}")
        print(f"Details: {result['details']}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_echo_chamber_detector = echo_chamber_detector

def echo_chamber_detector(input_text):
    _out = _sushi_raw_echo_chamber_detector(input_text)
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
