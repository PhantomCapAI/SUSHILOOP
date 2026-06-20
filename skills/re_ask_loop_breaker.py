import re
from collections import Counter
from math import log
from typing import Dict

def re_ask_loop_breaker(input_text: str) -> Dict:
    """
    Detects the user re-asking the same thing in slightly different words and suggests stepping back to think.

    This function combines multiple signals to detect re-ask loops, including:
    - Weighted pattern matches
    - Structural features (sentence or clause counts, ratios)
    - Lexical diversity
    - Hedging/absolute-term density

    The confidence score is a graded value between 0.0 and 1.0, indicating the likelihood of a re-ask loop.

    :param input_text: The user's input text
    :return: A dictionary containing the detection result, including:
        - blocked: A boolean indicating whether the input is blocked
        - reason: A string explaining the reason for blocking
        - confidence: A float between 0.0 and 1.0 indicating the confidence level
        - category: A string indicating the category of the detection
        - details: A dictionary containing additional details about the detection
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Tokenize the input text
    tokens = re.findall(r'\b\w+\b', input_text.lower())

    # Calculate lexical diversity
    lexical_diversity = len(set(tokens)) / len(tokens) if tokens else 0.0

    # Calculate hedging/absolute-term density
    hedge_terms = ['maybe', 'possibly', 'perhaps', 'could', 'might']
    absolute_terms = ['always', 'never', 'every', 'all']
    hedge_density = sum(1 for token in tokens if token in hedge_terms) / len(tokens) if tokens else 0.0
    absolute_density = sum(1 for token in tokens if token in absolute_terms) / len(tokens) if tokens else 0.0

    # Calculate sentence and clause counts
    sentences = re.split(r'[.!?]', input_text)
    clauses = re.split(r'[;,]', input_text)

    # Calculate structural features
    sentence_ratio = len(sentences) / len(clauses) if clauses else 0.0
    clause_ratio = len(clauses) / len(sentences) if sentences else 0.0

    # Combine signals to calculate confidence
    raw_score = 0.2 * (1 - lexical_diversity) + 0.3 * hedge_density + 0.2 * absolute_density + 0.3 * sentence_ratio
    confidence = max(0.0, min(1.0, raw_score))

    # Determine blocking and reason
    blocked = confidence > 0.7
    reason = 'Re-ask loop detected' if blocked else 'No re-ask loop detected'

    # Create result dictionary
    result = {
        'blocked': blocked,
        'reason': reason,
        'confidence': confidence,
        'category': 're-ask loop',
        'details': {
            'lexical_diversity': lexical_diversity,
            'hedge_density': hedge_density,
            'absolute_density': absolute_density,
            'sentence_ratio': sentence_ratio,
            'clause_ratio': clause_ratio
        }
    }

    return result


if __name__ == '__main__':
    test_cases = [
        'What is the meaning of life?',
        'I am wondering what the meaning of life is.',
        'Maybe the meaning of life is to find happiness.',
        'I am not sure what the meaning of life is, but I think it might be to find happiness.',
        'The meaning of life is to always be happy.',
        'I have been thinking about the meaning of life, and I think it is to find happiness, but maybe I am wrong.',
        'The meaning of life is never to be unhappy.',
        'I am not sure what the meaning of life is, but I think it could be to find happiness, or maybe it is something else.',
        'The meaning of life is every day to find happiness.',
        'I have been thinking about the meaning of life, and I think it is to find happiness, but I am not sure.'
    ]

    for test_case in test_cases:
        result = re_ask_loop_breaker(test_case)
        print(f'Input: {test_case}')
        print(f'Result: {result}')
        print('---')

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
