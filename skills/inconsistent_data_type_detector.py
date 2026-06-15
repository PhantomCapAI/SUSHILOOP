import re
import math
from typing import Dict
from dataclasses import dataclass

@dataclass
class DetectionResult:
    blocked: bool
    reason: str
    confidence: float
    category: str
    details: Dict[str, str]

def inconsistent_data_type_detector(input_text: str) -> Dict[str, str]:
    """
    Detects when personally identifiable information (PII) is provided in an inconsistent data type format.

    This function combines multiple signals to detect inconsistent data types in PII, 
    including weighted pattern matches, structural features, lexical diversity, 
    hedging/absolute-term density, etc. It returns a dictionary with the detection result, 
    including a graded confidence score that varies with the input.

    Args:
        input_text (str): The input text to be analyzed.

    Returns:
        Dict[str, str]: A dictionary containing the detection result, including:
            - blocked (bool): Whether the input text is blocked due to inconsistent data type.
            - reason (str): The reason for blocking the input text.
            - confidence (float): A graded confidence score between 0.0 and 1.0.
            - category (str): The category of the detection result.
            - details (Dict[str, str]): Additional details about the detection result.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Initialize the detection result
    result = DetectionResult(False, "", 0.0, "inconsistent_data_type", {})

    # Split the input text into sentences
    sentences = re.split(r'[.!?]', input_text)

    # Remove empty sentences
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    # Calculate the sentence count
    sentence_count = len(sentences)

    # Calculate the word count
    word_count = sum(len(sentence.split()) for sentence in sentences)

    # Calculate the lexical diversity
    lexical_diversity = len(set(word.lower() for sentence in sentences for word in sentence.split())) / word_count if word_count > 0 else 0.0

    # Calculate the hedging/absolute-term density
    hedging_terms = ["maybe", "possibly", "perhaps", "always", "never"]
    absolute_terms = ["all", "every", "each", "any"]
    hedging_density = sum(1 for sentence in sentences for word in sentence.split() if word.lower() in hedging_terms) / word_count if word_count > 0 else 0.0
    absolute_density = sum(1 for sentence in sentences for word in sentence.split() if word.lower() in absolute_terms) / word_count if word_count > 0 else 0.0

    # Calculate the weighted pattern matches
    pattern_matches = [
        (r"\b\d{3}-\d{3}-\d{4}\b", 0.5),  # phone number pattern
        (r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", 0.3),  # date pattern
        (r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", 0.2)  # IP address pattern
    ]
    pattern_match_count = sum(1 for sentence in sentences for pattern, _ in pattern_matches if re.search(pattern, sentence))
    pattern_match_ratio = pattern_match_count / sentence_count if sentence_count > 0 else 0.0

    # Calculate the raw confidence score
    raw_confidence = 0.4 * pattern_match_ratio + 0.3 * hedging_density + 0.2 * absolute_density + 0.1 * lexical_diversity

    # Clamp the confidence score to [0.0, 1.0]
    confidence = max(0.0, min(1.0, raw_confidence))

    # Update the detection result
    result.blocked = confidence > 0.5
    result.reason = "Inconsistent data type detected" if result.blocked else "No inconsistent data type detected"
    result.confidence = confidence
    result.details = {
        "sentence_count": str(sentence_count),
        "word_count": str(word_count),
        "lexical_diversity": str(lexical_diversity),
        "hedging_density": str(hedging_density),
        "absolute_density": str(absolute_density),
        "pattern_match_ratio": str(pattern_match_ratio)
    }

    # Return the detection result as a dictionary
    return {
        "blocked": str(result.blocked),
        "reason": result.reason,
        "confidence": str(result.confidence),
        "category": result.category,
        "details": result.details
    }

if __name__ == "__main__":
    test_cases = [
        "My phone number is 123-456-7890.",
        "I was born on 01/01/1990.",
        "The IP address is 192.168.1.1.",
        "Maybe I will go to the store.",
        "I always go to the store.",
        "The date is 2022-01-01.",
        "The phone number is 1234567890.",
        "The IP address is 192.168.1",
        "I go to the store every day.",
        "The date is 01/01/1990 and the time is 12:00 PM."
    ]

    for test_case in test_cases:
        print(inconsistent_data_type_detector(test_case))

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_inconsistent_data_type_detector = inconsistent_data_type_detector

def inconsistent_data_type_detector(input_text):
    _out = _sushi_raw_inconsistent_data_type_detector(input_text)
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
