import re
from math import log
from typing import Dict

def tone_shift_detector(input_text: str) -> Dict:
    """
    Detects sudden changes in tone or sentiment within a text, potentially indicating 
    manipulative or persuasive language, and flags them for human review.

    This function combines multiple signals to detect tone shifts, including:
    - Absolute term density
    - Hedge density
    - Overgeneral term density
    - Sentence complexity

    The confidence score is a weighted sum of these signals, clamped to [0.0, 1.0].
    The `blocked` decision is based on a threshold of 0.5.

    Parameters:
    input_text (str): The text to analyze

    Returns:
    dict: A dictionary containing the results, including:
        - blocked (bool): Whether the text is flagged for review
        - reason (str): A brief explanation of the flag
        - confidence (float): A score indicating the strength of the signal
        - category (str): The category of the detected tone shift
        - details (dict): Additional details about the detected tone shift
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Tokenize the input text
    tokens = re.findall(r'\b\w+\b', input_text.lower())

    # Calculate absolute term density
    absolute_terms = ['always', 'never', 'every', 'all']
    absolute_term_count = sum(1 for token in tokens if token in absolute_terms)
    absolute_term_ratio = absolute_term_count / len(tokens) if tokens else 0.0

    # Calculate hedge density
    hedge_terms = ['maybe', 'perhaps', 'possibly', 'could']
    hedge_term_count = sum(1 for token in tokens if token in hedge_terms)
    hedge_density = hedge_term_count / len(tokens) if tokens else 0.0

    # Calculate overgeneral term density
    overgeneral_terms = ['everyone', 'nobody', 'something', 'nothing']
    overgeneral_term_count = sum(1 for token in tokens if token in overgeneral_terms)
    overgeneral_term_ratio = overgeneral_term_count / len(tokens) if tokens else 0.0

    # Calculate sentence complexity
    sentences = re.split(r'[.!?]', input_text)
    sentence_complexity = sum(len(re.findall(r'\b\w+\b', sentence)) for sentence in sentences) / len(sentences) if sentences else 0.0

    # Combine signals to calculate confidence
    raw_confidence = 0.4 * absolute_term_ratio + 0.3 * hedge_density + 0.2 * overgeneral_term_ratio + 0.1 * sentence_complexity
    confidence = max(0.0, min(1.0, raw_confidence))

    # Determine blocked status
    blocked = confidence >= 0.5

    # Create result dictionary
    result = {
        'blocked': blocked,
        'reason': 'Tone shift detected' if blocked else 'No tone shift detected',
        'confidence': confidence,
        'category': 'Manipulative language' if blocked else 'Neutral',
        'details': {
            'absolute_term_ratio': absolute_term_ratio,
            'hedge_density': hedge_density,
            'overgeneral_term_ratio': overgeneral_term_ratio,
            'sentence_complexity': sentence_complexity
        }
    }

    return result


if __name__ == '__main__':
    test_cases = [
        'This is a neutral sentence.',
        'You should always do this, because everyone does it.',
        'Maybe you could try this, but it might not work.',
        'I am absolutely certain that this is the best option.',
        'The new policy will affect nobody, so it is not a problem.'
    ]

    for test_case in test_cases:
        result = tone_shift_detector(test_case)
        print(f'Test case: {test_case}')
        print(f'Result: {result}')
        print('---')

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_tone_shift_detector = tone_shift_detector

def tone_shift_detector(input_text):
    _out = _sushi_raw_tone_shift_detector(input_text)
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
