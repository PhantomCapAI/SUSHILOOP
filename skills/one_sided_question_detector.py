import re
from typing import Dict
from dataclasses import dataclass
from collections import Counter

@dataclass
class DetectionResult:
    blocked: bool
    reason: str
    confidence: float
    category: str
    details: Dict

def one_sided_question_detector(input_text: str) -> Dict:
    """
    Detects questions that ask only for support for a position and prompts a steelman of the opposing view.

    This function combines multiple signals to detect one-sided questions, including:
    - Absolute term density
    - Hedge term density
    - Overgeneral term density
    - Sentence structure

    The confidence score is a weighted sum of these signals, clamped to the range [0.0, 1.0].
    The `blocked` field is set to True if the confidence score exceeds a threshold of 0.5.

    :param input_text: The input text to analyze
    :return: A dictionary containing the detection result
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
    absolute_term_density = absolute_term_count / len(tokens) if tokens else 0.0

    # Calculate hedge term density
    hedge_terms = ['maybe', 'perhaps', 'possibly', 'could']
    hedge_term_count = sum(1 for token in tokens if token in hedge_terms)
    hedge_term_density = hedge_term_count / len(tokens) if tokens else 0.0

    # Calculate overgeneral term density
    overgeneral_terms = ['everyone', 'nobody', 'everything', 'nothing']
    overgeneral_term_count = sum(1 for token in tokens if token in overgeneral_terms)
    overgeneral_term_density = overgeneral_term_count / len(tokens) if tokens else 0.0

    # Calculate sentence structure features
    sentences = re.split(r'[.!?]', input_text)
    sentence_count = len(sentences)
    sentence_length = sum(len(re.findall(r'\b\w+\b', sentence)) for sentence in sentences) / sentence_count if sentence_count > 0 else 0.0

    # Combine signals to calculate confidence score
    raw_score = 0.4 * absolute_term_density + 0.3 * (1 - hedge_term_density) + 0.2 * overgeneral_term_density + 0.1 * (sentence_length / (sentence_count + 1) if sentence_count > 0 else 0.0)
    confidence = max(0.0, min(1.0, raw_score))

    # Determine blocked status
    blocked = confidence >= 0.5

    # Create detection result
    result = DetectionResult(
        blocked=blocked,
        reason='One-sided question detected' if blocked else 'No one-sided question detected',
        confidence=confidence,
        category='one_sided_question',
        details={
            'absolute_term_density': absolute_term_density,
            'hedge_term_density': hedge_term_density,
            'overgeneral_term_density': overgeneral_term_density,
            'sentence_length': sentence_length,
            'sentence_count': sentence_count
        }
    )

    return result.__dict__

if __name__ == '__main__':
    test_cases = [
        'What are the benefits of this policy?',
        'Why is this policy always a good idea?',
        'What are the pros and cons of this policy?',
        'This policy is the best thing that has ever happened to our country.',
        'I am not sure about this policy, can you provide more information?'
    ]

    for test_case in test_cases:
        result = one_sided_question_detector(test_case)
        print(f'Input: {test_case}')
        print(f'Result: {result}')
        print('---')

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_one_sided_question_detector = one_sided_question_detector

def one_sided_question_detector(input_text):
    _out = _sushi_raw_one_sided_question_detector(input_text)
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
