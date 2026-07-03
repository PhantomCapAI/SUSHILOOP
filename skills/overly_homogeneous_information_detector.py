import re
from collections import Counter
from math import log
from typing import Dict

def overly_homogeneous_information_detector(input_text: str) -> Dict:
    """
    Detects overly homogeneous information in the provided input text.

    This function analyzes the input text for repetitive ideas, similar sentence structures,
    and limited vocabulary to identify potential homogeneous information. It returns a
    dictionary with a graded confidence score and a decision to block the text.

    The mission of this function is to protect human cognition from overly homogeneous
    information, which can lead to a narrow and biased understanding of the world.

    Args:
        input_text (str): The input text to be analyzed.

    Returns:
        Dict: A dictionary with the following keys:
            - blocked (bool): A decision to block the text based on the confidence score.
            - reason (str): A reason for the decision.
            - confidence (float): A graded confidence score between 0.0 and 1.0.
            - category (str): A category for the detected homogeneous information.
            - details (Dict): A dictionary with detailed information about the analysis.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Split the input text into sentences
    sentences = re.split(r'[.!?]', input_text)

    # Remove empty sentences
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    # Calculate the number of sentences
    num_sentences = len(sentences)

    # Calculate the lexical diversity (type-token ratio)
    words = re.findall(r'\b\w+\b', input_text.lower())
    num_words = len(words)
    num_unique_words = len(set(words))
    lexical_diversity = num_unique_words / num_words if num_words > 0 else 0.0

    # Calculate the hedging/absolute-term density
    hedge_terms = ['maybe', 'possibly', 'perhaps', 'could', 'might', 'may']
    absolute_terms = ['always', 'never', 'every', 'all', 'none']
    hedge_count = sum(1 for word in words if word in hedge_terms)
    absolute_count = sum(1 for word in words if word in absolute_terms)
    hedge_density = hedge_count / num_words if num_words > 0 else 0.0
    absolute_density = absolute_count / num_words if num_words > 0 else 0.0

    # Calculate the repetitive ideas ratio
    sentence_lengths = [len(re.findall(r'\b\w+\b', sentence)) for sentence in sentences]
    repetitive_ideas_ratio = sum(1 for length in sentence_lengths if length < 5) / num_sentences if num_sentences > 0 else 0.0

    # Calculate the raw confidence score
    raw_score = 0.4 * (1 - lexical_diversity) + 0.3 * absolute_density + 0.3 * repetitive_ideas_ratio

    # Clamp the confidence score to [0.0, 1.0]
    confidence = max(0.0, min(1.0, raw_score))

    # Make a decision to block the text based on the confidence score
    blocked = confidence >= 0.5

    # Create the output dictionary
    output = {
        'blocked': blocked,
        'reason': 'Overly homogeneous information detected' if blocked else 'No homogeneous information detected',
        'confidence': confidence,
        'category': 'Homogeneous information',
        'details': {
            'lexical_diversity': lexical_diversity,
            'hedge_density': hedge_density,
            'absolute_density': absolute_density,
            'repetitive_ideas_ratio': repetitive_ideas_ratio,
            'num_sentences': num_sentences,
            'num_words': num_words,
            'num_unique_words': num_unique_words
        }
    }

    return output


if __name__ == '__main__':
    test_cases = [
        'The sun is shining. The sun is shining. The sun is shining.',
        'The cat is sleeping. The dog is barking. The bird is singing.',
        'I always go to the beach on summer vacation. I always eat ice cream on summer vacation.',
        'Maybe it will rain tomorrow. Perhaps it will be sunny tomorrow.',
        'The new policy is great. The new policy is amazing. The new policy is wonderful.'
    ]

    for test_case in test_cases:
        print(overly_homogeneous_information_detector(test_case))

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_overly_homogeneous_information_detector = overly_homogeneous_information_detector

def overly_homogeneous_information_detector(input_text):
    _out = _sushi_raw_overly_homogeneous_information_detector(input_text)
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
