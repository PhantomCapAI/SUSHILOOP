import re
from typing import Dict

def overly_broad_statement_detector(input_text: str) -> Dict:
    """
    Detects and flags AI-generated responses that contain overly broad or absolute statements.

    This function combines multiple signals to determine the confidence of a statement being overly broad.
    It checks for absolute language, hedge density, and overgeneral terms to promote more thoughtful engagement with AI outputs.

    Args:
        input_text (str): The input text to be evaluated.

    Returns:
        Dict: A dictionary containing the results of the evaluation, including a boolean indicating whether the statement is blocked,
              a reason for the block, a confidence score, a category, and additional details.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Initialize the result dictionary
    result = {
        "blocked": False,
        "reason": "",
        "confidence": 0.0,
        "category": "overly_broad_statement",
        "details": {}
    }

    # Split the input text into sentences
    sentences = re.split(r'[.!?]', input_text)

    # Remove empty sentences
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    # Check if there are no sentences
    if not sentences:
        return result

    # Initialize counters for absolute language and hedge density
    absolute_count = 0
    hedge_count = 0
    overgeneral_terms = 0

    # Define patterns for absolute language and hedge density
    absolute_patterns = [r"\b(always|never|everyone|everything)\b"]
    hedge_patterns = [r"\b(maybe|perhaps|possibly|likely|unlikely)\b"]
    overgeneral_terms_patterns = [r"\b(best|worst|greatest|least)\b"]

    # Iterate over each sentence
    for sentence in sentences:
        # Check for absolute language
        for pattern in absolute_patterns:
            absolute_count += len(re.findall(pattern, sentence, re.IGNORECASE))

        # Check for hedge density
        for pattern in hedge_patterns:
            hedge_count += len(re.findall(pattern, sentence, re.IGNORECASE))

        # Check for overgeneral terms
        for pattern in overgeneral_terms_patterns:
            overgeneral_terms += len(re.findall(pattern, sentence, re.IGNORECASE))

    # Calculate the absolute language ratio
    absolute_ratio = absolute_count / (len(sentences) * len(absolute_patterns))

    # Calculate the hedge density
    hedge_density = hedge_count / (len(sentences) * len(hedge_patterns)) if hedge_count > 0 else 0

    # Calculate the overgeneral terms ratio
    overgeneral_terms_ratio = overgeneral_terms / (len(sentences) * len(overgeneral_terms_patterns))

    # Calculate the raw confidence score
    raw_confidence = 0.5 * absolute_ratio + 0.3 * (1 - hedge_density) + 0.2 * overgeneral_terms_ratio

    # Clamp the confidence score to [0.0, 1.0]
    confidence = max(0.0, min(1.0, raw_confidence))

    # Update the result dictionary
    result["confidence"] = confidence
    result["blocked"] = confidence >= 0.5
    result["reason"] = "Overly broad statement detected" if result["blocked"] else "No overly broad statement detected"
    result["details"] = {
        "absolute_ratio": absolute_ratio,
        "hedge_density": hedge_density,
        "overgeneral_terms_ratio": overgeneral_terms_ratio
    }

    return result


if __name__ == "__main__":
    test_cases = [
        "This is the best solution.",
        "Maybe this solution is good, but it's not perfect.",
        "Everyone will love this solution.",
        "This solution is never going to work.",
        "Perhaps this solution is worth considering.",
        "This is the greatest solution ever.",
        "I'm not sure if this solution is good or not.",
        "This solution is always the best choice.",
        "This solution is likely to fail.",
        "This solution is possibly the worst idea ever."
    ]

    for test_case in test_cases:
        print(overly_broad_statement_detector(test_case))

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_overly_broad_statement_detector = overly_broad_statement_detector

def overly_broad_statement_detector(input_text):
    _out = _sushi_raw_overly_broad_statement_detector(input_text)
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
