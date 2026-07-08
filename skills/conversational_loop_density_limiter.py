import re
from typing import Dict
from dataclasses import dataclass
from math import log

@dataclass
class Result:
    blocked: bool
    reason: str
    confidence: float
    category: str
    details: Dict[str, float]

def conversational_loop_density_limiter(input_text: str) -> Dict:
    """
    This function detects and limits conversational loops where a user repeatedly asks similar questions 
    or receives similar responses within a short time frame, helping to prevent overreliance on AI-generated answers.
    
    It analyzes the conversational history to identify dense loops and throttles the response rate to encourage human reflection and exploration.
    
    Parameters:
    input_text (str): The input text to be analyzed.
    
    Returns:
    dict: A dictionary containing the result of the analysis, including whether the input is blocked, the reason, confidence, category, and details.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Initialize variables
    sentences = re.split(r'[.!?]', input_text)
    words = re.findall(r'\b\w+\b', input_text.lower())
    word_count = len(words)
    sentence_count = len([s for s in sentences if s.strip()])

    # Calculate lexical diversity
    if word_count > 0:
        lexical_diversity = len(set(words)) / word_count
    else:
        lexical_diversity = 0.0

    # Calculate hedging/absolute-term density
    hedge_terms = ['maybe', 'perhaps', 'possibly', 'probably', 'certainly', 'definitely']
    hedge_count = sum(1 for word in words if word in hedge_terms)
    if word_count > 0:
        hedge_density = hedge_count / word_count
    else:
        hedge_density = 0.0

    # Calculate weighted pattern matches
    pattern_matches = re.findall(r'\b(all|every|always|never)\b', input_text.lower())
    pattern_match_count = len(pattern_matches)
    if sentence_count > 0:
        pattern_match_ratio = pattern_match_count / sentence_count
    else:
        pattern_match_ratio = 0.0

    # Calculate raw score
    raw_score = 0.5 * pattern_match_ratio + 0.3 * hedge_density + 0.2 * (1 - lexical_diversity)

    # Clamp confidence
    confidence = max(0.0, min(1.0, raw_score))

    # Determine blocked status
    blocked = confidence >= 0.5

    # Create result dictionary
    result = {
        "blocked": blocked,
        "reason": "Conversational loop density limiter",
        "confidence": confidence,
        "category": "Conversational loop",
        "details": {
            "lexical_diversity": lexical_diversity,
            "hedge_density": hedge_density,
            "pattern_match_ratio": pattern_match_ratio
        }
    }

    return result

if __name__ == "__main__":
    test_cases = [
        "What is the meaning of life?",
        "I always wonder about the universe and its mysteries.",
        "This is a test case with no hedging terms or absolute language.",
        "Maybe we should consider the possibility of extraterrestrial life.",
        "Every time I ask a question, I get a similar response."
    ]

    for test_case in test_cases:
        result = conversational_loop_density_limiter(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_conversational_loop_density_limiter = conversational_loop_density_limiter

def conversational_loop_density_limiter(input_text):
    _out = _sushi_raw_conversational_loop_density_limiter(input_text)
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
