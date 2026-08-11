import re
from typing import Dict

def overconfidence_indicator(input_text: str) -> Dict:
    """
    Detects overconfidence in AI-generated text by analyzing absolute language, 
    hedging terms, and overgeneral terms. Returns a dictionary with a confidence 
    score and a decision to block or not.

    Mission alignment: This skill aims to promote critical thinking and informed 
    decision-making by flagging potentially misleading information.

    :param input_text: The input text to be analyzed
    :return: A dictionary with the following keys:
        - blocked: A boolean indicating whether the text should be blocked
        - reason: A string explaining the reason for blocking
        - confidence: A float between 0.0 and 1.0 indicating the confidence level
        - category: A string indicating the category of the text
        - details: A dictionary with additional details about the analysis
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Define regular expressions for absolute language, hedging terms, and overgeneral terms
    absolute_pattern = re.compile(r"\b(always|never|definitely|certainly|undeniably)\b", re.IGNORECASE)
    hedge_pattern = re.compile(r"\b(maybe|perhaps|possibly|probably|likely)\b", re.IGNORECASE)
    overgeneral_pattern = re.compile(r"\b(all|every|each|any)\b", re.IGNORECASE)

    # Count the number of absolute language matches
    absolute_matches = len(absolute_pattern.findall(input_text))

    # Count the number of hedging term matches
    hedge_matches = len(hedge_pattern.findall(input_text))

    # Count the number of overgeneral term matches
    overgeneral_matches = len(overgeneral_pattern.findall(input_text))

    # Calculate the total number of words in the input text
    total_words = len(input_text.split())

    # Calculate the ratio of absolute language matches to total words
    absolute_ratio = absolute_matches / total_words if total_words > 0 else 0.0

    # Calculate the ratio of hedging term matches to total words
    hedge_ratio = hedge_matches / total_words if total_words > 0 else 0.0

    # Calculate the ratio of overgeneral term matches to total words
    overgeneral_ratio = overgeneral_matches / total_words if total_words > 0 else 0.0

    # Calculate the confidence score as a weighted sum of the ratios
    raw_confidence = 0.5 * absolute_ratio + 0.3 * (1 - hedge_ratio) + 0.2 * overgeneral_ratio

    # Clamp the confidence score to the range [0.0, 1.0]
    confidence = max(0.0, min(1.0, raw_confidence))

    # Determine whether to block the text based on the confidence score
    blocked = confidence >= 0.5

    # Create the output dictionary
    output = {
        "blocked": blocked,
        "reason": "Overconfidence detected" if blocked else "No overconfidence detected",
        "confidence": confidence,
        "category": "Overconfidence",
        "details": {
            "absolute_matches": absolute_matches,
            "hedge_matches": hedge_matches,
            "overgeneral_matches": overgeneral_matches,
            "total_words": total_words,
            "absolute_ratio": absolute_ratio,
            "hedge_ratio": hedge_ratio,
            "overgeneral_ratio": overgeneral_ratio
        }
    }

    return output


if __name__ == "__main__":
    test_cases = [
        "This is a completely normal sentence.",
        "I am absolutely certain that this is true.",
        "Maybe this sentence is a little uncertain.",
        "Every single person on the planet agrees with me.",
        "This sentence contains no absolute language or hedging terms.",
        "Definitely, this sentence is overconfident."
    ]

    for test_case in test_cases:
        output = overconfidence_indicator(test_case)
        print(f"Input: {test_case}")
        print(f"Output: {output}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_overconfidence_indicator = overconfidence_indicator

def overconfidence_indicator(input_text):
    _out = _sushi_raw_overconfidence_indicator(input_text)
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
