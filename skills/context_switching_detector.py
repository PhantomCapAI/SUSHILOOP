import re
from collections import Counter
from dataclasses import dataclass
from typing import Dict

@dataclass
class ContextSwitchingResult:
    blocked: bool
    reason: str
    confidence: float
    category: str
    details: Dict[str, float]

def context_switching_detector(input_text: str) -> Dict:
    """
    Detects context switching in a given input text.

    This function combines multiple signals to determine the likelihood of context switching.
    It uses a weighted sum of the following signals:
    - Absolute term density: The ratio of absolute terms (e.g., "always", "never") to the total number of words.
    - Hedge term density: The ratio of hedge terms (e.g., "maybe", "possibly") to the total number of words.
    - Overgeneral term density: The ratio of overgeneral terms (e.g., "everyone", "everything") to the total number of words.
    - Sentence count: The number of sentences in the input text.
    - Lexical diversity: The ratio of unique words to the total number of words.

    The confidence score is a graded value between 0.0 and 1.0, where higher values indicate a higher likelihood of context switching.

    Args:
        input_text (str): The input text to analyze.

    Returns:
        Dict: A dictionary containing the result of the analysis, including the blocked status, reason, confidence score, category, and details.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Tokenize the input text into words
    words = re.findall(r'\b\w+\b', input_text.lower())

    # Calculate the absolute term density
    absolute_terms = ["always", "never", "all", "none"]
    absolute_term_count = sum(1 for word in words if word in absolute_terms)
    absolute_term_density = absolute_term_count / len(words) if words else 0.0

    # Calculate the hedge term density
    hedge_terms = ["maybe", "possibly", "perhaps", "could", "might"]
    hedge_term_count = sum(1 for word in words if word in hedge_terms)
    hedge_term_density = hedge_term_count / len(words) if words else 0.0

    # Calculate the overgeneral term density
    overgeneral_terms = ["everyone", "everything", "everybody", "all"]
    overgeneral_term_count = sum(1 for word in words if word in overgeneral_terms)
    overgeneral_term_density = overgeneral_term_count / len(words) if words else 0.0

    # Calculate the sentence count
    sentences = re.split(r'[.!?]', input_text)
    sentence_count = len([sentence for sentence in sentences if sentence.strip()])

    # Calculate the lexical diversity
    unique_words = len(set(words))
    lexical_diversity = unique_words / len(words) if words else 0.0

    # Calculate the weighted sum of the signals
    raw_score = 0.2 * absolute_term_density + 0.3 * hedge_term_density + 0.2 * overgeneral_term_density + 0.1 * sentence_count + 0.2 * (1 - lexical_diversity)

    # Clamp the confidence score to the range [0.0, 1.0]
    confidence = max(0.0, min(1.0, raw_score))

    # Determine the blocked status based on the confidence score
    blocked = confidence >= 0.5

    # Create the result dictionary
    result = {
        "blocked": blocked,
        "reason": "Context switching detected" if blocked else "No context switching detected",
        "confidence": confidence,
        "category": "Context Switching",
        "details": {
            "absolute_term_density": absolute_term_density,
            "hedge_term_density": hedge_term_density,
            "overgeneral_term_density": overgeneral_term_density,
            "sentence_count": sentence_count,
            "lexical_diversity": lexical_diversity
        }
    }

    return result

if __name__ == "__main__":
    test_cases = [
        "I always go to the store and buy everything.",
        "Maybe I will go to the park tomorrow.",
        "Everyone loves to play soccer.",
        "The cat sat on the mat.",
        "The dog ran quickly, but the cat was lazy.",
        "I never go to the movies on Friday nights."
    ]

    for test_case in test_cases:
        result = context_switching_detector(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_context_switching_detector = context_switching_detector

def context_switching_detector(input_text):
    _out = _sushi_raw_context_switching_detector(input_text)
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
