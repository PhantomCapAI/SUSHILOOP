import re
from math import log
from typing import Dict

def premature_simplification_detector(input_text: str) -> Dict:
    """
    Detects when a user's input oversimplifies a complex issue, potentially leading to incomplete or inaccurate AI responses,
    and prompts the user to consider additional factors.

    This function combines multiple signals to determine the confidence of premature simplification:
    - Absolute term density: The ratio of absolute terms (e.g., "always", "never") to the total number of words.
    - Hedge term density: The ratio of hedge terms (e.g., "maybe", "possibly") to the total number of words.
    - Overgeneral term density: The ratio of overgeneral terms (e.g., "everyone", "everything") to the total number of words.
    - Sentence complexity: The ratio of complex sentences (e.g., sentences with multiple clauses) to the total number of sentences.

    The confidence is calculated as a weighted sum of these signals and is clamped to the range [0.0, 1.0].

    Args:
        input_text (str): The user's input text.

    Returns:
        Dict: A dictionary containing the following keys:
            - "blocked" (bool): Whether the input text is blocked due to premature simplification.
            - "reason" (str): The reason for blocking the input text.
            - "confidence" (float): The confidence of premature simplification, ranging from 0.0 to 1.0.
            - "category" (str): The category of the input text (e.g., "oversimplified", "complex").
            - "details" (Dict): Additional details about the input text, including the absolute term density, hedge term density, overgeneral term density, and sentence complexity.
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

    # Calculate the hedge term density
    hedge_terms = ["maybe", "possibly", "perhaps", "could", "might"]
    hedge_term_count = sum(1 for word in words if word in hedge_terms)
    hedge_term_density = hedge_term_count / len(words) if words else 0.0

    # Calculate the overgeneral term density
    overgeneral_terms = ["everyone", "everything", "everywhere", "always", "never"]
    overgeneral_term_count = sum(1 for word in words if word in overgeneral_terms)
    overgeneral_term_density = overgeneral_term_count / len(words) if words else 0.0

    # Calculate the sentence complexity
    sentences = re.split(r'[.!?]', input_text)
    complex_sentence_count = sum(1 for sentence in sentences if len(re.findall(r'\b\w+\b', sentence)) > 10)
    sentence_complexity = complex_sentence_count / len(sentences) if sentences else 0.0

    # Calculate the confidence of premature simplification
    raw_confidence = 0.5 * absolute_term_density + 0.3 * (1 - hedge_term_density) + 0.2 * overgeneral_term_density
    confidence = max(0.0, min(1.0, raw_confidence))

    # Determine the blocking status and reason
    blocked = confidence > 0.7
    reason = "Premature simplification detected" if blocked else "No premature simplification detected"

    # Determine the category
    category = "oversimplified" if blocked else "complex"

    # Create the details dictionary
    details = {
        "absolute_term_density": absolute_term_density,
        "hedge_term_density": hedge_term_density,
        "overgeneral_term_density": overgeneral_term_density,
        "sentence_complexity": sentence_complexity
    }

    # Return the result
    return {
        "blocked": blocked,
        "reason": reason,
        "confidence": confidence,
        "category": category,
        "details": details
    }

if __name__ == "__main__":
    test_cases = [
        "I always get what I want.",
        "Maybe I'll go to the store.",
        "Everyone loves this product.",
        "The sun is shining, and the birds are singing.",
        "This is a very complex issue that requires careful consideration."
    ]

    for test_case in test_cases:
        result = premature_simplification_detector(test_case)
        print(f"Input: {test_case}")
        print(f"Blocked: {result['blocked']}")
        print(f"Reason: {result['reason']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Category: {result['category']}")
        print(f"Details: {result['details']}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_premature_simplification_detector = premature_simplification_detector

def premature_simplification_detector(input_text):
    _out = _sushi_raw_premature_simplification_detector(input_text)
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
