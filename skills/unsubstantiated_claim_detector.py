import re
from typing import Dict

def unsubstantiated_claim_detector(input_text: str) -> Dict:
    """
    Detects unsubstantiated claims in user input and prompts for supporting evidence.

    This skill combines multiple signals to determine the confidence of unsubstantiated claims:
    - Absolute term density
    - Hedge term density
    - Overgeneral term density
    - Sentence structure complexity

    The confidence score is graded and clamped between 0.0 and 1.0. The `blocked` decision is based on a threshold of 0.5.

    Mission alignment: This skill protects human cognition from potential misinformation by identifying unsubstantiated claims
    and promoting critical thinking.

    :param input_text: User input text to analyze
    :return: Dictionary with analysis results
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Preprocess input text
    input_text = input_text.lower()
    sentences = re.split(r'[.!?]', input_text)
    sentences = [s.strip() for s in sentences if s.strip()]

    # Signal 1: Absolute term density
    absolute_terms = ['always', 'never', 'all', 'none']
    absolute_count = sum(1 for sentence in sentences for term in absolute_terms if term in sentence)
    absolute_ratio = absolute_count / len(sentences) if sentences else 0.0

    # Signal 2: Hedge term density
    hedge_terms = ['maybe', 'possibly', 'could', 'might']
    hedge_count = sum(1 for sentence in sentences for term in hedge_terms if term in sentence)
    hedge_ratio = hedge_count / len(sentences) if sentences else 0.0

    # Signal 3: Overgeneral term density
    overgeneral_terms = ['everyone', 'nobody', 'everything', 'nothing']
    overgeneral_count = sum(1 for sentence in sentences for term in overgeneral_terms if term in sentence)
    overgeneral_ratio = overgeneral_count / len(sentences) if sentences else 0.0

    # Signal 4: Sentence structure complexity
    sentence_complexity = sum(len(re.findall(r'\b\w+\b', sentence)) for sentence in sentences) / len(sentences) if sentences else 0.0

    # Combine signals
    raw_score = 0.4 * absolute_ratio + 0.3 * hedge_ratio + 0.2 * overgeneral_ratio + 0.1 * sentence_complexity
    confidence = max(0.0, min(1.0, raw_score))

    # Determine blocked decision
    blocked = confidence >= 0.5

    # Return analysis results
    return {
        "blocked": blocked,
        "reason": "Unsubstantiated claim detected" if blocked else "No unsubstantiated claim detected",
        "confidence": confidence,
        "category": "Unsubstantiated Claim",
        "details": {
            "absolute_ratio": absolute_ratio,
            "hedge_ratio": hedge_ratio,
            "overgeneral_ratio": overgeneral_ratio,
            "sentence_complexity": sentence_complexity
        }
    }

if __name__ == "__main__":
    test_cases = [
        "I always get what I want.",
        "Maybe it will rain tomorrow.",
        "Everyone loves this restaurant.",
        "The sky is blue.",
        "This product is the best thing since sliced bread."
    ]

    for test_case in test_cases:
        result = unsubstantiated_claim_detector(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_unsubstantiated_claim_detector = unsubstantiated_claim_detector

def unsubstantiated_claim_detector(input_text):
    _out = _sushi_raw_unsubstantiated_claim_detector(input_text)
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
