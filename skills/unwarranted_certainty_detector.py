import re
from typing import Dict

def unwarranted_certainty_detector(input_text: str) -> Dict:
    """
    Detects instances of unwarranted certainty in AI-generated text.

    This function combines multiple signals to detect phrases that imply absolute confidence or universality.
    It provides clear and actionable feedback to users on how to rephrase or reevaluate uncertain statements.

    Args:
        input_text (str): The input text to be evaluated.

    Returns:
        Dict: A dictionary containing the results of the evaluation, including:
            - blocked (bool): Whether the input text contains unwarranted certainty.
            - reason (str): A brief explanation of the reason for the evaluation result.
            - confidence (float): A graded confidence score between 0.0 and 1.0.
            - category (str): The category of the evaluation result.
            - details (Dict): Additional details about the evaluation result.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Define regular expression patterns for absolute terms and hedging terms
    absolute_terms = re.compile(r"\b(always|never|everyone|nobody|all|none)\b", re.IGNORECASE)
    hedging_terms = re.compile(r"\b(maybe|perhaps|possibly|likely|unlikely)\b", re.IGNORECASE)
    overgeneral_terms = re.compile(r"\b(every|all|any|each)\b", re.IGNORECASE)

    # Split the input text into sentences
    sentences = re.split(r"[.!?]", input_text)

    # Initialize counters for absolute terms, hedging terms, and overgeneral terms
    absolute_count = 0
    hedging_count = 0
    overgeneral_count = 0

    # Iterate over each sentence
    for sentence in sentences:
        # Count absolute terms
        absolute_count += len(absolute_terms.findall(sentence))

        # Count hedging terms
        hedging_count += len(hedging_terms.findall(sentence))

        # Count overgeneral terms
        overgeneral_count += len(overgeneral_terms.findall(sentence))

    # Calculate the ratio of absolute terms to total terms
    total_terms = len(re.findall(r"\b\w+\b", input_text))
    if total_terms == 0:
        absolute_ratio = 0.0
    else:
        absolute_ratio = absolute_count / total_terms

    # Calculate the density of hedging terms
    if len(sentences) == 0:
        hedging_density = 0.0
    else:
        hedging_density = hedging_count / len(sentences)

    # Calculate the ratio of overgeneral terms to total terms
    if total_terms == 0:
        overgeneral_ratio = 0.0
    else:
        overgeneral_ratio = overgeneral_count / total_terms

    # Calculate the raw confidence score
    raw_score = 0.5 * absolute_ratio + 0.3 * (1 - hedging_density) + 0.2 * overgeneral_ratio

    # Clamp the confidence score to the range [0.0, 1.0]
    confidence = max(0.0, min(1.0, raw_score))

    # Determine whether the input text is blocked
    blocked = confidence >= 0.5

    # Create the result dictionary
    result = {
        "blocked": blocked,
        "reason": "Unwarranted certainty detected" if blocked else "No unwarranted certainty detected",
        "confidence": confidence,
        "category": "Unwarranted Certainty",
        "details": {
            "absolute_ratio": absolute_ratio,
            "hedging_density": hedging_density,
            "overgeneral_ratio": overgeneral_ratio,
        },
    }

    return result


if __name__ == "__main__":
    test_cases = [
        "The sun always rises in the east.",
        "Maybe it will rain tomorrow.",
        "Everyone loves ice cream.",
        "The new policy is likely to be effective.",
        "All cats are black.",
    ]

    for test_case in test_cases:
        result = unwarranted_certainty_detector(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_unwarranted_certainty_detector = unwarranted_certainty_detector

def unwarranted_certainty_detector(input_text):
    _out = _sushi_raw_unwarranted_certainty_detector(input_text)
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
