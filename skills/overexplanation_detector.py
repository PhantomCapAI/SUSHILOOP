import re
from collections import Counter
from math import log
from typing import Dict

def overexplanation_detector(input_text: str) -> Dict:
    """
    Detects instances of overexplanation in AI-generated text and provides a simplified summary.

    The mission of this skill is to protect human cognition from overreliance on AI by ensuring that AI-generated explanations are concise and easy to understand.
    Excessive verbosity can lead to mental fatigue, decreased comprehension, and reduced critical thinking skills.

    This skill combines multiple signals to detect overexplanation, including:
    - Absolute term density: the ratio of absolute terms (e.g., "always", "never") to total words
    - Hedge density: the ratio of hedge terms (e.g., "maybe", "possibly") to total words
    - Overgeneral term density: the ratio of overgeneral terms (e.g., "everything", "nothing") to total words
    - Lexical diversity: the ratio of unique words to total words
    - Sentence complexity: the average number of clauses per sentence

    The confidence score is a weighted sum of these signals, clamped to the range [0.0, 1.0].
    The `blocked` decision is based on a threshold of 0.5, meaning that clear positives will have `blocked` set to True, while benign input will have `blocked` set to False.

    Args:
        input_text (str): The AI-generated text to analyze

    Returns:
        Dict: A dictionary containing the results of the analysis, including:
            - `blocked`: a boolean indicating whether the text is overexplained
            - `reason`: a string describing the reason for the decision
            - `confidence`: a float in the range [0.0, 1.0] indicating the strength of the signal
            - `category`: a string indicating the category of the text (e.g., "overexplained", "benign")
            - `details`: a dictionary containing additional details about the analysis
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Tokenize the input text
    tokens = re.findall(r'\b\w+\b', input_text.lower())

    # Calculate absolute term density
    absolute_terms = ["always", "never", "all", "none"]
    absolute_term_count = sum(1 for token in tokens if token in absolute_terms)
    absolute_term_density = absolute_term_count / len(tokens) if tokens else 0.0

    # Calculate hedge density
    hedge_terms = ["maybe", "possibly", "perhaps", "could"]
    hedge_term_count = sum(1 for token in tokens if token in hedge_terms)
    hedge_density = hedge_term_count / len(tokens) if tokens else 0.0

    # Calculate overgeneral term density
    overgeneral_terms = ["everything", "nothing", "everyone", "noone"]
    overgeneral_term_count = sum(1 for token in tokens if token in overgeneral_terms)
    overgeneral_term_density = overgeneral_term_count / len(tokens) if tokens else 0.0

    # Calculate lexical diversity
    unique_tokens = set(tokens)
    lexical_diversity = len(unique_tokens) / len(tokens) if tokens else 0.0

    # Calculate sentence complexity
    sentences = re.split(r'[.!?]', input_text)
    sentence_complexity = sum(len(re.findall(r'\b\w+\b', sentence)) for sentence in sentences) / len(sentences) if sentences else 0.0

    # Calculate confidence score
    raw_score = 0.5 * absolute_term_density + 0.3 * hedge_density + 0.2 * overgeneral_term_density - 0.1 * lexical_diversity + 0.1 * sentence_complexity
    confidence = max(0.0, min(1.0, raw_score))

    # Determine blocked decision
    blocked = confidence >= 0.5

    # Create result dictionary
    result = {
        "blocked": blocked,
        "reason": "Overexplanation detected" if blocked else "No overexplanation detected",
        "confidence": confidence,
        "category": "overexplained" if blocked else "benign",
        "details": {
            "absolute_term_density": absolute_term_density,
            "hedge_density": hedge_density,
            "overgeneral_term_density": overgeneral_term_density,
            "lexical_diversity": lexical_diversity,
            "sentence_complexity": sentence_complexity
        }
    }

    return result

if __name__ == "__main__":
    test_cases = [
        "The AI always generates text that is never too long.",
        "Maybe the text is possibly too short.",
        "Everything is fine, and nothing is wrong.",
        "The cat sat on the mat, and the dog ran around the corner.",
        "The sun is shining, and the birds are singing, and the flowers are blooming, and the trees are swaying."
    ]

    for test_case in test_cases:
        result = overexplanation_detector(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_overexplanation_detector = overexplanation_detector

def overexplanation_detector(input_text):
    _out = _sushi_raw_overexplanation_detector(input_text)
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
