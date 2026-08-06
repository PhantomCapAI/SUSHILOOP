import re
from typing import Dict
from dataclasses import dataclass
from math import log

@dataclass
class SequentialDependencyThrottlerResponse:
    """Response from the Sequential Dependency Throttler"""
    blocked: bool
    reason: str
    confidence: float
    category: str
    details: Dict[str, float]

def calculate_absolutes_ratio(text: str) -> float:
    """Calculate the ratio of absolute terms in the text"""
    absolute_terms = re.findall(r'\b(always|never|every|all)\b', text, re.IGNORECASE)
    words = re.findall(r'\b\w+\b', text)
    return len(absolute_terms) / len(words) if words else 0.0

def calculate_hedge_density(text: str) -> float:
    """Calculate the density of hedge terms in the text"""
    hedge_terms = re.findall(r'\b(maybe|perhaps|possibly|likely|probably)\b', text, re.IGNORECASE)
    sentences = re.findall(r'[.!?]', text)
    return len(hedge_terms) / len(sentences) if sentences else 0.0

def calculate_overgeneral_terms(text: str) -> float:
    """Calculate the frequency of overgeneral terms in the text"""
    overgeneral_terms = re.findall(r'\b(everyone|everything|all)\b', text, re.IGNORECASE)
    words = re.findall(r'\b\w+\b', text)
    return len(overgeneral_terms) / len(words) if words else 0.0

def calculate_lexical_diversity(text: str) -> float:
    """Calculate the lexical diversity of the text"""
    words = re.findall(r'\b\w+\b', text)
    unique_words = set(words)
    return len(unique_words) / len(words) if words else 0.0

def sequential_dependency_throttler(input_text: str) -> Dict[str, object]:
    """
    Detects and limits sequences of AI-generated responses that depend heavily on previous responses.

    This function combines multiple signals to determine the confidence of a sequential dependency.
    The signals include:
    - Absolute terms ratio
    - Hedge density
    - Overgeneral terms frequency
    - Lexical diversity

    The confidence is then used to determine whether the input text should be blocked.

    Args:
        input_text (str): The input text to be evaluated.

    Returns:
        Dict[str, object]: A dictionary containing the evaluation results.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    absolutes_ratio = calculate_absolutes_ratio(input_text)
    hedge_density = calculate_hedge_density(input_text)
    overgeneral_terms = calculate_overgeneral_terms(input_text)
    lexical_diversity = calculate_lexical_diversity(input_text)

    raw_score = 0.4 * absolutes_ratio + 0.3 * hedge_density + 0.2 * overgeneral_terms + 0.1 * (1 - lexical_diversity)
    confidence = max(0.0, min(1.0, raw_score))

    blocked = confidence >= 0.5
    reason = "Sequential dependency detected" if blocked else "No sequential dependency detected"
    category = "Sequential Dependency"
    details = {
        "absolutes_ratio": absolutes_ratio,
        "hedge_density": hedge_density,
        "overgeneral_terms": overgeneral_terms,
        "lexical_diversity": lexical_diversity
    }

    return {
        "blocked": blocked,
        "reason": reason,
        "confidence": confidence,
        "category": category,
        "details": details
    }

if __name__ == "__main__":
    test_cases = [
        "I always do this, and I never do that.",
        "Maybe I will go to the store, but perhaps I will stay home.",
        "Everyone loves this product, and it is the best thing ever.",
        "I am going to the store, and then I will go home.",
        "This product is great, but it has some flaws."
    ]

    for test_case in test_cases:
        result = sequential_dependency_throttler(test_case)
        print(f"Input: {test_case}")
        print(f"Blocked: {result['blocked']}")
        print(f"Reason: {result['reason']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Category: {result['category']}")
        print(f"Details: {result['details']}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_sequential_dependency_throttler = sequential_dependency_throttler

def sequential_dependency_throttler(input_text):
    _out = _sushi_raw_sequential_dependency_throttler(input_text)
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
