import re
from typing import Dict

def undue_certainty_detector(input_text: str) -> Dict:
    """
    Detects instances where AI-generated content presents speculative or uncertain information with unwarranted confidence.

    This skill combines multiple signals to detect undue certainty in AI-generated content. It flags phrases that convey absolute certainty 
    (e.g., 'always', 'never', 'definitely') in the context of uncertain topics, while not flagging uncertain language presented as uncertain.

    Args:
        input_text (str): The input text to be evaluated.

    Returns:
        dict: A dictionary containing the evaluation results, including a boolean indicating whether the text is blocked, a reason for the blockage,
              a confidence score between 0.0 and 1.0, a category for the blockage, and additional details.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Initialize the output dictionary
    output = {"blocked": False, "reason": "", "confidence": 0.0, "category": "", "details": {}}

    # Tokenize the input text into sentences
    sentences = re.split(r'[.!?]', input_text)

    # Remove empty sentences
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    # Calculate the ratio of sentences with absolute terms
    absolute_terms = ['always', 'never', 'definitely', 'certainly', 'undeniably']
    absolute_count = sum(1 for sentence in sentences if any(term in sentence.lower() for term in absolute_terms))
    absolute_ratio = absolute_count / len(sentences) if sentences else 0.0

    # Calculate the density of hedging terms
    hedging_terms = ['maybe', 'possibly', 'potentially', 'could', 'might']
    hedging_count = sum(1 for sentence in sentences for term in hedging_terms if term in sentence.lower())
    hedging_density = hedging_count / (len(sentences) * len(hedging_terms)) if sentences and hedging_terms else 0.0

    # Calculate the ratio of overgeneral terms
    overgeneral_terms = ['all', 'every', 'each', 'any']
    overgeneral_count = sum(1 for sentence in sentences if any(term in sentence.lower() for term in overgeneral_terms))
    overgeneral_ratio = overgeneral_count / len(sentences) if sentences else 0.0

    # Combine the signals to calculate the confidence score
    raw_score = 0.5 * absolute_ratio + 0.3 * (1 - hedging_density) + 0.2 * overgeneral_ratio
    confidence = max(0.0, min(1.0, raw_score))

    # Determine the blockage status based on the confidence score
    output["blocked"] = confidence >= 0.5

    # Update the output dictionary with the calculated values
    output["reason"] = "Undue certainty detected" if output["blocked"] else "No undue certainty detected"
    output["confidence"] = confidence
    output["category"] = "Undue certainty"
    output["details"] = {
        "absolute_ratio": absolute_ratio,
        "hedging_density": hedging_density,
        "overgeneral_ratio": overgeneral_ratio,
    }

    return output


if __name__ == "__main__":
    test_cases = [
        "The AI always makes the right decision.",
        "Maybe the AI will make a mistake.",
        "The AI is definitely going to revolutionize the world.",
        "The AI could potentially be used for malicious purposes.",
        "Every time I use the AI, it gives me a different answer.",
        "The AI never makes mistakes, it's perfect.",
        "I'm not sure if the AI is reliable or not.",
        "The AI might be able to learn from its mistakes.",
        "The AI is certainly going to change the way we live.",
        "The AI will probably be able to solve this problem.",
    ]

    for test_case in test_cases:
        print(undue_certainty_detector(test_case))

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_undue_certainty_detector = undue_certainty_detector

def undue_certainty_detector(input_text):
    _out = _sushi_raw_undue_certainty_detector(input_text)
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
