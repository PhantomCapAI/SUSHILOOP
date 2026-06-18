import re
from typing import Dict
from dataclasses import dataclass
from math import log

@dataclass
class InsufficientNuanceIndicatorResult:
    blocked: bool
    reason: str
    confidence: float
    category: str
    details: Dict[str, float]

def insufficient_nuance_indicator(input_text: str) -> Dict:
    """
    Detects AI-generated content that oversimplifies complex issues by using absolute language, 
    failing to acknowledge potential counterarguments, or neglecting to provide evidence-based 
    support for claims. This function helps protect human cognition by promoting critical thinking 
    and nuanced understanding.

    Args:
        input_text (str): The text to be analyzed.

    Returns:
        Dict: A dictionary containing the results of the analysis, including whether the text 
        is blocked, the reason for blocking, the confidence level, the category of the issue, 
        and additional details.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Initialize the result object
    result = InsufficientNuanceIndicatorResult(False, "", 0.0, "insufficient_nuance", {})

    # Tokenize the input text
    tokens = re.findall(r'\b\w+\b', input_text.lower())

    # Calculate the absolute language ratio
    absolute_terms = ["always", "never", "all", "none"]
    absolute_count = sum(1 for token in tokens if token in absolute_terms)
    absolute_ratio = absolute_count / len(tokens) if tokens else 0.0

    # Calculate the hedge density
    hedge_terms = ["maybe", "perhaps", "possibly", "likely"]
    hedge_count = sum(1 for token in tokens if token in hedge_terms)
    hedge_density = hedge_count / len(tokens) if tokens else 0.0

    # Calculate the overgeneralization term ratio
    overgeneral_terms = ["everyone", "nobody", "everything", "nothing"]
    overgeneral_count = sum(1 for token in tokens if token in overgeneral_terms)
    overgeneral_ratio = overgeneral_count / len(tokens) if tokens else 0.0

    # Calculate the lexical diversity
    unique_tokens = set(tokens)
    lexical_diversity = len(unique_tokens) / len(tokens) if tokens else 0.0

    # Calculate the raw score
    raw_score = 0.4 * absolute_ratio + 0.3 * (1 - hedge_density) + 0.2 * overgeneral_ratio + 0.1 * (1 - lexical_diversity)

    # Clamp the confidence level
    confidence = max(0.0, min(1.0, raw_score))

    # Update the result object
    result.blocked = confidence > 0.7
    result.reason = "Insufficient nuance detected" if result.blocked else "No issues detected"
    result.confidence = confidence
    result.details = {
        "absolute_ratio": absolute_ratio,
        "hedge_density": hedge_density,
        "overgeneral_ratio": overgeneral_ratio,
        "lexical_diversity": lexical_diversity
    }

    # Return the result as a dictionary
    return {
        "blocked": result.blocked,
        "reason": result.reason,
        "confidence": result.confidence,
        "category": result.category,
        "details": result.details
    }

if __name__ == "__main__":
    test_cases = [
        "This is a simple statement.",
        "The answer is always yes.",
        "Maybe it's possible that everyone will agree.",
        "The new policy is a disaster and will never work.",
        "The company is great and everyone loves working there.",
        "The research shows that the treatment is effective in most cases.",
        "I'm not sure what to think about the new development.",
        "The data clearly indicates that the trend is upwards.",
        "It's impossible to predict the outcome with certainty.",
        "The team is confident that they can win the championship."
    ]

    for test_case in test_cases:
        print(insufficient_nuance_indicator(test_case))

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_insufficient_nuance_indicator = insufficient_nuance_indicator

def insufficient_nuance_indicator(input_text):
    _out = _sushi_raw_insufficient_nuance_indicator(input_text)
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
