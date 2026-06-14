import re
from typing import Dict
from dataclasses import dataclass
from math import log

@dataclass
class ExplanationAnalysis:
    """Dataclass to hold the analysis of the input text."""
    sentence_count: int
    word_count: int
    absolute_terms: int
    hedge_terms: int
    overgeneral_terms: int
    lexical_diversity: float

def calculate_lexical_diversity(word_count: int, unique_word_count: int) -> float:
    """Calculate the lexical diversity of the input text."""
    if word_count == 0:
        return 0.0
    return unique_word_count / word_count

def calculate_absolute_terms(sentence: str) -> int:
    """Calculate the number of absolute terms in a sentence."""
    absolute_terms = re.findall(r'\b(always|never|all|none)\b', sentence, re.IGNORECASE)
    return len(absolute_terms)

def calculate_hedge_terms(sentence: str) -> int:
    """Calculate the number of hedge terms in a sentence."""
    hedge_terms = re.findall(r'\b(maybe|perhaps|possibly|probably)\b', sentence, re.IGNORECASE)
    return len(hedge_terms)

def calculate_overgeneral_terms(sentence: str) -> int:
    """Calculate the number of overgeneral terms in a sentence."""
    overgeneral_terms = re.findall(r'\b(everyone|everything|all)\b', sentence, re.IGNORECASE)
    return len(overgeneral_terms)

def analyze_text(input_text: str) -> ExplanationAnalysis:
    """Analyze the input text and return an ExplanationAnalysis object."""
    sentences = re.split(r'[.!?]', input_text)
    sentence_count = len(sentences)
    words = re.findall(r'\b\w+\b', input_text)
    word_count = len(words)
    unique_words = set(words)
    lexical_diversity = calculate_lexical_diversity(word_count, len(unique_words))
    absolute_terms = sum(calculate_absolute_terms(sentence) for sentence in sentences)
    hedge_terms = sum(calculate_hedge_terms(sentence) for sentence in sentences)
    overgeneral_terms = sum(calculate_overgeneral_terms(sentence) for sentence in sentences)
    return ExplanationAnalysis(
        sentence_count=sentence_count,
        word_count=word_count,
        absolute_terms=absolute_terms,
        hedge_terms=hedge_terms,
        overgeneral_terms=overgeneral_terms,
        lexical_diversity=lexical_diversity
    )

def overly_simplistic_explanation_detector(input_text: str) -> Dict:
    """
    Detects when AI-generated explanations oversimplify complex topics.

    This function analyzes the input text and returns a dictionary with the following keys:
    - blocked: Whether the explanation is blocked or not.
    - reason: The reason for blocking the explanation.
    - confidence: The confidence level of the detection, ranging from 0.0 to 1.0.
    - category: The category of the detection.
    - details: Additional details about the detection.

    The detection is based on a combination of signals, including:
    - Absolute term density
    - Hedge term density
    - Overgeneral term density
    - Lexical diversity

    The confidence level is calculated based on the strength of these signals.

    :param input_text: The input text to analyze.
    :return: A dictionary with the detection results.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    analysis = analyze_text(input_text)
    if analysis.sentence_count == 0:
        return {
            "blocked": False,
            "reason": "No sentences found",
            "confidence": 0.0,
            "category": "no_sentences",
            "details": {}
        }
    absolute_term_density = analysis.absolute_terms / analysis.sentence_count if analysis.sentence_count > 0 else 0.0
    hedge_term_density = analysis.hedge_terms / analysis.sentence_count if analysis.sentence_count > 0 else 0.0
    overgeneral_term_density = analysis.overgeneral_terms / analysis.sentence_count if analysis.sentence_count > 0 else 0.0
    raw_confidence = 0.5 * absolute_term_density + 0.3 * hedge_term_density + 0.2 * overgeneral_term_density
    confidence = max(0.0, min(1.0, raw_confidence))
    if confidence > 0.7:
        return {
            "blocked": True,
            "reason": "Oversimplified explanation detected",
            "confidence": confidence,
            "category": "oversimplification",
            "details": {
                "absolute_term_density": absolute_term_density,
                "hedge_term_density": hedge_term_density,
                "overgeneral_term_density": overgeneral_term_density
            }
        }
    else:
        return {
            "blocked": False,
            "reason": "No oversimplification detected",
            "confidence": confidence,
            "category": "no_oversimplification",
            "details": {
                "absolute_term_density": absolute_term_density,
                "hedge_term_density": hedge_term_density,
                "overgeneral_term_density": overgeneral_term_density
            }
        }

if __name__ == "__main__":
    test_cases = [
        "The sun always rises in the east.",
        "Maybe it will rain tomorrow.",
        "Everyone loves ice cream.",
        "The capital of France is Paris.",
        "The universe is infinite and everything is connected.",
        "The number 42 is the answer to all questions.",
        "The weather is always sunny in California.",
        "The best food in the world is pizza.",
        "The most popular sport in the world is soccer.",
        "The most intelligent animal is the human."
    ]
    for test_case in test_cases:
        print(overly_simplistic_explanation_detector(test_case))

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_overly_simplistic_explanation_detector = overly_simplistic_explanation_detector

def overly_simplistic_explanation_detector(input_text):
    _out = _sushi_raw_overly_simplistic_explanation_detector(input_text)
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
