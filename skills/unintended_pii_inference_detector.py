import re
import math
from typing import Dict
from dataclasses import dataclass

@dataclass
class PIIInference:
    blocked: bool
    reason: str
    confidence: float
    category: str
    details: Dict

def unintended_pii_inference_detector(input_text: str) -> Dict:
    """
    Detects when AI-generated text inadvertently reveals personally identifiable information (PII) 
    through subtle context clues, such as mentioning specific locations or organizations that 
    could be linked to an individual.

    Args:
        input_text (str): The AI-generated text to analyze.

    Returns:
        Dict: A dictionary containing the detection results, including a boolean indicating 
        whether the text is blocked, a reason for the block, a confidence score, a category 
        for the PII inference, and additional details.

    Mission Alignment:
        This skill promotes more mindful and responsible AI-generated content by detecting 
        and flagging potential PII inferences, which helps prevent unintentional exposure of 
        sensitive information and protects human cognition.
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
    absolute_terms = ['always', 'never', 'definitely', 'certainly']
    hedge_density = sum(1 for token in tokens if token in hedge_terms) / len(tokens) if tokens else 0.0
    absolute_density = sum(1 for token in tokens if token in absolute_terms) / len(tokens) if tokens else 0.0

    # Calculate weighted pattern matches
    location_terms = ['city', 'town', 'state', 'country']
    organization_terms = ['company', 'school', 'hospital', 'government']
    location_matches = sum(1 for token in tokens if token in location_terms)
    organization_matches = sum(1 for token in tokens if token in organization_terms)
    weighted_matches = (location_matches + organization_matches) / len(tokens) if tokens else 0.0

    # Calculate raw score
    raw_score = 0.4 * lexical_diversity + 0.3 * hedge_density + 0.2 * absolute_density + 0.1 * weighted_matches

    # Clamp confidence score
    confidence = max(0.0, min(1.0, raw_score))

    # Determine block status and reason
    blocked = confidence > 0.7
    reason = 'Potential PII inference detected' if blocked else 'No PII inference detected'

    # Determine category and details
    category = 'Location' if location_matches > organization_matches else 'Organization'
    details = {
        'lexical_diversity': lexical_diversity,
        'hedge_density': hedge_density,
        'absolute_density': absolute_density,
        'weighted_matches': weighted_matches
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
        'The company is located in New York City.',
        'I live in a small town in the countryside.',
        'The hospital is a great place to work.',
        'I love visiting the city during the summer.',
        'The school is a wonderful place to learn.'
    ]

    for test_case in test_cases:
        result = unintended_pii_inference_detector(test_case)
        print(f'Input: {test_case}')
        print(f'Result: {result}')
        print('---')

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_unintended_pii_inference_detector = unintended_pii_inference_detector

def unintended_pii_inference_detector(input_text):
    _out = _sushi_raw_unintended_pii_inference_detector(input_text)
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
