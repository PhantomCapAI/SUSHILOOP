import re
from typing import Dict

def implicit_assumption_highlighter(input_text: str) -> Dict:
    """
    Detects and highlights implicit assumptions in AI-generated text, 
    prompting users to verify the validity of these assumptions.

    Args:
        input_text (str): The AI-generated text to be analyzed.

    Returns:
        Dict: A dictionary containing the results of the analysis, 
              including a boolean indicating whether the text is blocked, 
              a reason for the block, a confidence score, a category, 
              and additional details.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Initialize variables to store the results
    blocked = False
    reason = ""
    confidence = 0.0
    category = ""
    details = {}

    # Tokenize the input text into sentences
    sentences = re.split(r'[.!?]', input_text)

    # Remove empty strings from the list of sentences
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    # Calculate the number of sentences
    num_sentences = len(sentences)

    # Handle the case where there are no sentences
    if num_sentences == 0:
        return {
            "blocked": False,
            "reason": "No sentences found",
            "confidence": 0.0,
            "category": "No sentences",
            "details": {}
        }

    # Calculate the ratio of sentences with absolute terms
    absolutes = re.findall(r'\b(always|never|all|every|none)\b', input_text, re.IGNORECASE)
    absolutes_ratio = len(absolutes) / num_sentences if num_sentences > 0 else 0

    # Calculate the density of hedging terms
    hedges = re.findall(r'\b(maybe|perhaps|possibly|likely|unlikely)\b', input_text, re.IGNORECASE)
    hedge_density = len(hedges) / num_sentences if num_sentences > 0 else 0

    # Calculate the ratio of overgeneral terms
    overgeneral_terms = re.findall(r'\b(everyone|everybody|all people)\b', input_text, re.IGNORECASE)
    overgeneral_terms_ratio = len(overgeneral_terms) / num_sentences if num_sentences > 0 else 0

    # Calculate the raw confidence score
    raw_confidence = 0.5 * absolutes_ratio + 0.3 * hedge_density + 0.2 * overgeneral_terms_ratio

    # Clamp the confidence score to the range [0.0, 1.0]
    confidence = max(0.0, min(1.0, raw_confidence))

    # Determine whether the text is blocked based on the confidence score
    blocked = confidence >= 0.5

    # Set the reason and category based on the confidence score
    if blocked:
        reason = "Implicit assumptions detected"
        category = "Implicit assumptions"
    else:
        reason = "No implicit assumptions detected"
        category = "No implicit assumptions"

    # Set the details based on the confidence score
    details = {
        "absolutes_ratio": absolutes_ratio,
        "hedge_density": hedge_density,
        "overgeneral_terms_ratio": overgeneral_terms_ratio
    }

    return {
        "blocked": blocked,
        "reason": reason,
        "confidence": confidence,
        "category": category,
        "details": details
    }

if __name__ == "__main__":
    test_cases = [
        "The AI system is always correct.",
        "The AI system is possibly correct.",
        "The AI system is never wrong.",
        "The AI system is likely to be correct.",
        "The AI system is not always correct."
    ]

    for test_case in test_cases:
        result = implicit_assumption_highlighter(test_case)
        print(f"Input: {test_case}")
        print(f"Blocked: {result['blocked']}")
        print(f"Reason: {result['reason']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Category: {result['category']}")
        print(f"Details: {result['details']}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_implicit_assumption_highlighter = implicit_assumption_highlighter

def implicit_assumption_highlighter(input_text):
    _out = _sushi_raw_implicit_assumption_highlighter(input_text)
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
