import re
from collections import Counter
from math import log
from typing import Dict

def feedback_loop_closure_detector(input_text: str) -> Dict:
    """
    Detects self-referential feedback loops in user input and alerts users to reframe their queries.

    This function combines multiple signals to detect potential feedback loops, including:
    - Absolute term density
    - Hedging term density
    - Overgeneral term density
    - Lexical diversity
    - Sentence structure

    The confidence score is a graded value between 0.0 and 1.0, representing the likelihood of a feedback loop.

    Args:
        input_text (str): The user input text to analyze.

    Returns:
        dict: A dictionary containing the analysis results, including:
            - blocked (bool): Whether the input text is likely to create a feedback loop.
            - reason (str): A brief explanation of the detection result.
            - confidence (float): A graded confidence score between 0.0 and 1.0.
            - category (str): The category of the detection result (e.g., "feedback loop").
            - details (dict): Additional details about the detection result, including signal scores.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Preprocess the input text
    input_text = input_text.lower()
    sentences = re.split(r'[.!?]', input_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = re.findall(r'\b\w+\b', input_text)

    # Calculate signal scores
    absolute_terms = ['always', 'never', 'every', 'all']
    absolute_ratio = sum(1 for w in words if w in absolute_terms) / len(words) if words else 0.0
    hedge_terms = ['maybe', 'perhaps', 'possibly', 'probably']
    hedge_density = sum(1 for w in words if w in hedge_terms) / len(words) if words else 0.0
    overgeneral_terms = ['everyone', 'everything', 'always', 'never']
    overgeneral_ratio = sum(1 for w in words if w in overgeneral_terms) / len(words) if words else 0.0
    lexical_diversity = len(set(words)) / len(words) if words else 0.0
    sentence_structure = len(sentences) / (len(words) / 10.0) if words else 0.0

    # Combine signal scores
    raw_score = 0.4 * absolute_ratio + 0.3 * hedge_density + 0.2 * overgeneral_ratio + 0.1 * (1 - lexical_diversity) + 0.1 * sentence_structure
    confidence = max(0.0, min(1.0, raw_score))

    # Determine the detection result
    blocked = confidence > 0.7
    reason = "Potential feedback loop detected" if blocked else "No feedback loop detected"
    category = "feedback loop"
    details = {
        "absolute_ratio": absolute_ratio,
        "hedge_density": hedge_density,
        "overgeneral_ratio": overgeneral_ratio,
        "lexical_diversity": lexical_diversity,
        "sentence_structure": sentence_structure,
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
        "I always believe what the AI says.",
        "Maybe the AI is right, but I'm not sure.",
        "Everyone knows that the AI is always correct.",
        "The AI said it, so it must be true.",
        "I'm not sure what to think, can you help me?",
        "The AI is probably right, but I need to verify.",
        "I never question the AI's responses.",
        "The AI said it, and I believe it.",
        "I'm not sure what to do, can you give me some advice?",
        "The AI is always right, and I trust it completely.",
    ]

    for test_case in test_cases:
        result = feedback_loop_closure_detector(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_feedback_loop_closure_detector = feedback_loop_closure_detector

def feedback_loop_closure_detector(input_text):
    _out = _sushi_raw_feedback_loop_closure_detector(input_text)
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
