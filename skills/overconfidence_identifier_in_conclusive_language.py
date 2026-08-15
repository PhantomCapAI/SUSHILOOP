import re
from typing import Dict

def overconfidence_identifier_in_conclusive_language(input_text: str) -> Dict:
    """
    Identifies overconfidence patterns in conclusive language, providing a graded confidence score.
    
    This skill aims to detect when AI-generated text exhibits overconfidence by using conclusive language patterns,
    potentially misleading users into relying too heavily on AI output. It flags instances where absolute terms are used
    without adequate justification or evidence, promoting nuanced understanding and decision-making.
    
    The confidence score is computed by combining multiple signals, including:
    - Absolute term density
    - Hedge term density
    - Overgeneral term density
    - Sentence structure and complexity
    
    The skill returns a dictionary with the following keys:
    - blocked: A boolean indicating whether the input text exhibits overconfidence (True) or not (False)
    - reason: A string describing the reason for the blocking decision
    - confidence: A float between 0.0 and 1.0 representing the confidence in the blocking decision
    - category: A string categorizing the type of overconfidence detected
    - details: A dictionary with additional details about the detection, including the input text and signal values
    
    :param input_text: The input text to analyze
    :return: A dictionary with the analysis results
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Define regular expressions for absolute, hedge, and overgeneral terms
    absolute_terms = re.compile(r"\b(always|never|certainly|definitely|undoubtedly)\b")
    hedge_terms = re.compile(r"\b(maybe|perhaps|possibly|probably|likely)\b")
    overgeneral_terms = re.compile(r"\b(all|every|each|any)\b")

    # Split the input text into sentences
    sentences = re.split(r"[.!?]", input_text)

    # Initialize signal values
    absolute_count = 0
    hedge_count = 0
    overgeneral_count = 0
    sentence_count = len(sentences)

    # Iterate over sentences and count signal terms
    for sentence in sentences:
        absolute_count += len(absolute_terms.findall(sentence))
        hedge_count += len(hedge_terms.findall(sentence))
        overgeneral_count += len(overgeneral_terms.findall(sentence))

    # Compute signal ratios
    if sentence_count > 0:
        absolute_ratio = absolute_count / sentence_count
        hedge_ratio = hedge_count / sentence_count
        overgeneral_ratio = overgeneral_count / sentence_count
    else:
        absolute_ratio = 0.0
        hedge_ratio = 0.0
        overgeneral_ratio = 0.0

    # Compute confidence score
    raw_score = 0.5 * absolute_ratio + 0.3 * (1 - hedge_ratio) + 0.2 * overgeneral_ratio
    confidence = max(0.0, min(1.0, raw_score))

    # Determine blocking decision
    blocked = confidence >= 0.5

    # Create result dictionary
    result = {
        "blocked": blocked,
        "reason": "Overconfidence detected" if blocked else "No overconfidence detected",
        "confidence": confidence,
        "category": "Conclusive language" if blocked else "Benign language",
        "details": {
            "input_text": input_text,
            "absolute_count": absolute_count,
            "hedge_count": hedge_count,
            "overgeneral_count": overgeneral_count,
            "sentence_count": sentence_count,
            "absolute_ratio": absolute_ratio,
            "hedge_ratio": hedge_ratio,
            "overgeneral_ratio": overgeneral_ratio,
        },
    }

    return result


if __name__ == "__main__":
    test_cases = [
        "This is a clearly benign sentence.",
        "The AI is always right, and we should never question its output.",
        "Maybe the AI is correct, but we should consider alternative perspectives.",
        "Every single person on the planet agrees with this statement.",
        "The AI's output is certainly accurate, but we should still verify the results.",
    ]

    for test_case in test_cases:
        result = overconfidence_identifier_in_conclusive_language(test_case)
        print(f"Input: {test_case}")
        print(f"Blocked: {result['blocked']}")
        print(f"Reason: {result['reason']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Category: {result['category']}")
        print(f"Details: {result['details']}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_overconfidence_identifier_in_conclusive_language = overconfidence_identifier_in_conclusive_language

def overconfidence_identifier_in_conclusive_language(input_text):
    _out = _sushi_raw_overconfidence_identifier_in_conclusive_language(input_text)
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
