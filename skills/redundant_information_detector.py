import re
from collections import Counter
from typing import Dict
import math

def redundant_information_detector(input_text: str) -> Dict:
    """
    Detects and alerts users when input prompts contain redundant or repetitive information.

    This function combines multiple signals to determine the confidence of redundant information:
    1. Sentence count and ratio
    2. Lexical diversity (type-token ratio)
    3. Hedging/absolute-term density
    4. Duplicate phrases or sentences

    Args:
        input_text (str): The input text to be analyzed.

    Returns:
        Dict: A dictionary containing the results of the analysis.
            - "blocked" (bool): Whether the input text contains redundant information.
            - "reason" (str): The reason for blocking the input text.
            - "confidence" (float): The confidence level of redundant information (between 0.0 and 1.0).
            - "category" (str): The category of redundant information.
            - "details" (dict): Additional details about the redundant information.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Split the input text into sentences
    sentences = re.split(r'[.!?]\s*', input_text)

    # Remove empty sentences
    sentences = [sentence for sentence in sentences if sentence]

    # Calculate the sentence count and ratio
    sentence_count = len(sentences)
    sentence_ratio = sentence_count / (sentence_count + 1) if sentence_count > 0 else 0.0

    # Calculate the lexical diversity (type-token ratio)
    words = re.findall(r'\b\w+\b', input_text.lower())
    word_count = len(words)
    unique_word_count = len(set(words))
    lexical_diversity = unique_word_count / word_count if word_count > 0 else 0.0

    # Calculate the hedging/absolute-term density
    hedging_terms = ['always', 'never', 'usually', 'often', 'rarely', 'sometimes']
    absolute_terms = ['all', 'every', 'each', 'any', 'none']
    hedging_term_count = sum(1 for word in words if word in hedging_terms)
    absolute_term_count = sum(1 for word in words if word in absolute_terms)
    hedging_density = (hedging_term_count + absolute_term_count) / word_count if word_count > 0 else 0.0

    # Calculate the duplicate phrase or sentence count
    phrase_counts = Counter(' '.join(re.findall(r'\b\w+\b', sentence.lower())) for sentence in sentences)
    duplicate_phrase_count = sum(count - 1 for count in phrase_counts.values() if count > 1)

    # Combine the signals to determine the confidence of redundant information
    raw_score = 0.4 * sentence_ratio + 0.3 * (1 - lexical_diversity) + 0.2 * hedging_density + 0.1 * (duplicate_phrase_count / sentence_count if sentence_count > 0 else 0.0)
    confidence = max(0.0, min(1.0, raw_score))

    # Determine the blocking status and reason
    blocked = confidence > 0.5
    reason = 'Redundant information detected' if blocked else 'No redundant information detected'
    category = 'Redundant Information'

    # Create the result dictionary
    result = {
        'blocked': blocked,
        'reason': reason,
        'confidence': confidence,
        'category': category,
        'details': {
            'sentence_count': sentence_count,
            'sentence_ratio': sentence_ratio,
            'lexical_diversity': lexical_diversity,
            'hedging_density': hedging_density,
            'duplicate_phrase_count': duplicate_phrase_count
        }
    }

    return result


if __name__ == '__main__':
    test_cases = [
        'This is a test sentence. This is another test sentence.',
        'The cat sat on the mat. The dog ran around the corner.',
        'I always go to the store. I never go to the park.',
        'The sun is shining. The sun is shining. The sun is shining.',
        'This is a test sentence with no redundant information.',
        'The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog.',
        'The cat purrs contentedly. The dog wags its tail.',
        'I often go to the store. I usually buy milk.',
        'The sun is shining. The sun is shining. The sun is shining. The sun is shining.'
    ]

    for test_case in test_cases:
        result = redundant_information_detector(test_case)
        print(f'Input: {test_case}')
        print(f'Result: {result}')
        print('---')

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_redundant_information_detector = redundant_information_detector

def redundant_information_detector(input_text):
    _out = _sushi_raw_redundant_information_detector(input_text)
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
