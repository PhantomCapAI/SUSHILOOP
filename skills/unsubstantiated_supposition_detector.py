import re
from typing import Dict

def unsubstantiated_supposition_detector(input_text: str) -> Dict:
    """
    Detects and flags instances where AI-generated text presents unsubstantiated suppositions as facts.

    This function combines multiple signals to determine the confidence of unsubstantiated suppositions in the input text.
    The signals used are:
    - Absolute terms density: The ratio of absolute terms (e.g., "always", "never") to the total number of words.
    - Hedge terms density: The ratio of hedge terms (e.g., "maybe", "possibly") to the total number of words.
    - Overgeneralization terms density: The ratio of overgeneralization terms (e.g., "everyone", "all") to the total number of words.
    - Sentence complexity: The average number of clauses per sentence.

    The confidence is calculated as a weighted sum of these signals and is clamped to the range [0.0, 1.0].
    The `blocked` flag is set to True if the confidence is greater than or equal to 0.5.

    Args:
        input_text (str): The input text to be analyzed.

    Returns:
        Dict: A dictionary containing the results of the analysis, including the `blocked` flag, `reason`, `confidence`, `category`, and `details`.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Tokenize the input text into words
    words = re.findall(r'\b\w+\b', input_text.lower())

    # Calculate the absolute terms density
    absolute_terms = ["always", "never", "clearly", "obviously"]
    absolute_terms_count = sum(1 for word in words if word in absolute_terms)
    absolute_terms_ratio = absolute_terms_count / len(words) if words else 0.0

    # Calculate the hedge terms density
    hedge_terms = ["maybe", "possibly", "perhaps", "could"]
    hedge_terms_count = sum(1 for word in words if word in hedge_terms)
    hedge_terms_ratio = hedge_terms_count / len(words) if words else 0.0

    # Calculate the overgeneralization terms density
    overgeneralization_terms = ["everyone", "all", "every", "any"]
    overgeneralization_terms_count = sum(1 for word in words if word in overgeneralization_terms)
    overgeneralization_terms_ratio = overgeneralization_terms_count / len(words) if words else 0.0

    # Calculate the sentence complexity
    sentences = re.split(r'[.!?]', input_text)
    clauses_per_sentence = [len(re.findall(r'\b\w+\b', sentence)) for sentence in sentences if sentence]
    average_clauses_per_sentence = sum(clauses_per_sentence) / len(clauses_per_sentence) if clauses_per_sentence else 0.0

    # Calculate the confidence
    raw_confidence = 0.5 * absolute_terms_ratio + 0.3 * (1 - hedge_terms_ratio) + 0.2 * overgeneralization_terms_ratio
    confidence = max(0.0, min(1.0, raw_confidence))

    # Determine the blocked flag
    blocked = confidence >= 0.5

    # Create the result dictionary
    result = {
        "blocked": blocked,
        "reason": "Unsubstantiated suppositions detected" if blocked else "No unsubstantiated suppositions detected",
        "confidence": confidence,
        "category": "Unsubstantiated Suppositions",
        "details": {
            "absolute_terms_ratio": absolute_terms_ratio,
            "hedge_terms_ratio": hedge_terms_ratio,
            "overgeneralization_terms_ratio": overgeneralization_terms_ratio,
            "average_clauses_per_sentence": average_clauses_per_sentence
        }
    }

    return result


if __name__ == "__main__":
    test_cases = [
        "The new policy is clearly a good idea.",
        "Maybe the new policy is a good idea, but we need more information.",
        "Everyone loves the new policy, and it's obviously the best choice.",
        "The new policy has some potential benefits, but it also has some drawbacks.",
        "All of the experts agree that the new policy is the best option."
    ]

    for test_case in test_cases:
        result = unsubstantiated_supposition_detector(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_unsubstantiated_supposition_detector = unsubstantiated_supposition_detector

def unsubstantiated_supposition_detector(input_text):
    _out = _sushi_raw_unsubstantiated_supposition_detector(input_text)
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
