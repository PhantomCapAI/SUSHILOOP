import re
from collections import Counter
from dataclasses import dataclass
from typing import Dict

@dataclass
class DeliberationPaceNudgerResult:
    blocked: bool
    reason: str
    confidence: float
    category: str
    details: Dict[str, float]

def count_sentences(text: str) -> int:
    """Count the number of sentences in a given text."""
    return text.count('.') + text.count('!') + text.count('?')

def count_words(text: str) -> int:
    """Count the number of words in a given text."""
    return len(text.split())

def count_clauses(text: str) -> int:
    """Count the number of clauses in a given text."""
    return text.count(',') + text.count(';') + text.count(':')

def calculate_absolutes_ratio(text: str) -> float:
    """Calculate the ratio of absolute terms (e.g., always, never) in a given text."""
    absolute_terms = ['always', 'never', 'all', 'none']
    word_count = count_words(text)
    absolute_count = sum(1 for word in text.lower().split() if word in absolute_terms)
    return absolute_count / word_count if word_count > 0 else 0.0

def calculate_hedge_density(text: str) -> float:
    """Calculate the density of hedge terms (e.g., maybe, possibly) in a given text."""
    hedge_terms = ['maybe', 'possibly', 'perhaps', 'could', 'might']
    word_count = count_words(text)
    hedge_count = sum(1 for word in text.lower().split() if word in hedge_terms)
    return hedge_count / word_count if word_count > 0 else 0.0

def calculate_overgeneral_terms(text: str) -> float:
    """Calculate the ratio of overgeneral terms (e.g., everyone, nobody) in a given text."""
    overgeneral_terms = ['everyone', 'nobody', 'everybody', 'noone']
    word_count = count_words(text)
    overgeneral_count = sum(1 for word in text.lower().split() if word in overgeneral_terms)
    return overgeneral_count / word_count if word_count > 0 else 0.0

def calculate_lexical_diversity(text: str) -> float:
    """Calculate the lexical diversity of a given text."""
    words = text.lower().split()
    unique_words = set(words)
    return len(unique_words) / len(words) if len(words) > 0 else 0.0

def deliberation_pace_nudger(input_text: str) -> Dict:
    """
    Distinguishes rapid-fire dependent querying from deliberate use and adds a soft, overridable pause.

    This function combines multiple signals to detect compulsive querying patterns and returns a graded confidence score.
    The signals used include:
    - Absolute terms ratio
    - Hedge density
    - Overgeneral terms ratio
    - Lexical diversity
    - Sentence count
    - Clause count

    The confidence score is clamped between 0.0 and 1.0, and the `blocked` decision is made based on a threshold of 0.5.

    Args:
        input_text (str): The input text to be evaluated.

    Returns:
        Dict: A dictionary containing the evaluation results, including `blocked`, `reason`, `confidence`, `category`, and `details`.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    sentence_count = count_sentences(input_text)
    clause_count = count_clauses(input_text)
    absolutes_ratio = calculate_absolutes_ratio(input_text)
    hedge_density = calculate_hedge_density(input_text)
    overgeneral_terms = calculate_overgeneral_terms(input_text)
    lexical_diversity = calculate_lexical_diversity(input_text)

    raw_score = 0.2 * absolutes_ratio + 0.2 * hedge_density + 0.2 * overgeneral_terms + 0.2 * (1 - lexical_diversity) + 0.2 * (sentence_count / (clause_count + 1))
    confidence = max(0.0, min(1.0, raw_score))

    blocked = confidence >= 0.5
    reason = "Compulsive querying pattern detected" if blocked else "No compulsive querying pattern detected"
    category = "Deliberation Pace Nudger"
    details = {
        "sentence_count": sentence_count,
        "clause_count": clause_count,
        "absolutes_ratio": absolutes_ratio,
        "hedge_density": hedge_density,
        "overgeneral_terms": overgeneral_terms,
        "lexical_diversity": lexical_diversity,
    }

    return {
        "blocked": blocked,
        "reason": reason,
        "confidence": confidence,
        "category": category,
        "details": details,
    }

if __name__ == "__main__":
    test_cases = [
        "I always do this, and I never do that.",
        "Maybe I'll go to the store, or perhaps I'll stay home.",
        "Everyone loves this product, and nobody has any complaints.",
        "This is a test case with no compulsive querying pattern.",
        "I'm not sure what to do, but I'll figure it out eventually.",
    ]

    for test_case in test_cases:
        result = deliberation_pace_nudger(test_case)
        print(f"Input: {test_case}")
        print(f"Blocked: {result['blocked']}")
        print(f"Reason: {result['reason']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Category: {result['category']}")
        print(f"Details: {result['details']}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_deliberation_pace_nudger = deliberation_pace_nudger

def deliberation_pace_nudger(input_text):
    _out = _sushi_raw_deliberation_pace_nudger(input_text)
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
