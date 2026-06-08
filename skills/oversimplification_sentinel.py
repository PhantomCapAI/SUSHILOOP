import re
import math
from typing import Dict
from dataclasses import dataclass

@dataclass
class SentenceFeatures:
    """Features extracted from a sentence."""
    word_count: int
    clause_count: int
    absolute_terms: int
    hedge_terms: int

def extract_sentence_features(sentence: str) -> SentenceFeatures:
    """Extract features from a sentence."""
    word_count = len(re.findall(r'\b\w+\b', sentence))
    clause_count = len(re.findall(r'[.!?]', sentence))
    absolute_terms = len(re.findall(r'\b(always|never|all|none)\b', sentence, re.IGNORECASE))
    hedge_terms = len(re.findall(r'\b(maybe|perhaps|possibly|likely)\b', sentence, re.IGNORECASE))
    return SentenceFeatures(word_count, clause_count, absolute_terms, hedge_terms)

def calculate_sentence_complexity(sentence: str) -> float:
    """Calculate the complexity of a sentence."""
    features = extract_sentence_features(sentence)
    if features.word_count == 0:
        return 0.0
    clause_ratio = features.clause_count / features.word_count if features.word_count > 0 else 0.0
    absolute_ratio = features.absolute_terms / features.word_count if features.word_count > 0 else 0.0
    hedge_ratio = features.hedge_terms / features.word_count if features.word_count > 0 else 0.0
    return clause_ratio + absolute_ratio + hedge_ratio

def oversimplification_sentinel(input_text: str) -> Dict:
    """
    Detects when AI-generated text oversimplifies complex topics.

    This function uses a combination of signals to determine the complexity of the input text.
    It calculates the sentence complexity, lexical diversity, and hedge term density to determine
    the confidence of oversimplification.

    Args:
        input_text (str): The input text to be evaluated.

    Returns:
        Dict: A dictionary containing the results of the evaluation.
            - blocked (bool): Whether the text is blocked due to oversimplification.
            - reason (str): The reason for blocking the text.
            - confidence (float): The confidence of oversimplification, ranging from 0.0 to 1.0.
            - category (str): The category of the text, either "oversimplified" or "not oversimplified".
            - details (Dict): Additional details about the evaluation.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    sentences = re.split(r'[.!?]', input_text)
    sentence_complexities = [calculate_sentence_complexity(sentence) for sentence in sentences if sentence.strip()]
    if not sentence_complexities:
        return {
            "blocked": False,
            "reason": "No sentences found",
            "confidence": 0.0,
            "category": "not oversimplified",
            "details": {}
        }

    average_complexity = sum(sentence_complexities) / len(sentence_complexities)
    lexical_diversity = len(set(re.findall(r'\b\w+\b', input_text))) / len(re.findall(r'\b\w+\b', input_text)) if re.findall(r'\b\w+\b', input_text) else 0.0
    hedge_term_density = len(re.findall(r'\b(maybe|perhaps|possibly|likely)\b', input_text, re.IGNORECASE)) / len(re.findall(r'\b\w+\b', input_text)) if re.findall(r'\b\w+\b', input_text) else 0.0

    raw_score = 0.5 * (1 - average_complexity) + 0.3 * (1 - lexical_diversity) + 0.2 * (1 - hedge_term_density)
    confidence = max(0.0, min(1.0, raw_score))

    if confidence > 0.8:
        return {
            "blocked": True,
            "reason": "Oversimplification detected",
            "confidence": confidence,
            "category": "oversimplified",
            "details": {
                "average_complexity": average_complexity,
                "lexical_diversity": lexical_diversity,
                "hedge_term_density": hedge_term_density
            }
        }
    else:
        return {
            "blocked": False,
            "reason": "No oversimplification detected",
            "confidence": confidence,
            "category": "not oversimplified",
            "details": {
                "average_complexity": average_complexity,
                "lexical_diversity": lexical_diversity,
                "hedge_term_density": hedge_term_density
            }
        }

if __name__ == "__main__":
    test_cases = [
        "The sun is shining.",
        "The sun is shining, and the birds are singing.",
        "The sun is always shining, and the birds are always singing.",
        "Maybe the sun is shining, and perhaps the birds are singing.",
        "The sun is shining. The birds are singing. The flowers are blooming."
    ]

    for test_case in test_cases:
        print(oversimplification_sentinel(test_case))

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_oversimplification_sentinel = oversimplification_sentinel

def oversimplification_sentinel(input_text):
    _out = _sushi_raw_oversimplification_sentinel(input_text)
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
