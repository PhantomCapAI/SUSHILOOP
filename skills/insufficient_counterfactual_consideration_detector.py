import re
from collections import Counter
from math import log
from typing import Dict

def insufficient_counterfactual_consideration_detector(input_text: str) -> Dict:
    """
    Detects lack of counterfactual consideration in AI-generated text.

    This function combines multiple signals to determine the confidence level of insufficient counterfactual consideration.
    The signals include:
    - Absolute term density: The ratio of absolute terms (e.g., always, never) to the total number of terms.
    - Hedge term density: The ratio of hedge terms (e.g., maybe, possibly) to the total number of terms.
    - Overgeneral term density: The ratio of overgeneral terms (e.g., everyone, everything) to the total number of terms.
    - Lexical diversity: The ratio of unique terms to the total number of terms.
    - Sentence structure: The ratio of simple sentences to complex sentences.

    The function returns a dictionary with the following keys:
    - blocked: A boolean indicating whether the text lacks sufficient counterfactual consideration.
    - reason: A string describing the reason for the detection.
    - confidence: A float between 0.0 and 1.0 representing the confidence level of the detection.
    - category: A string categorizing the type of detection.
    - details: A dictionary containing detailed information about the detection.

    :param input_text: The input text to be analyzed.
    :return: A dictionary containing the detection results.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Tokenize the input text
    tokens = re.findall(r'\b\w+\b', input_text.lower())

    # Calculate the absolute term density
    absolute_terms = ['always', 'never', 'all', 'none']
    absolute_term_count = sum(1 for token in tokens if token in absolute_terms)
    absolute_term_density = absolute_term_count / len(tokens) if tokens else 0.0

    # Calculate the hedge term density
    hedge_terms = ['maybe', 'possibly', 'perhaps', 'could', 'might']
    hedge_term_count = sum(1 for token in tokens if token in hedge_terms)
    hedge_term_density = hedge_term_count / len(tokens) if tokens else 0.0

    # Calculate the overgeneral term density
    overgeneral_terms = ['everyone', 'everything', 'all', 'none']
    overgeneral_term_count = sum(1 for token in tokens if token in overgeneral_terms)
    overgeneral_term_density = overgeneral_term_count / len(tokens) if tokens else 0.0

    # Calculate the lexical diversity
    unique_terms = set(tokens)
    lexical_diversity = len(unique_terms) / len(tokens) if tokens else 0.0

    # Calculate the sentence structure
    sentences = re.split(r'[.!?]', input_text)
    simple_sentence_count = sum(1 for sentence in sentences if len(re.findall(r'\b\w+\b', sentence)) < 10)
    complex_sentence_count = sum(1 for sentence in sentences if len(re.findall(r'\b\w+\b', sentence)) >= 10)
    sentence_structure = simple_sentence_count / (simple_sentence_count + complex_sentence_count) if simple_sentence_count + complex_sentence_count > 0 else 0.0

    # Combine the signals to determine the confidence level
    raw_score = 0.2 * absolute_term_density + 0.2 * overgeneral_term_density + 0.2 * (1 - lexical_diversity) + 0.2 * (1 - hedge_term_density) + 0.2 * sentence_structure
    confidence = max(0.0, min(1.0, raw_score))

    # Determine the detection result
    blocked = confidence > 0.5
    reason = 'Insufficient counterfactual consideration detected' if blocked else 'No insufficient counterfactual consideration detected'
    category = 'Insufficient Counterfactual Consideration'
    details = {
        'absolute_term_density': absolute_term_density,
        'hedge_term_density': hedge_term_density,
        'overgeneral_term_density': overgeneral_term_density,
        'lexical_diversity': lexical_diversity,
        'sentence_structure': sentence_structure
    }

    return {
        'blocked': blocked,
        'reason': reason,
        'confidence': confidence,
        'category': category,
        'details': details
    }

if __name__ == '__main__':
    test_cases = [
        'The AI system always makes the correct decision.',
        'The new policy will possibly have some negative consequences.',
        'Everyone will benefit from the new policy.',
        'The company never makes mistakes.',
        'The new technology might revolutionize the industry.'
    ]

    for test_case in test_cases:
        result = insufficient_counterfactual_consideration_detector(test_case)
        print(f'Test Case: {test_case}')
        print(f'Result: {result}')
        print('---')

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_insufficient_counterfactual_consideration_detector = insufficient_counterfactual_consideration_detector

def insufficient_counterfactual_consideration_detector(input_text):
    _out = _sushi_raw_insufficient_counterfactual_consideration_detector(input_text)
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
