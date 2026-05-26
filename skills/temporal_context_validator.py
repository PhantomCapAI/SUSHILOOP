import re
from typing import Dict
from dataclasses import dataclass
from math import log

@dataclass
class TemporalContext:
    """Temporal context information"""
    time_sensitive: bool
    temporal_context: str
    absolutes_ratio: float
    hedge_density: float
    overgeneral_terms: float

def calculate_temporal_context(input_text: str) -> TemporalContext:
    """
    Calculate temporal context information

    Args:
    input_text (str): Input text to analyze

    Returns:
    TemporalContext: Temporal context information
    """
    sentences = re.split(r'[.!?]', input_text)
    sentences = [s for s in sentences if s]  # remove empty strings

    time_sensitive = False
    temporal_context = ""
    absolutes_ratio = 0.0
    hedge_density = 0.0
    overgeneral_terms = 0.0

    # Check for time-sensitive keywords
    time_sensitive_keywords = ["yesterday", "today", "tomorrow", "next week", "last week"]
    for keyword in time_sensitive_keywords:
        if keyword in input_text.lower():
            time_sensitive = True
            temporal_context = keyword
            break

    # Calculate absolutes ratio
    absolutes = ["always", "never", "every"]
    absolute_count = sum(1 for sentence in sentences for absolute in absolutes if absolute in sentence.lower())
    if len(sentences) > 0:
        absolutes_ratio = absolute_count / len(sentences)

    # Calculate hedge density
    hedges = ["maybe", "perhaps", "possibly", "could", "might"]
    hedge_count = sum(1 for sentence in sentences for hedge in hedges if hedge in sentence.lower())
    if len(sentences) > 0:
        hedge_density = hedge_count / len(sentences)

    # Calculate overgeneral terms
    overgeneral_terms_list = ["everyone", "nobody", "all", "none"]
    overgeneral_terms_count = sum(1 for sentence in sentences for term in overgeneral_terms_list if term in sentence.lower())
    if len(sentences) > 0:
        overgeneral_terms = overgeneral_terms_count / len(sentences)

    return TemporalContext(time_sensitive, temporal_context, absolutes_ratio, hedge_density, overgeneral_terms)

def temporal_context_validator(input_text: str) -> Dict:
    """
    Temporal context validator

    This function checks if the input prompt or context provided to the AI model is time-sensitive
    and requires consideration of temporal factors, ensuring that the human user is aware of
    potential temporal biases or limitations in the AI's response.

    Args:
    input_text (str): Input text to analyze

    Returns:
    dict: Dictionary containing the result of the validation
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    temporal_context = calculate_temporal_context(input_text)

    # Calculate confidence
    raw_score = 0.5 * temporal_context.absolutes_ratio + 0.3 * temporal_context.hedge_density + 0.2 * temporal_context.overgeneral_terms
    confidence = max(0.0, min(1.0, raw_score))

    # Determine category
    category = "temporal_context"

    # Determine reason
    reason = ""
    if temporal_context.time_sensitive:
        reason = f"Time-sensitive keyword '{temporal_context.temporal_context}' detected"
    elif temporal_context.absolutes_ratio > 0.5:
        reason = "High absolutes ratio detected"
    elif temporal_context.hedge_density > 0.5:
        reason = "High hedge density detected"
    elif temporal_context.overgeneral_terms > 0.5:
        reason = "High overgeneral terms detected"
    else:
        reason = "No temporal context issues detected"

    # Determine blocked status
    blocked = confidence > 0.7

    # Create result dictionary
    result = {
        "blocked": blocked,
        "reason": reason,
        "confidence": confidence,
        "category": category,
        "details": {
            "time_sensitive": temporal_context.time_sensitive,
            "temporal_context": temporal_context.temporal_context,
            "absolutes_ratio": temporal_context.absolutes_ratio,
            "hedge_density": temporal_context.hedge_density,
            "overgeneral_terms": temporal_context.overgeneral_terms
        }
    }

    return result

if __name__ == "__main__":
    test_cases = [
        "I will always be there for you.",
        "Maybe it will rain tomorrow.",
        "Everyone loves this restaurant.",
        "The meeting is scheduled for yesterday.",
        "The new policy will be implemented next week.",
        "This is a test case with no temporal context.",
        "The company will never go bankrupt.",
        "The weather forecast says it will be sunny today.",
        "The new employee will start working tomorrow.",
        "The project deadline is next Friday."
    ]

    for test_case in test_cases:
        result = temporal_context_validator(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_temporal_context_validator = temporal_context_validator

def temporal_context_validator(input_text):
    _out = _sushi_raw_temporal_context_validator(input_text)
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
