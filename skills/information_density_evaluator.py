import re
import math
from typing import Dict
from dataclasses import dataclass

@dataclass
class InformationDensityEvaluation:
    blocked: bool
    reason: str
    confidence: float
    category: str
    details: Dict[str, float]

def information_density_evaluator(input_text: str) -> Dict[str, object]:
    """
    Evaluates the density of information in a given input text, detecting potential oversimplification or information overload,
    and provides suggestions for improvement to maintain optimal cognitive engagement.

    Args:
    input_text (str): The input text to be evaluated.

    Returns:
    Dict[str, object]: A dictionary containing the evaluation results, including a boolean indicating whether the input is blocked,
    a reason for the blockage, a confidence score, a category, and additional details.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Tokenize the input text into sentences and words
    sentences = re.split(r'[.!?]', input_text)
    words = re.findall(r'\b\w+\b', input_text.lower())

    # Calculate lexical diversity
    lexical_diversity = len(set(words)) / len(words) if words else 0.0

    # Calculate hedging term density
    hedging_terms = ['maybe', 'possibly', 'could', 'might', 'should']
    hedge_density = sum(1 for word in words if word in hedging_terms) / len(words) if words else 0.0

    # Calculate absolute term density
    absolute_terms = ['always', 'never', 'all', 'none']
    absolutes_ratio = sum(1 for word in words if word in absolute_terms) / len(words) if words else 0.0

    # Calculate overgeneral term density
    overgeneral_terms = ['everyone', 'everything', 'all the time']
    overgeneral_terms_density = sum(1 for word in words if word in overgeneral_terms) / len(words) if words else 0.0

    # Calculate sentence complexity
    sentence_complexity = sum(len(re.findall(r'\b\w+\b', sentence)) for sentence in sentences) / len(sentences) if sentences else 0.0

    # Combine signals to calculate confidence
    raw_score = 0.2 * lexical_diversity + 0.3 * hedge_density + 0.2 * absolutes_ratio + 0.1 * overgeneral_terms_density + 0.2 * sentence_complexity
    confidence = max(0.0, min(1.0, raw_score))

    # Determine blockage and reason
    blocked = confidence < 0.4 or confidence > 0.7
    reason = 'Oversimplification' if confidence < 0.4 else 'Information Overload' if confidence > 0.7 else 'Optimal'

    # Determine category
    category = 'Oversimplification' if confidence < 0.4 else 'Information Overload' if confidence > 0.7 else 'Optimal'

    # Create evaluation result
    evaluation = InformationDensityEvaluation(
        blocked=blocked,
        reason=reason,
        confidence=confidence,
        category=category,
        details={
            'lexical_diversity': lexical_diversity,
            'hedge_density': hedge_density,
            'absolutes_ratio': absolutes_ratio,
            'overgeneral_terms_density': overgeneral_terms_density,
            'sentence_complexity': sentence_complexity
        }
    )

    # Return evaluation result as dictionary
    return {
        'blocked': evaluation.blocked,
        'reason': evaluation.reason,
        'confidence': evaluation.confidence,
        'category': evaluation.category,
        'details': evaluation.details
    }

if __name__ == '__main__':
    test_cases = [
        'This is a simple sentence.',
        'The quick brown fox jumps over the lazy dog.',
        'Maybe, possibly, could, might, or should we go to the store?',
        'Always, never, all, or none of the above are correct.',
        'Everyone, everything, all the time, is going to be okay.'
    ]

    for test_case in test_cases:
        evaluation = information_density_evaluator(test_case)
        print(f'Input: {test_case}')
        print(f'Blocked: {evaluation["blocked"]}')
        print(f'Reason: {evaluation["reason"]}')
        print(f'Confidence: {evaluation["confidence"]}')
        print(f'Category: {evaluation["category"]}')
        print(f'Details: {evaluation["details"]}')
        print('---')

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_information_density_evaluator = information_density_evaluator

def information_density_evaluator(input_text):
    _out = _sushi_raw_information_density_evaluator(input_text)
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
