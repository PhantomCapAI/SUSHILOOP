import re
from typing import Dict

def ambiguous_hypothesis_alert(input_text: str) -> Dict:
    """
    Detects and flags instances where AI-generated text presents a hypothesis as fact without sufficient evidence.

    This skill protects human cognition by preventing the unconscious acceptance of unverified hypotheses, 
    encouraging critical thinking and skepticism when evaluating AI-generated information.

    Args:
    input_text (str): The AI-generated text to be evaluated.

    Returns:
    dict: A dictionary containing the following keys:
        - blocked (bool): Whether the input text has been flagged as presenting a hypothesis as fact without sufficient evidence.
        - reason (str): The reason for flagging the input text.
        - confidence (float): A graded confidence score between 0.0 and 1.0 indicating the strength of the signal.
        - category (str): The category of the signal (e.g., "ambiguous hypothesis").
        - details (dict): Additional details about the signal, including the ratios of absolute terms, hedge terms, and overgeneral terms.

    Mission alignment:
    This skill aligns with the mission of protecting human cognition by preventing the unconscious acceptance of unverified hypotheses.
    It encourages critical thinking and skepticism when evaluating AI-generated information.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Initialize variables
    absolute_terms = ["clearly", "obviously", "it is clear that", "it is obvious that"]
    hedge_terms = ["may", "might", "could", "possibly", "potentially"]
    overgeneral_terms = ["always", "never", "every", "all"]

    # Calculate the ratio of absolute terms
    absolute_ratio = sum(1 for term in absolute_terms if term in input_text.lower()) / (len(input_text.split()) + 1)
    if absolute_ratio > 1:
        absolute_ratio = 1

    # Calculate the ratio of hedge terms
    hedge_ratio = sum(1 for term in hedge_terms if term in input_text.lower()) / (len(input_text.split()) + 1)
    if hedge_ratio > 1:
        hedge_ratio = 1

    # Calculate the ratio of overgeneral terms
    overgeneral_ratio = sum(1 for term in overgeneral_terms if term in input_text.lower()) / (len(input_text.split()) + 1)
    if overgeneral_ratio > 1:
        overgeneral_ratio = 1

    # Calculate the confidence score
    raw_score = 0.5 * absolute_ratio + 0.3 * (1 - hedge_ratio) + 0.2 * overgeneral_ratio
    confidence = max(0.0, min(1.0, raw_score))

    # Determine whether the input text has been flagged
    blocked = confidence >= 0.5

    # Create the output dictionary
    output = {
        "blocked": blocked,
        "reason": "Ambiguous hypothesis detected" if blocked else "No ambiguous hypothesis detected",
        "confidence": confidence,
        "category": "ambiguous hypothesis",
        "details": {
            "absolute_ratio": absolute_ratio,
            "hedge_ratio": hedge_ratio,
            "overgeneral_ratio": overgeneral_ratio
        }
    }

    return output


if __name__ == "__main__":
    test_cases = [
        "It is clear that the sky is blue.",
        "The sky is blue, but it may be gray on some days.",
        "The sky is always blue.",
        "The sky is blue, and it is obvious that it is a beautiful color.",
        "The sky is blue, but it could be gray on some days.",
        "The sky is blue, and it is clear that it is a beautiful color, but it may be gray on some days."
    ]

    for test_case in test_cases:
        print(ambiguous_hypothesis_alert(test_case))

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_ambiguous_hypothesis_alert = ambiguous_hypothesis_alert

def ambiguous_hypothesis_alert(input_text):
    _out = _sushi_raw_ambiguous_hypothesis_alert(input_text)
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
