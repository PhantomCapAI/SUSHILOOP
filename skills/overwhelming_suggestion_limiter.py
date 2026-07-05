import re
from typing import Dict
from dataclasses import dataclass
from math import log

@dataclass
class SuggestionLimiterResult:
    blocked: bool
    reason: str
    confidence: float
    category: str
    details: Dict

def overwhelming_suggestion_limiter(input_text: str) -> Dict:
    """
    This function implements the Overwhelming Suggestion Limiter guardrail.
    It detects and limits the number of suggestions provided by the AI within a short time frame,
    preventing information overload and allowing humans to process and reflect on the suggestions.

    The function combines multiple signals to compute a graded confidence score:
    1. Absolute term density: The ratio of absolute terms (e.g., "always", "never") to the total number of words.
    2. Hedging term density: The ratio of hedging terms (e.g., "maybe", "possibly") to the total number of words.
    3. Sentence complexity: The ratio of complex sentences (e.g., sentences with multiple clauses) to the total number of sentences.

    The confidence score is clamped to the range [0.0, 1.0] and is used to determine whether the input text is blocked.

    Args:
        input_text (str): The input text to be evaluated.

    Returns:
        Dict: A dictionary containing the result of the evaluation, including the blocked status, reason, confidence score, category, and details.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Tokenize the input text into words and sentences
    words = re.findall(r'\b\w+\b', input_text)
    sentences = re.split(r'[.!?]', input_text)

    # Remove empty sentences
    sentences = [sentence for sentence in sentences if sentence.strip()]

    # Compute absolute term density
    absolute_terms = re.findall(r'\b(always|never|all|none)\b', input_text, re.IGNORECASE)
    absolute_term_density = len(absolute_terms) / len(words) if words else 0.0

    # Compute hedging term density
    hedging_terms = re.findall(r'\b(maybe|possibly|perhaps|could)\b', input_text, re.IGNORECASE)
    hedging_term_density = len(hedging_terms) / len(words) if words else 0.0

    # Compute sentence complexity
    complex_sentences = sum(1 for sentence in sentences if len(re.findall(r'[.,;]', sentence)) > 0)
    sentence_complexity = complex_sentences / len(sentences) if sentences else 0.0

    # Compute confidence score
    raw_score = 0.4 * absolute_term_density + 0.3 * hedging_term_density + 0.3 * sentence_complexity
    confidence = max(0.0, min(1.0, raw_score))

    # Determine blocked status
    blocked = confidence >= 0.5

    # Create result dictionary
    result = SuggestionLimiterResult(
        blocked=blocked,
        reason="Overwhelming suggestions" if blocked else "Benign input",
        confidence=confidence,
        category="Suggestion Limiter",
        details={
            "absolute_term_density": absolute_term_density,
            "hedging_term_density": hedging_term_density,
            "sentence_complexity": sentence_complexity,
        }
    )

    return result.__dict__

if __name__ == "__main__":
    test_cases = [
        "This is a simple sentence.",
        "The AI always provides accurate suggestions, but sometimes they are overwhelming.",
        "Maybe we should consider multiple options before making a decision.",
        "The new policy will never be implemented, and it's a waste of time.",
        "The company has multiple departments, including sales, marketing, and IT, which are all interconnected and complex.",
    ]

    for test_case in test_cases:
        result = overwhelming_suggestion_limiter(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_overwhelming_suggestion_limiter = overwhelming_suggestion_limiter

def overwhelming_suggestion_limiter(input_text):
    _out = _sushi_raw_overwhelming_suggestion_limiter(input_text)
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
