import re
from typing import Dict
from dataclasses import dataclass
from collections import Counter

@dataclass
class ReAskLoopBreakerResult:
    blocked: bool
    reason: str
    confidence: float
    category: str
    details: Dict

def re_ask_loop_breaker(input_text: str) -> Dict:
    """
    Detects the user re-asking the same thing in slightly different words and suggests stepping back to think.

    This function combines multiple signals to detect re-ask loops, including:
    - Absolute term density
    - Hedge term density
    - Overgeneral term density
    - Sentence structure similarity

    The confidence score is a weighted sum of these signals, clamped to [0.0, 1.0].
    The `blocked` decision is based on a threshold of 0.5.

    Args:
        input_text (str): The user's input text.

    Returns:
        Dict: A dictionary containing the result, including `blocked`, `reason`, `confidence`, `category`, and `details`.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Tokenize the input text
    tokens = re.findall(r'\b\w+\b', input_text.lower())

    # Calculate absolute term density
    absolute_terms = ['always', 'never', 'all', 'none']
    absolute_term_count = sum(1 for token in tokens if token in absolute_terms)
    absolute_term_ratio = absolute_term_count / len(tokens) if tokens else 0.0

    # Calculate hedge term density
    hedge_terms = ['maybe', 'possibly', 'could', 'might']
    hedge_term_count = sum(1 for token in tokens if token in hedge_terms)
    hedge_term_ratio = hedge_term_count / len(tokens) if tokens else 0.0

    # Calculate overgeneral term density
    overgeneral_terms = ['everyone', 'nobody', 'everything', 'nothing']
    overgeneral_term_count = sum(1 for token in tokens if token in overgeneral_terms)
    overgeneral_term_ratio = overgeneral_term_count / len(tokens) if tokens else 0.0

    # Calculate sentence structure similarity
    sentences = re.split(r'[.!?]', input_text)
    sentence_lengths = [len(re.findall(r'\b\w+\b', sentence)) for sentence in sentences if sentence]
    sentence_length_stddev = (sum((length - sum(sentence_lengths) / len(sentence_lengths)) ** 2 for length in sentence_lengths) / len(sentence_lengths)) ** 0.5 if sentence_lengths else 0.0

    # Calculate the confidence score
    raw_score = 0.4 * absolute_term_ratio + 0.3 * hedge_term_ratio + 0.2 * overgeneral_term_ratio + 0.1 * sentence_length_stddev
    confidence = max(0.0, min(1.0, raw_score))

    # Determine the blocked decision
    blocked = confidence >= 0.5

    # Create the result dictionary
    result = ReAskLoopBreakerResult(
        blocked=blocked,
        reason='Re-ask loop detected' if blocked else 'No re-ask loop detected',
        confidence=confidence,
        category='ReAskLoopBreaker',
        details={
            'absolute_term_ratio': absolute_term_ratio,
            'hedge_term_ratio': hedge_term_ratio,
            'overgeneral_term_ratio': overgeneral_term_ratio,
            'sentence_length_stddev': sentence_length_stddev
        }
    )

    return result.__dict__

if __name__ == '__main__':
    test_cases = [
        'I always wonder if I will ever be able to do this.',
        'Maybe I could try to do it, but I am not sure.',
        'Everyone is going to love this, and nobody will hate it.',
        'This is a simple sentence.',
        'This is another simple sentence, and it is very similar to the previous one.'
    ]

    for test_case in test_cases:
        result = re_ask_loop_breaker(test_case)
        print(result)

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
