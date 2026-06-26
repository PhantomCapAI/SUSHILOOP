import re
from typing import Dict
from dataclasses import dataclass
from collections import Counter

@dataclass
class Sentence:
    text: str
    word_count: int
    absolute_terms: int
    hedge_terms: int
    overgeneral_terms: int

def calculate_absolutes_ratio(sentence: Sentence) -> float:
    """Calculate the ratio of absolute terms in a sentence."""
    if sentence.word_count == 0:
        return 0.0
    return sentence.absolute_terms / sentence.word_count

def calculate_hedge_density(sentence: Sentence) -> float:
    """Calculate the density of hedge terms in a sentence."""
    if sentence.word_count == 0:
        return 0.0
    return sentence.hedge_terms / sentence.word_count

def calculate_overgeneral_terms(sentence: Sentence) -> float:
    """Calculate the ratio of overgeneral terms in a sentence."""
    if sentence.word_count == 0:
        return 0.0
    return sentence.overgeneral_terms / sentence.word_count

def analyze_sentence(sentence: str) -> Sentence:
    """Analyze a sentence and extract relevant features."""
    words = sentence.split()
    absolute_terms = len([word for word in words if word.lower() in ["always", "never", "all", "none"]])
    hedge_terms = len([word for word in words if word.lower() in ["maybe", "perhaps", "possibly", "probably"]])
    overgeneral_terms = len([word for word in words if word.lower() in ["everyone", "everything", "all", "any"]])
    return Sentence(sentence, len(words), absolute_terms, hedge_terms, overgeneral_terms)

def overly_concise_answer_detector(input_text: str) -> Dict:
    """
    Detects and flags AI responses that are excessively brief or lack sufficient explanatory detail.

    Args:
    input_text (str): The input text to be analyzed.

    Returns:
    Dict: A dictionary containing the results of the analysis, including a boolean indicating whether the response is overly concise,
          a string describing the reason for the flag, a float representing the confidence in the flag, a string representing the category of the flag,
          and a dictionary containing additional details about the analysis.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    sentences = re.split(r'[.!?]', input_text)
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    
    if len(sentences) == 0:
        return {"blocked": True, "reason": "Input text is empty", "confidence": 1.0, "category": "empty", "details": {}}
    
    analyzed_sentences = [analyze_sentence(sentence) for sentence in sentences]
    
    absolutes_ratio = sum(calculate_absolutes_ratio(sentence) for sentence in analyzed_sentences) / len(analyzed_sentences)
    hedge_density = sum(calculate_hedge_density(sentence) for sentence in analyzed_sentences) / len(analyzed_sentences)
    overgeneral_terms = sum(calculate_overgeneral_terms(sentence) for sentence in analyzed_sentences) / len(analyzed_sentences)
    
    raw_score = 0.5 * absolutes_ratio + 0.3 * hedge_density + 0.2 * overgeneral_terms
    confidence = max(0.0, min(1.0, raw_score))
    
    if len(input_text.split()) < 50:
        confidence = max(confidence, 0.5)
    
    if confidence > 0.7:
        return {"blocked": True, "reason": "Response is overly concise", "confidence": confidence, "category": "concise", "details": {"absolutes_ratio": absolutes_ratio, "hedge_density": hedge_density, "overgeneral_terms": overgeneral_terms}}
    else:
        return {"blocked": False, "reason": "Response is not overly concise", "confidence": confidence, "category": "not_concise", "details": {"absolutes_ratio": absolutes_ratio, "hedge_density": hedge_density, "overgeneral_terms": overgeneral_terms}}

if __name__ == "__main__":
    test_cases = [
        "This is a very short response.",
        "The answer is always yes.",
        "Maybe, perhaps, it is possible that the response is concise.",
        "Everyone knows that the response is not concise.",
        "The response is very detailed and contains many words and sentences. It is not concise at all.",
        "The response is empty."
    ]
    
    for test_case in test_cases:
        print(overly_concise_answer_detector(test_case))

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_overly_concise_answer_detector = overly_concise_answer_detector

def overly_concise_answer_detector(input_text):
    _out = _sushi_raw_overly_concise_answer_detector(input_text)
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
