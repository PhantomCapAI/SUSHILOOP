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

def unhedged_medicallegal_claim_filter(input_text: str) -> Dict:
    """
    Flags AI output giving medical or legal directives without a verify-with-a-professional caveat.

    This function combines multiple signals to detect unhedged medical or legal claims in the input text.
    The signals include:
    1. Absolute terms density: The ratio of absolute terms (e.g., "always", "never") to the total number of words.
    2. Hedge density: The ratio of hedging terms (e.g., "may", "might") to the total number of words.
    3. Overgeneral terms: The presence of overgeneral terms (e.g., "everyone", "all") in the input text.

    The confidence score is a weighted sum of these signals, clamped to the range [0.0, 1.0].
    The `blocked` field is set to True if the confidence score exceeds a threshold of 0.5.

    :param input_text: The input text to be analyzed.
    :return: A dictionary containing the detection result, including the `blocked` field, `reason`, `confidence`, `category`, and `details`.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Define the patterns for absolute terms, hedging terms, and overgeneral terms
    absolute_terms = re.compile(r"\b(always|never|must|should|will)\b", re.IGNORECASE)
    hedge_terms = re.compile(r"\b(may|might|could|would|can)\b", re.IGNORECASE)
    overgeneral_terms = re.compile(r"\b(everyone|all|anyone|no one)\b", re.IGNORECASE)

    # Count the number of absolute terms, hedging terms, and overgeneral terms
    absolute_count = len(absolute_terms.findall(input_text))
    hedge_count = len(hedge_terms.findall(input_text))
    overgeneral_count = len(overgeneral_terms.findall(input_text))

    # Calculate the total number of words
    word_count = len(input_text.split())

    # Calculate the density of absolute terms and hedging terms
    absolute_density = absolute_count / word_count if word_count > 0 else 0.0
    hedge_density = hedge_count / word_count if word_count > 0 else 0.0

    # Calculate the weighted sum of the signals
    raw_score = 0.5 * absolute_density + 0.3 * (1 - hedge_density) + 0.2 * (overgeneral_count > 0)

    # Clamp the confidence score to the range [0.0, 1.0]
    confidence = max(0.0, min(1.0, raw_score))

    # Set the `blocked` field based on the confidence score
    blocked = confidence >= 0.5

    # Create the detection result dictionary
    result = {
        "blocked": blocked,
        "reason": "Unhedged medical or legal claim detected" if blocked else "No unhedged medical or legal claim detected",
        "confidence": confidence,
        "category": "Medical/Legal Claim",
        "details": {
            "absolute_density": absolute_density,
            "hedge_density": hedge_density,
            "overgeneral_terms": overgeneral_count > 0
        }
    }

    return result


if __name__ == "__main__":
    test_cases = [
        "You should always consult a doctor before taking any medication.",
        "I'm not a medical professional, but I think you might want to consider seeing a doctor.",
        "Everyone should take this medication to cure their illness.",
        "This is just a harmless suggestion, and you should not take it as medical advice.",
        "If you have any concerns, please consult a qualified medical professional."
    ]

    for test_case in test_cases:
        result = unhedged_medicallegal_claim_filter(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_unhedged_medicallegal_claim_filter = unhedged_medicallegal_claim_filter

def unhedged_medicallegal_claim_filter(input_text):
    _out = _sushi_raw_unhedged_medicallegal_claim_filter(input_text)
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
