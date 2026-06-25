import re
from typing import Dict

def overly_prescriptive_language_detector(input_text: str) -> Dict:
    """
    Detects overly prescriptive language in AI-generated content.

    This function combines multiple signals to determine the confidence level of
    prescriptive language in the input text. It calculates the ratio of absolute
    terms, hedge density, and the presence of overgeneral terms to produce a
    graded confidence score.

    Args:
        input_text (str): The input text to be analyzed.

    Returns:
        dict: A dictionary containing the results of the analysis, including:
            - blocked (bool): Whether the text contains overly prescriptive language.
            - reason (str): A brief explanation of the reason for the detection.
            - confidence (float): A confidence score between 0.0 and 1.0.
            - category (str): The category of the detected language.
            - details (dict): Additional details about the detection.

    Mission Alignment:
        This function is designed to protect human cognition from AI overreliance
        by detecting and mitigating overly prescriptive language in AI-generated
        content. It aims to maintain a balance between leveraging AI for assistance
        and preserving human autonomy in decision-making.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Tokenize the input text into sentences
    sentences = re.split(r'[.!?]', input_text)

    # Remove empty sentences
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    # Calculate the total number of words
    total_words = sum(len(sentence.split()) for sentence in sentences)

    # Calculate the ratio of absolute terms
    absolute_terms = re.findall(r'\b(always|never|must|should|will)\b', input_text, re.IGNORECASE)
    absolutes_ratio = len(absolute_terms) / total_words if total_words > 0 else 0.0

    # Calculate the hedge density
    hedge_terms = re.findall(r'\b(maybe|perhaps|possibly|likely|unlikely)\b', input_text, re.IGNORECASE)
    hedge_density = len(hedge_terms) / total_words if total_words > 0 else 0.0

    # Calculate the presence of overgeneral terms
    overgeneral_terms = re.findall(r'\b(everyone|everyone|all|any|each)\b', input_text, re.IGNORECASE)
    overgeneral_terms_ratio = len(overgeneral_terms) / total_words if total_words > 0 else 0.0

    # Calculate the confidence score
    raw_score = 0.5 * absolutes_ratio + 0.3 * (1 - hedge_density) + 0.2 * overgeneral_terms_ratio
    confidence = max(0.0, min(1.0, raw_score))

    # Determine the blocked status and reason
    blocked = confidence > 0.7
    reason = "Overly prescriptive language detected" if blocked else "No overly prescriptive language detected"

    # Determine the category
    category = "Prescriptive Language" if blocked else "Descriptive Language"

    # Create the details dictionary
    details = {
        "absolute_terms": len(absolute_terms),
        "hedge_terms": len(hedge_terms),
        "overgeneral_terms": len(overgeneral_terms),
        "absolutes_ratio": absolutes_ratio,
        "hedge_density": hedge_density,
        "overgeneral_terms_ratio": overgeneral_terms_ratio
    }

    # Return the results
    return {
        "blocked": blocked,
        "reason": reason,
        "confidence": confidence,
        "category": category,
        "details": details
    }


if __name__ == "__main__":
    test_cases = [
        "You must always follow the rules.",
        "It's possible that the weather will be nice tomorrow.",
        "Everyone should try this new restaurant.",
        "The new policy will likely affect everyone.",
        "Maybe we should consider alternative options.",
        "This is the only way to do it.",
        "The instructions are clear and easy to follow.",
        "You should never give up on your dreams.",
        "The results are based on a thorough analysis.",
        "The decision is final and cannot be changed."
    ]

    for test_case in test_cases:
        result = overly_prescriptive_language_detector(test_case)
        print(f"Input: {test_case}")
        print(f"Blocked: {result['blocked']}")
        print(f"Reason: {result['reason']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Category: {result['category']}")
        print(f"Details: {result['details']}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_overly_prescriptive_language_detector = overly_prescriptive_language_detector

def overly_prescriptive_language_detector(input_text):
    _out = _sushi_raw_overly_prescriptive_language_detector(input_text)
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
