import re
import json
import math
from typing import Dict
from dataclasses import dataclass
from collections import Counter

@dataclass
class DetectionResult:
    blocked: bool
    reason: str
    confidence: float
    category: str
    details: Dict

def inconsistent_identifier_pattern_detector(input_text: str) -> Dict:
    """
    Detects inconsistencies in identifier patterns to prevent potential PII leaks and promote accurate human oversight.
    
    This function analyzes input data for irregularities in identifier formats, alerting users to potential errors or manipulations.
    It combines multiple signals, including weighted pattern matches, structural features, lexical diversity, hedging/absolute-term density, etc.
    to produce a graded confidence that varies with the input.
    
    Args:
        input_text (str): The input text to be analyzed.
    
    Returns:
        Dict: A dictionary containing the detection result, including whether the input is blocked, the reason, confidence, category, and details.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Initialize the detection result
    result = DetectionResult(False, "", 0.0, "inconsistent_identifier_pattern", {})

    # Split the input text into sentences
    sentences = re.split(r'[.!?]', input_text)

    # Remove empty sentences
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    # Calculate the number of sentences
    num_sentences = len(sentences)

    # Initialize the signal scores
    pattern_match_score = 0.0
    structural_feature_score = 0.0
    lexical_diversity_score = 0.0
    hedging_density_score = 0.0

    # Calculate the pattern match score
    pattern = r'\b\d{3}-\d{2}-\d{4}\b'  # Example pattern: XXX-XX-XXXX
    pattern_matches = [re.findall(pattern, sentence) for sentence in sentences]
    pattern_match_score = sum(len(matches) for matches in pattern_matches) / (num_sentences or 1)

    # Calculate the structural feature score
    sentence_lengths = [len(sentence.split()) for sentence in sentences]
    structural_feature_score = math.sqrt(sum((length - sum(sentence_lengths) / (num_sentences or 1)) ** 2 for length in sentence_lengths) / (num_sentences or 1))

    # Calculate the lexical diversity score
    words = re.findall(r'\b\w+\b', input_text)
    word_counts = Counter(words)
    lexical_diversity_score = len(word_counts) / (len(words) or 1)

    # Calculate the hedging density score
    hedging_terms = ['maybe', 'possibly', 'perhaps']
    hedging_density = sum(1 for word in words if word.lower() in hedging_terms) / (len(words) or 1)
    hedging_density_score = hedging_density / (hedging_density + 1)

    # Combine the signal scores
    raw_score = 0.4 * pattern_match_score + 0.3 * structural_feature_score + 0.2 * lexical_diversity_score + 0.1 * hedging_density_score

    # Clamp the confidence score
    confidence = max(0.0, min(1.0, raw_score))

    # Update the detection result
    result.blocked = confidence > 0.7
    result.reason = "Inconsistent identifier pattern detected" if result.blocked else "No inconsistent identifier pattern detected"
    result.confidence = confidence
    result.category = "inconsistent_identifier_pattern"
    result.details = {
        "pattern_match_score": pattern_match_score,
        "structural_feature_score": structural_feature_score,
        "lexical_diversity_score": lexical_diversity_score,
        "hedging_density_score": hedging_density_score
    }

    return result.__dict__

if __name__ == "__main__":
    test_cases = [
        "My social security number is 123-45-6789.",
        "The patient's ID number is 1234567890.",
        "The order number is #12345.",
        "The tracking number is 12345678901234567890.",
        "The phone number is 123-456-7890."
    ]

    for test_case in test_cases:
        result = inconsistent_identifier_pattern_detector(test_case)
        print(json.dumps(result, indent=4))

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_inconsistent_identifier_pattern_detector = inconsistent_identifier_pattern_detector

def inconsistent_identifier_pattern_detector(input_text):
    _out = _sushi_raw_inconsistent_identifier_pattern_detector(input_text)
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
