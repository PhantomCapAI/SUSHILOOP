import re
import json
import math
from typing import Dict
from dataclasses import dataclass

@dataclass
class ConversationAnalysis:
    """Holds the results of the conversation analysis."""
    absolutes_ratio: float
    hedge_density: float
    overgeneral_terms: float
    sentence_count: int
    word_count: int

def calculate_absolutes_ratio(input_text: str) -> float:
    """Calculates the ratio of absolute terms in the input text."""
    absolute_terms = re.findall(r"\b(always|never|every|all)\b", input_text, re.IGNORECASE)
    word_count = len(re.findall(r"\b\w+\b", input_text))
    return len(absolute_terms) / word_count if word_count > 0 else 0.0

def calculate_hedge_density(input_text: str) -> float:
    """Calculates the density of hedge terms in the input text."""
    hedge_terms = re.findall(r"\b(maybe|perhaps|possibly|probably)\b", input_text, re.IGNORECASE)
    sentence_count = len(re.findall(r"[.!?]", input_text))
    return len(hedge_terms) / sentence_count if sentence_count > 0 else 0.0

def calculate_overgeneral_terms(input_text: str) -> float:
    """Calculates the ratio of overgeneral terms in the input text."""
    overgeneral_terms = re.findall(r"\b(everyone|everything|all)\b", input_text, re.IGNORECASE)
    word_count = len(re.findall(r"\b\w+\b", input_text))
    return len(overgeneral_terms) / word_count if word_count > 0 else 0.0

def analyze_conversation(input_text: str) -> ConversationAnalysis:
    """Analyzes the conversation and returns the results."""
    absolutes_ratio = calculate_absolutes_ratio(input_text)
    hedge_density = calculate_hedge_density(input_text)
    overgeneral_terms = calculate_overgeneral_terms(input_text)
    sentence_count = len(re.findall(r"[.!?]", input_text))
    word_count = len(re.findall(r"\b\w+\b", input_text))
    return ConversationAnalysis(absolutes_ratio, hedge_density, overgeneral_terms, sentence_count, word_count)

def conversational_loopback_limiter(input_text: str) -> Dict:
    """
    This function detects and limits the number of times a user can engage in a conversational loop with an AI.
    
    It analyzes the conversation history to identify repetitive patterns and intervenes when a threshold is reached.
    
    The mission of this function is to protect human cognition by preventing users from relying too heavily on AI-generated responses, 
    which can stifle critical thinking and problem-solving skills. By limiting conversational loopbacks, users are encouraged to think more deeply about the topic and generate their own responses.
    
    The function returns a dictionary with the following keys:
    - blocked: A boolean indicating whether the conversational loopback is blocked.
    - reason: A string explaining why the conversational loopback is blocked.
    - confidence: A float between 0.0 and 1.0 indicating the confidence level of the block.
    - category: A string indicating the category of the block.
    - details: A dictionary with additional details about the block.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    analysis = analyze_conversation(input_text)
    raw_score = 0.5 * analysis.absolutes_ratio + 0.3 * analysis.hedge_density + 0.2 * analysis.overgeneral_terms
    confidence = max(0.0, min(1.0, raw_score))
    blocked = confidence >= 0.5
    reason = "Conversational loopback detected" if blocked else "No conversational loopback detected"
    category = "Conversational Loopback Limiter"
    details = {
        "absolutes_ratio": analysis.absolutes_ratio,
        "hedge_density": analysis.hedge_density,
        "overgeneral_terms": analysis.overgeneral_terms,
        "sentence_count": analysis.sentence_count,
        "word_count": analysis.word_count
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
        "I always do this and it works every time.",
        "Maybe I should try something new, but I'm not sure.",
        "Everyone does it this way, so it must be right.",
        "I'm not sure what to do, can you help me?",
        "This is a test case with no conversational loopback."
    ]
    for test_case in test_cases:
        result = conversational_loopback_limiter(test_case)
        print(json.dumps(result, indent=4))

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_conversational_loopback_limiter = conversational_loopback_limiter

def conversational_loopback_limiter(input_text):
    _out = _sushi_raw_conversational_loopback_limiter(input_text)
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
