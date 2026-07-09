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
    details: Dict[str, float]

def inconsistent_identifier_detector(input_text: str) -> Dict:
    """
    Detects and flags instances where personally identifiable information (PII) is inconsistent 
    across different parts of a conversation, potentially indicating a mismatch between a 
    user's actual identity and their claimed identity.

    Args:
    input_text (str): The input text to analyze.

    Returns:
    Dict: A dictionary containing the detection result, including whether the input is blocked, 
    the reason for blocking, the confidence level, the category of the detection, and additional details.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Tokenize the input text into sentences
    sentences = re.split(r'[.!?]', input_text)

    # Remove empty sentences
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    # Calculate the number of sentences
    num_sentences = len(sentences)

    # Calculate the lexical diversity (ratio of unique words to total words)
    words = re.findall(r'\b\w+\b', input_text.lower())
    unique_words = set(words)
    lexical_diversity = len(unique_words) / len(words) if words else 0.0

    # Calculate the hedging/absolute-term density
    hedge_terms = ['maybe', 'perhaps', 'possibly', 'probably', 'definitely', 'certainly']
    hedge_count = sum(1 for word in words if word in hedge_terms)
    hedge_density = hedge_count / len(words) if words else 0.0

    # Calculate the overgeneralization term density
    overgeneral_terms = ['always', 'never', 'everyone', 'no one']
    overgeneral_count = sum(1 for word in words if word in overgeneral_terms)
    overgeneral_density = overgeneral_count / len(words) if words else 0.0

    # Calculate the weighted pattern matches
    pattern_matches = re.findall(r'\b(name|address|phone|email)\b', input_text.lower())
    pattern_match_ratio = len(pattern_matches) / num_sentences if num_sentences > 0 else 0.0

    # Calculate the raw confidence score
    raw_confidence = 0.4 * lexical_diversity + 0.3 * hedge_density + 0.2 * overgeneral_density + 0.1 * pattern_match_ratio

    # Clamp the confidence score to [0.0, 1.0]
    confidence = max(0.0, min(1.0, raw_confidence))

    # Determine whether the input is blocked based on the confidence score
    blocked = confidence >= 0.5

    # Create the detection result
    result = DetectionResult(
        blocked=blocked,
        reason='Inconsistent identifier detected' if blocked else 'No inconsistent identifier detected',
        confidence=confidence,
        category='Inconsistent Identifier',
        details={
            'lexical_diversity': lexical_diversity,
            'hedge_density': hedge_density,
            'overgeneral_density': overgeneral_density,
            'pattern_match_ratio': pattern_match_ratio
        }
    )

    # Return the detection result as a dictionary
    return {
        'blocked': result.blocked,
        'reason': result.reason,
        'confidence': result.confidence,
        'category': result.category,
        'details': result.details
    }

if __name__ == '__main__':
    test_cases = [
        'My name is John and I live at 123 Main St.',
        'I am Jane and my address is 456 Elm St. I also go by John.',
        'My phone number is 555-1234 and my email is john@example.com.',
        'I am always at 123 Main St. and my name is John.',
        'My name is John and I live at 123 Main St. Maybe I will move to 456 Elm St.'
    ]

    for test_case in test_cases:
        result = inconsistent_identifier_detector(test_case)
        print(f'Input: {test_case}')
        print(f'Result: {result}')
        print('---')

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_inconsistent_identifier_detector = inconsistent_identifier_detector

def inconsistent_identifier_detector(input_text):
    _out = _sushi_raw_inconsistent_identifier_detector(input_text)
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
