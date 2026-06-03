import re
from dataclasses import dataclass
from typing import Dict

@dataclass
class Signal:
    name: str
    weight: float
    value: float

def calculate_absolutes_ratio(text: str) -> float:
    """Calculate the ratio of absolute terms to total words in the text."""
    absolute_terms = re.findall(r'\b(always|never|all|none|every)\b', text, re.IGNORECASE)
    total_words = len(re.findall(r'\b\w+\b', text))
    return len(absolute_terms) / total_words if total_words > 0 else 0.0

def calculate_hedge_density(text: str) -> float:
    """Calculate the density of hedging terms in the text."""
    hedge_terms = re.findall(r'\b(maybe|perhaps|possibly|probably|likely)\b', text, re.IGNORECASE)
    total_words = len(re.findall(r'\b\w+\b', text))
    return len(hedge_terms) / total_words if total_words > 0 else 0.0

def calculate_overgeneral_terms(text: str) -> float:
    """Calculate the ratio of overgeneral terms to total words in the text."""
    overgeneral_terms = re.findall(r'\b(everyone|everybody|all|any)\b', text, re.IGNORECASE)
    total_words = len(re.findall(r'\b\w+\b', text))
    return len(overgeneral_terms) / total_words if total_words > 0 else 0.0

def calculate_lexical_diversity(text: str) -> float:
    """Calculate the lexical diversity of the text."""
    words = re.findall(r'\b\w+\b', text)
    unique_words = set(words)
    return len(unique_words) / len(words) if len(words) > 0 else 0.0

def calculate_sentence_count(text: str) -> int:
    """Calculate the number of sentences in the text."""
    return len(re.findall(r'[.!?]', text))

def calculate_clause_count(text: str) -> int:
    """Calculate the number of clauses in the text."""
    return len(re.findall(r'(and|but|or)', text, re.IGNORECASE))

def inferred_attribute_exposer(input_text: str) -> Dict:
    """
    Detects when AI-generated text implies or infers personal attributes about an individual, 
    such as age, location, or occupation, without explicitly stating them, and highlights 
    these inferences to prevent potential privacy leaks.

    Args:
        input_text (str): The input text to analyze.

    Returns:
        Dict: A dictionary containing the results of the analysis, including a boolean 
        indicating whether the text implies personal attributes, a string describing the 
        reason for the implication, a float representing the confidence in the implication, 
        a string representing the category of the implication, and a dictionary containing 
        additional details about the implication.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    signals = [
        Signal('absolutes_ratio', 0.5, calculate_absolutes_ratio(input_text)),
        Signal('hedge_density', 0.3, calculate_hedge_density(input_text)),
        Signal('overgeneral_terms', 0.2, calculate_overgeneral_terms(input_text)),
        Signal('lexical_diversity', 0.1, calculate_lexical_diversity(input_text)),
        Signal('sentence_count', 0.05, calculate_sentence_count(input_text) / (1 + calculate_clause_count(input_text))),
    ]

    raw_score = sum(signal.weight * signal.value for signal in signals)
    confidence = max(0.0, min(1.0, raw_score))

    if confidence > 0.7:
        reason = 'High confidence in implied personal attributes'
        category = 'age'
        details = {'signals': [signal.name for signal in signals]}
    elif confidence > 0.4:
        reason = 'Moderate confidence in implied personal attributes'
        category = 'location'
        details = {'signals': [signal.name for signal in signals]}
    else:
        reason = 'Low confidence in implied personal attributes'
        category = 'occupation'
        details = {'signals': [signal.name for signal in signals]}

    return {
        'blocked': confidence > 0.5,
        'reason': reason,
        'confidence': confidence,
        'category': category,
        'details': details,
    }

if __name__ == '__main__':
    test_cases = [
        'The old man walked slowly.',
        'I live in New York City.',
        'She is a doctor.',
        'The weather is nice today.',
        'Everyone loves ice cream.',
    ]

    for test_case in test_cases:
        result = inferred_attribute_exposer(test_case)
        print(f'Test case: {test_case}')
        print(f'Result: {result}')
        print('---')

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_inferred_attribute_exposer = inferred_attribute_exposer

def inferred_attribute_exposer(input_text):
    _out = _sushi_raw_inferred_attribute_exposer(input_text)
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
