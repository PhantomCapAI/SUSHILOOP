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

def self_harm_routing_guard(input_text: str) -> Dict:
    """
    Detects distress signals in the input text and ensures the path to human/professional support is surfaced.

    The model combines multiple signals to detect distress, including:
    - Absolute term density: the ratio of absolute terms (e.g., "always", "never") to total words
    - Hedge density: the ratio of hedge terms (e.g., "maybe", "possibly") to total words
    - Overgeneralization term density: the ratio of overgeneralization terms (e.g., "everyone", "nobody") to total words
    - Sentence complexity: the average number of clauses per sentence

    The confidence score is a weighted sum of these signals, clamped to the range [0.0, 1.0].
    The `blocked` flag is set to True if the confidence score exceeds a threshold of 0.5.

    :param input_text: The input text to analyze
    :return: A dictionary containing the detection result, including the `blocked` flag, `reason`, `confidence` score, `category`, and `details`
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Tokenize the input text into words
    words = re.findall(r'\b\w+\b', input_text.lower())

    # Calculate the absolute term density
    absolute_terms = ["always", "never", "all", "none"]
    absolute_term_count = sum(1 for word in words if word in absolute_terms)
    absolute_term_density = absolute_term_count / len(words) if words else 0.0

    # Calculate the hedge density
    hedge_terms = ["maybe", "possibly", "perhaps", "could"]
    hedge_term_count = sum(1 for word in words if word in hedge_terms)
    hedge_density = hedge_term_count / len(words) if words else 0.0

    # Calculate the overgeneralization term density
    overgeneralization_terms = ["everyone", "nobody", "everybody", "noone"]
    overgeneralization_term_count = sum(1 for word in words if word in overgeneralization_terms)
    overgeneralization_term_density = overgeneralization_term_count / len(words) if words else 0.0

    # Calculate the sentence complexity
    sentences = re.split(r'[.!?]', input_text)
    sentence_complexity = sum(len(re.findall(r'\b\w+\b', sentence)) for sentence in sentences) / len(sentences) if sentences else 0.0

    # Calculate the weighted sum of the signals
    raw_score = 0.4 * absolute_term_density + 0.3 * hedge_density + 0.2 * overgeneralization_term_density + 0.1 * sentence_complexity

    # Clamp the confidence score to the range [0.0, 1.0]
    confidence = max(0.0, min(1.0, raw_score))

    # Set the blocked flag based on the confidence score
    blocked = confidence >= 0.5

    # Create the detection result dictionary
    result = {
        "blocked": blocked,
        "reason": "Distress signals detected" if blocked else "No distress signals detected",
        "confidence": confidence,
        "category": "Self-harm" if blocked else "Benign",
        "details": {
            "absolute_term_density": absolute_term_density,
            "hedge_density": hedge_density,
            "overgeneralization_term_density": overgeneralization_term_density,
            "sentence_complexity": sentence_complexity
        }
    }

    return result

if __name__ == "__main__":
    test_cases = [
        "I'm feeling really down and I don't know what to do.",
        "I'm just having a bad day, but I'll be fine.",
        "I've been feeling hopeless for weeks and I don't see a way out.",
        "I'm just tired and need to get some rest.",
        "I've been thinking about ending it all, but I don't know if I can go through with it."
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
