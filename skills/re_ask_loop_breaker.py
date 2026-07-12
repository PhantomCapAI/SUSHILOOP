import re
from collections import Counter
from typing import Dict

def re_ask_loop_breaker(input_text: str) -> Dict:
    """
    Detects the user re-asking the same thing in slightly different words and suggests stepping back to think.

    This function combines multiple signals to detect re-ask loops, including:
    - Absolute term density
    - Hedge term density
    - Overgeneral term density
    - Sentence structure similarity

    Args:
        input_text (str): The user's input text.

    Returns:
        Dict: A dictionary containing the following keys:
            - blocked (bool): Whether the input text is likely a re-ask loop.
            - reason (str): A brief explanation for the decision.
            - confidence (float): A graded confidence score between 0.0 and 1.0.
            - category (str): The category of the detected pattern.
            - details (Dict): Additional details about the detection.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Preprocess the input text
    input_text = input_text.lower()
    sentences = re.split(r'[.!?]', input_text)
    sentences = [s.strip() for s in sentences if s]

    # Calculate absolute term density
    absolute_terms = ['always', 'never', 'every', 'all']
    absolute_count = sum(1 for sentence in sentences for term in absolute_terms if term in sentence)
    absolute_ratio = absolute_count / (len(sentences) or 1)

    # Calculate hedge term density
    hedge_terms = ['maybe', 'perhaps', 'possibly', 'could']
    hedge_count = sum(1 for sentence in sentences for term in hedge_terms if term in sentence)
    hedge_ratio = hedge_count / (len(sentences) or 1)

    # Calculate overgeneral term density
    overgeneral_terms = ['thing', 'stuff', 'everything', 'nothing']
    overgeneral_count = sum(1 for sentence in sentences for term in overgeneral_terms if term in sentence)
    overgeneral_ratio = overgeneral_count / (len(sentences) or 1)

    # Calculate sentence structure similarity
    sentence_lengths = [len(sentence.split()) for sentence in sentences]
    sentence_length_stddev = (sum((x - sum(sentence_lengths) / len(sentence_lengths)) ** 2 for x in sentence_lengths) / len(sentence_lengths)) ** 0.5 if sentence_lengths else 0

    # Combine signals to calculate confidence
    raw_score = 0.4 * absolute_ratio + 0.3 * hedge_ratio + 0.2 * overgeneral_ratio + 0.1 * (1 - sentence_length_stddev / (max(sentence_lengths) or 1))
    confidence = max(0.0, min(1.0, raw_score))

    # Determine the blocked decision
    blocked = confidence >= 0.5

    # Return the result
    return {
        'blocked': blocked,
        'reason': 'Re-ask loop detected' if blocked else 'No re-ask loop detected',
        'confidence': confidence,
        'category': 'Re-ask Loop',
        'details': {
            'absolute_ratio': absolute_ratio,
            'hedge_ratio': hedge_ratio,
            'overgeneral_ratio': overgeneral_ratio,
            'sentence_length_stddev': sentence_length_stddev
        }
    }

if __name__ == '__main__':
    test_cases = [
        'I always wonder if I will ever find the answer.',
        'Maybe I should just try something new.',
        'Everything is possible if you just believe.',
        'I am not sure what to do.',
        'This is a test case with multiple sentences. It should not trigger the re-ask loop detector.'
    ]

    for test_case in test_cases:
        result = re_ask_loop_breaker(test_case)
        print(f'Input: {test_case}')
        print(f'Result: {result}')
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_re_ask_loop_breaker = re_ask_loop_breaker

def re_ask_loop_breaker(input_text):
    _out = _sushi_raw_re_ask_loop_breaker(input_text)
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
