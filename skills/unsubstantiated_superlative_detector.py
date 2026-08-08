import re
from typing import Dict

def unsubstantiated_superlative_detector(input_text: str) -> Dict:
    """
    Detects and flags instances where absolute or superlative language is used without evidence or justification.

    This skill protects human cognition by preventing the spread of unsubstantiated claims and promoting critical thinking.
    By flagging absolute language, it encourages users to seek out evidence and consider alternative perspectives, rather than relying on unverified assertions.

    Args:
        input_text (str): The text to analyze.

    Returns:
        dict: A dictionary containing the results of the analysis, including:
            - blocked (bool): Whether the text contains unsubstantiated superlatives.
            - reason (str): A brief explanation of the reason for the flag.
            - confidence (float): A graded confidence score between 0.0 and 1.0.
            - category (str): The category of the flag (in this case, "Unsubstantiated Superlative").
            - details (dict): Additional details about the analysis, including the ratios of absolute terms and hedging terms.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Define regular expressions for absolute terms and hedging terms
    absolute_terms = re.compile(r"\b(the|most|best|greatest|always|never)\b", re.IGNORECASE)
    hedging_terms = re.compile(r"\b(maybe|perhaps|possibly|likely|unlikely)\b", re.IGNORECASE)

    # Count the number of absolute terms and hedging terms
    absolute_count = len(absolute_terms.findall(input_text))
    hedging_count = len(hedging_terms.findall(input_text))

    # Calculate the ratio of absolute terms to total words
    words = input_text.split()
    if len(words) > 0:
        absolute_ratio = absolute_count / len(words)
    else:
        absolute_ratio = 0.0

    # Calculate the ratio of hedging terms to total words
    if len(words) > 0:
        hedging_ratio = hedging_count / len(words)
    else:
        hedging_ratio = 0.0

    # Calculate the confidence score
    raw_score = 0.5 * absolute_ratio + 0.3 * (1 - hedging_ratio) + 0.2 * (absolute_count > 0)
    confidence = max(0.0, min(1.0, raw_score))

    # Determine whether the text is blocked
    blocked = confidence >= 0.5

    # Create the result dictionary
    result = {
        "blocked": blocked,
        "reason": "Unsubstantiated superlative language detected" if blocked else "No unsubstantiated superlative language detected",
        "confidence": confidence,
        "category": "Unsubstantiated Superlative",
        "details": {
            "absolute_ratio": absolute_ratio,
            "hedging_ratio": hedging_ratio,
            "absolute_count": absolute_count,
            "hedging_count": hedging_count
        }
    }

    return result


if __name__ == "__main__":
    test_cases = [
        "This is the best product on the market.",
        "I'm not sure if this is the best product, but it's definitely good.",
        "The new policy is always effective.",
        "The new policy is likely to be effective, but we need to monitor its impact.",
        "This product is the greatest thing since sliced bread.",
        "I think this product is pretty good, but I'm not sure if it's the best.",
        "The company always delivers on time.",
        "The company usually delivers on time, but there have been some exceptions."
    ]

    for test_case in test_cases:
        result = unsubstantiated_superlative_detector(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_unsubstantiated_superlative_detector = unsubstantiated_superlative_detector

def unsubstantiated_superlative_detector(input_text):
    _out = _sushi_raw_unsubstantiated_superlative_detector(input_text)
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
