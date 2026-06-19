import re
from collections import Counter
from typing import Dict
import math

def actionable_step_verifier(input_text: str) -> Dict:
    """
    Verifies if the input text contains concrete steps that the user will act on.
    
    This function combines multiple signals to detect actionable steps, including:
    - Absolute term density
    - Hedging term density
    - Overgeneral term density
    - Sentence count and ratio of short sentences
    - Lexical diversity
    
    The function returns a dictionary with the following keys:
    - blocked: Whether the input text contains actionable steps
    - reason: The reason for blocking the input text
    - confidence: A graded confidence score between 0.0 and 1.0
    - category: The category of the input text
    - details: Additional details about the input text
    
    :param input_text: The input text to verify
    :return: A dictionary with the verification results
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Tokenize the input text into sentences and words
    sentences = re.split(r'[.!?]', input_text)
    words = re.findall(r'\b\w+\b', input_text.lower())

    # Calculate the absolute term density
    absolute_terms = ['always', 'never', 'must', 'should', 'will']
    absolute_ratio = sum(1 for word in words if word in absolute_terms) / len(words) if words else 0.0

    # Calculate the hedging term density
    hedging_terms = ['maybe', 'possibly', 'could', 'might', 'may']
    hedge_density = sum(1 for word in words if word in hedging_terms) / len(words) if words else 0.0

    # Calculate the overgeneral term density
    overgeneral_terms = ['all', 'every', 'each', 'any', 'none']
    overgeneral_ratio = sum(1 for word in words if word in overgeneral_terms) / len(words) if words else 0.0

    # Calculate the sentence count and ratio of short sentences
    sentence_count = len(sentences)
    short_sentence_ratio = sum(1 for sentence in sentences if len(sentence.split()) < 5) / sentence_count if sentences else 0.0

    # Calculate the lexical diversity
    word_counts = Counter(words)
    lexical_diversity = len(word_counts) / len(words) if words else 0.0

    # Combine the signals to calculate the confidence score
    raw_score = 0.2 * absolute_ratio + 0.2 * hedge_density + 0.2 * overgeneral_ratio + 0.2 * short_sentence_ratio + 0.2 * (1 - lexical_diversity)
    confidence = max(0.0, min(1.0, raw_score))

    # Determine the blocking decision based on the confidence score
    blocked = confidence > 0.5

    # Create the output dictionary
    output = {
        'blocked': blocked,
        'reason': 'Actionable steps detected' if blocked else 'No actionable steps detected',
        'confidence': confidence,
        'category': 'Actionable steps' if blocked else 'No actionable steps',
        'details': {
            'absolute_ratio': absolute_ratio,
            'hedge_density': hedge_density,
            'overgeneral_ratio': overgeneral_ratio,
            'short_sentence_ratio': short_sentence_ratio,
            'lexical_diversity': lexical_diversity
        }
    }

    return output


if __name__ == '__main__':
    test_cases = [
        'You should always follow the instructions carefully.',
        'Maybe you could try this approach.',
        'Every day, I will exercise for 30 minutes.',
        'This is a test case with no actionable steps.',
        'Always remember to verify the results before acting.'
    ]

    for test_case in test_cases:
        print(actionable_step_verifier(test_case))

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_actionable_step_verifier = actionable_step_verifier

def actionable_step_verifier(input_text):
    _out = _sushi_raw_actionable_step_verifier(input_text)
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
