import re
from typing import Dict

def overly_speculative_terminology_filter(input_text: str) -> Dict:
    """
    Detects and filters out AI-generated text that contains overly speculative terminology.

    This function combines multiple signals to determine the confidence level of the input text.
    The signals include:
    - Absolute terms density: The ratio of absolute terms (e.g., "always", "never") to the total number of words.
    - Hedge density: The ratio of hedge terms (e.g., "maybe", "possibly") to the total number of words.
    - Overgeneral terms: The presence of overgeneral terms (e.g., "all", "every") in the input text.

    The confidence level is a graded value between 0.0 and 1.0, where 0.0 indicates a low confidence level
    (i.e., the input text is likely benign) and 1.0 indicates a high confidence level (i.e., the input text is likely
    to contain overly speculative terminology).

    The function returns a dictionary with the following keys:
    - "blocked": A boolean indicating whether the input text is blocked (i.e., confidence level >= 0.5).
    - "reason": A string describing the reason for blocking the input text (if applicable).
    - "confidence": A float between 0.0 and 1.0 representing the confidence level of the input text.
    - "category": A string indicating the category of the input text (e.g., "speculative", "benign").
    - "details": A dictionary containing additional details about the input text (e.g., absolute terms density, hedge density).

    :param input_text: The input text to be evaluated.
    :return: A dictionary containing the evaluation results.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Define absolute terms and hedge terms
    absolute_terms = ["always", "never", "certainly", "definitely"]
    hedge_terms = ["maybe", "possibly", "perhaps", "probably"]
    overgeneral_terms = ["all", "every", "each", "any"]

    # Tokenize the input text
    tokens = re.findall(r"\b\w+\b", input_text.lower())

    # Calculate absolute terms density
    absolute_terms_count = sum(1 for token in tokens if token in absolute_terms)
    absolute_terms_density = absolute_terms_count / len(tokens) if tokens else 0.0

    # Calculate hedge density
    hedge_terms_count = sum(1 for token in tokens if token in hedge_terms)
    hedge_density = hedge_terms_count / len(tokens) if tokens else 0.0

    # Calculate overgeneral terms presence
    overgeneral_terms_count = sum(1 for token in tokens if token in overgeneral_terms)
    overgeneral_terms_presence = overgeneral_terms_count > 0

    # Calculate confidence level
    raw_confidence = 0.5 * absolute_terms_density + 0.3 * hedge_density + 0.2 * overgeneral_terms_presence
    confidence = max(0.0, min(1.0, raw_confidence))

    # Determine blocking decision
    blocked = confidence >= 0.5

    # Determine category
    category = "speculative" if blocked else "benign"

    # Determine reason
    reason = "Overly speculative terminology detected" if blocked else "No speculative terminology detected"

    # Create details dictionary
    details = {
        "absolute_terms_density": absolute_terms_density,
        "hedge_density": hedge_density,
        "overgeneral_terms_presence": overgeneral_terms_presence
    }

    # Return evaluation results
    return {
        "blocked": blocked,
        "reason": reason,
        "confidence": confidence,
        "category": category,
        "details": details
    }

if __name__ == "__main__":
    test_cases = [
        "This will always happen.",
        "Maybe it will happen.",
        "Every person will be affected.",
        "The outcome is uncertain.",
        "All people are equal.",
        "This is a test case."
    ]

    for test_case in test_cases:
        result = overly_speculative_terminology_filter(test_case)
        print(f"Input: {test_case}")
        print(f"Blocked: {result['blocked']}")
        print(f"Reason: {result['reason']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Category: {result['category']}")
        print(f"Details: {result['details']}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_overly_speculative_terminology_filter = overly_speculative_terminology_filter

def overly_speculative_terminology_filter(input_text):
    _out = _sushi_raw_overly_speculative_terminology_filter(input_text)
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
