import re
from typing import Dict

def assumptive_leap_detector(input_text: str) -> Dict:
    """
    Detects when a user's prompt assumes a specific outcome or conclusion without providing sufficient evidence or justification.

    This skill identifies patterns where the user's language implies a certain result or inference without adequately supporting it.
    It encourages users to think critically about their assumptions and the evidence they provide, rather than relying on AI to fill in gaps or make leaps of logic.

    Args:
        input_text (str): The user's prompt.

    Returns:
        dict: A dictionary containing the results of the detection, including:
            - blocked (bool): Whether the input text is blocked due to assumptive language.
            - reason (str): The reason for blocking the input text.
            - confidence (float): A graded confidence score between 0.0 and 1.0.
            - category (str): The category of the detection.
            - details (dict): Additional details about the detection.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Preprocess the input text
    input_text = input_text.lower()
    sentences = re.split(r'[.!?]', input_text)
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    words = re.findall(r'\b\w+\b', input_text)

    # Calculate the ratio of absolute terms
    absolute_terms = re.findall(r'\b(always|never|all|every|none)\b', input_text)
    absolutes_ratio = len(absolute_terms) / len(words) if words else 0.0

    # Calculate the density of hedge terms
    hedge_terms = re.findall(r'\b(maybe|perhaps|possibly|likely|unlikely)\b', input_text)
    hedge_density = len(hedge_terms) / len(words) if words else 0.0

    # Calculate the frequency of overgeneral terms
    overgeneral_terms = re.findall(r'\b(all|every|always|never)\b', input_text)
    overgeneral_terms_frequency = len(overgeneral_terms) / len(sentences) if sentences else 0.0

    # Calculate the raw confidence score
    raw_score = 0.5 * absolutes_ratio + 0.3 * hedge_density + 0.2 * overgeneral_terms_frequency

    # Clamp the confidence score to the range [0.0, 1.0]
    confidence = max(0.0, min(1.0, raw_score))

    # Determine whether the input text is blocked
    blocked = confidence >= 0.5

    # Create the result dictionary
    result = {
        'blocked': blocked,
        'reason': 'Assumptive language detected' if blocked else 'No assumptive language detected',
        'confidence': confidence,
        'category': 'Assumptive Leap Detector',
        'details': {
            'absolutes_ratio': absolutes_ratio,
            'hedge_density': hedge_density,
            'overgeneral_terms_frequency': overgeneral_terms_frequency
        }
    }

    return result


if __name__ == '__main__':
    test_cases = [
        'I always get what I want.',
        'Maybe it will rain tomorrow.',
        'Every person is unique.',
        'The company will never go bankrupt.',
        'It is possible that the weather will be nice.',
        'All people are equal.',
        'The new policy is likely to be successful.',
        'The team will definitely win the game.'
    ]

    for test_case in test_cases:
        result = assumptive_leap_detector(test_case)
        print(f'Input: {test_case}')
        print(f'Result: {result}')
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_assumptive_leap_detector = assumptive_leap_detector

def assumptive_leap_detector(input_text):
    _out = _sushi_raw_assumptive_leap_detector(input_text)
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
