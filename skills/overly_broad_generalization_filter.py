import re
from typing import Dict

def overly_broad_generalization_filter(input_text: str) -> Dict:
    """
    Detects and flags instances where AI output contains overly broad generalizations,
    such as absolute statements or universal claims, to prevent humans from overrelying
    on simplistic or inaccurate information. It aims to encourage more nuanced and
    critical thinking.

    Args:
        input_text (str): The text to be analyzed.

    Returns:
        Dict: A dictionary containing the results of the analysis.
            - "blocked" (bool): Whether the input text contains overly broad generalizations.
            - "reason" (str): The reason for the blocking decision.
            - "confidence" (float): A graded confidence score between 0.0 and 1.0.
            - "category" (str): The category of the detected generalization.
            - "details" (dict): Additional details about the detected generalization.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Initialize the results dictionary
    results = {
        "blocked": False,
        "reason": "",
        "confidence": 0.0,
        "category": "",
        "details": {}
    }

    # Define absolute terms and overgeneral terms
    absolute_terms = ["always", "never", "all", "every", "none"]
    overgeneral_terms = ["everyone", "everything", "anyone", "anything"]

    # Calculate the ratio of absolute terms to total words
    words = re.findall(r"\b\w+\b", input_text.lower())
    absolute_count = sum(1 for word in words if word in absolute_terms)
    absolutes_ratio = absolute_count / len(words) if words else 0.0

    # Calculate the hedge density
    hedge_terms = ["maybe", "perhaps", "possibly", "probably"]
    hedge_count = sum(1 for word in words if word in hedge_terms)
    hedge_density = hedge_count / len(words) if words else 0.0

    # Calculate the overgeneral term density
    overgeneral_count = sum(1 for word in words if word in overgeneral_terms)
    overgeneral_density = overgeneral_count / len(words) if words else 0.0

    # Calculate the raw confidence score
    raw_confidence = 0.5 * absolutes_ratio + 0.3 * (1 - hedge_density) + 0.2 * overgeneral_density

    # Clamp the confidence score to [0.0, 1.0]
    confidence = max(0.0, min(1.0, raw_confidence))

    # Determine the blocking decision
    results["blocked"] = confidence >= 0.5

    # Set the reason and category
    if results["blocked"]:
        results["reason"] = "Overly broad generalization detected"
        results["category"] = "Absolute statement"
    else:
        results["reason"] = "No overly broad generalization detected"
        results["category"] = "Benign statement"

    # Set the confidence and details
    results["confidence"] = confidence
    results["details"] = {
        "absolutes_ratio": absolutes_ratio,
        "hedge_density": hedge_density,
        "overgeneral_density": overgeneral_density
    }

    return results


if __name__ == "__main__":
    test_cases = [
        "I always eat breakfast.",
        "Maybe I'll go to the store later.",
        "Everyone loves ice cream.",
        "The sun rises in the east and sets in the west.",
        "It's possible that it will rain tomorrow.",
        "All humans are mortal.",
        "I never eat vegetables.",
        "The book is on the table.",
        "The cat is sleeping.",
        "The dog is barking loudly."
    ]

    for test_case in test_cases:
        print(overly_broad_generalization_filter(test_case))

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_overly_broad_generalization_filter = overly_broad_generalization_filter

def overly_broad_generalization_filter(input_text):
    _out = _sushi_raw_overly_broad_generalization_filter(input_text)
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
