import re
from collections import Counter
from typing import Dict

def actionable_step_verifier(input_text: str) -> Dict:
    """
    Actionable Step Verifier: Injects a 'verify these before acting' checkpoint when output contains concrete steps.

    Mission Alignment:
    This module aims to provide a safety guardrail for AI outputs by detecting and flagging potentially actionable steps.
    It combines multiple signals, including weighted pattern matches, structural features, and lexical diversity,
    to produce a graded confidence score that varies with the input.

    Args:
        input_text (str): The input text to be verified.

    Returns:
        Dict: A dictionary containing the verification result, including:
            - blocked (bool): Whether the input text contains potentially actionable steps.
            - reason (str): The reason for the verification result.
            - confidence (float): A graded confidence score between 0.0 and 1.0.
            - category (str): The category of the verification result.
            - details (Dict): Additional details about the verification result.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Preprocessing
    input_text = input_text.lower()
    sentences = re.split(r'[.!?]', input_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = re.findall(r'\b\w+\b', input_text)
    word_count = len(words)

    # Signal 1: Weighted pattern matches
    pattern_matches = re.findall(r'\b(step|action|instruction)\b', input_text)
    pattern_match_ratio = len(pattern_matches) / word_count if word_count > 0 else 0

    # Signal 2: Structural features
    sentence_count = len(sentences)
    sentence_ratio = sentence_count / word_count if word_count > 0 else 0

    # Signal 3: Lexical diversity
    word_freq = Counter(words)
    lexical_diversity = len(word_freq) / word_count if word_count > 0 else 0

    # Signal 4: Hedging/absolute-term density
    hedge_terms = re.findall(r'\b(maybe|perhaps|possibly|probably)\b', input_text)
    absolute_terms = re.findall(r'\b(always|never|definitely)\b', input_text)
    hedge_density = len(hedge_terms) / word_count if word_count > 0 else 0
    absolute_term_density = len(absolute_terms) / word_count if word_count > 0 else 0

    # Combine signals
    raw_score = 0.4 * pattern_match_ratio + 0.3 * sentence_ratio + 0.2 * lexical_diversity + 0.1 * hedge_density
    confidence = max(0.0, min(1.0, raw_score))

    # Determine verification result
    blocked = confidence > 0.5
    reason = "Potentially actionable steps detected" if blocked else "No potentially actionable steps detected"
    category = "Actionable Step" if blocked else "Non-Actionable Step"
    details = {
        "pattern_match_ratio": pattern_match_ratio,
        "sentence_ratio": sentence_ratio,
        "lexical_diversity": lexical_diversity,
        "hedge_density": hedge_density,
        "absolute_term_density": absolute_term_density
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
        "Please follow these steps to complete the task.",
        "This is a non-actionable sentence.",
        "Maybe you should consider taking this action.",
        "Always follow the instructions carefully.",
        "This sentence contains multiple actionable steps, including step 1 and step 2.",
        "The task requires careful consideration and attention to detail.",
        "You should probably take this action, but maybe not.",
        "The instructions are clear and easy to follow.",
        "This is a test case with multiple sentences. The first sentence is non-actionable. The second sentence contains actionable steps.",
        "The task requires careful planning and execution."
    ]

    for test_case in test_cases:
        result = actionable_step_verifier(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_actionable_step_verifier = actionable_step_verifier

def actionable_step_verifier(input_text):
    _out = _sushi_raw_actionable_step_verifier(input_text)
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
