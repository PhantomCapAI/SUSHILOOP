import re
from typing import Dict

def overemphasis_on_consensus_detector(input_text: str) -> Dict:
    """
    Detects overemphasis on consensus in AI-generated content.

    This function identifies patterns where the AI-generated text repeatedly uses phrases 
    that imply universal agreement, such as 'everyone agrees' or 'it's widely accepted'. 
    It provides feedback to encourage more balanced presentation of opinions.

    Args:
        input_text (str): The input text to be analyzed.

    Returns:
        Dict: A dictionary containing the results of the analysis, including:
            - blocked (bool): Whether the input text is blocked due to overemphasis on consensus.
            - reason (str): The reason for blocking the input text.
            - confidence (float): A confidence score between 0.0 and 1.0 indicating the likelihood of overemphasis on consensus.
            - category (str): The category of the input text (e.g., "consensus").
            - details (Dict): Additional details about the analysis, including the number of sentences, words, and phrases that imply universal agreement.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Initialize variables
    sentences = re.split(r'[.!?]', input_text)
    words = re.findall(r'\b\w+\b', input_text)
    phrases = re.findall(r'\b(everyone|all|most|it\'s widely accepted|there is a consensus)\b', input_text, re.IGNORECASE)
    absolutes = re.findall(r'\b(always|never|every|all)\b', input_text, re.IGNORECASE)
    hedges = re.findall(r'\b(maybe|perhaps|possibly|it seems)\b', input_text, re.IGNORECASE)

    # Calculate ratios
    sentence_count = len(sentences)
    word_count = len(words)
    phrase_count = len(phrases)
    absolute_count = len(absolutes)
    hedge_count = len(hedges)

    # Handle zero/one case
    if sentence_count == 0:
        sentence_ratio = 0.0
    else:
        sentence_ratio = phrase_count / sentence_count

    if word_count == 0:
        word_ratio = 0.0
    else:
        word_ratio = absolute_count / word_count

    if word_count == 0:
        hedge_ratio = 0.0
    else:
        hedge_ratio = hedge_count / word_count

    # Calculate confidence score
    raw_score = 0.5 * sentence_ratio + 0.3 * word_ratio + 0.2 * (1 - hedge_ratio)
    confidence = max(0.0, min(1.0, raw_score))

    # Determine blocking
    blocked = confidence >= 0.5

    # Create result dictionary
    result = {
        "blocked": blocked,
        "reason": "Overemphasis on consensus detected" if blocked else "No overemphasis on consensus detected",
        "confidence": confidence,
        "category": "consensus",
        "details": {
            "sentence_count": sentence_count,
            "word_count": word_count,
            "phrase_count": phrase_count,
            "absolute_count": absolute_count,
            "hedge_count": hedge_count,
            "sentence_ratio": sentence_ratio,
            "word_ratio": word_ratio,
            "hedge_ratio": hedge_ratio
        }
    }

    return result


if __name__ == "__main__":
    test_cases = [
        "Everyone agrees that this is the best approach. It's widely accepted that this is the way to go.",
        "Maybe we should consider other options. Perhaps there are better ways to do this.",
        "All of the experts agree that this is the best course of action. There is a consensus that this is the way to go.",
        "I'm not sure about this. It seems like there are some potential drawbacks.",
        "Always follow the rules. Never question authority."
    ]

    for test_case in test_cases:
        result = overemphasis_on_consensus_detector(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_overemphasis_on_consensus_detector = overemphasis_on_consensus_detector

def overemphasis_on_consensus_detector(input_text):
    _out = _sushi_raw_overemphasis_on_consensus_detector(input_text)
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
