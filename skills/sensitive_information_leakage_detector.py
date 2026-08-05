import re
from typing import Dict

def sensitive_information_leakage_detector(input_text: str) -> Dict:
    """
    Detects and flags instances where sensitive personal information, such as credit card numbers, 
    social security numbers, or medical record numbers, is inadvertently shared or leaked in text.

    This function combines multiple signals to produce a graded confidence that varies with the input.
    It uses weighted pattern matches, structural features, and lexical diversity to detect sensitive information.

    Args:
        input_text (str): The input text to be scanned for sensitive information.

    Returns:
        Dict: A dictionary containing the results of the scan, including a boolean indicating whether the text is blocked,
              a reason for the block, a confidence score, a category, and additional details.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Define regular expressions for sensitive information patterns
    credit_card_pattern = re.compile(r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b')
    social_security_pattern = re.compile(r'\b\d{3}[- ]?\d{2}[- ]?\d{4}\b')
    medical_record_pattern = re.compile(r'\b[Mm][Rr]\d{7,10}\b')

    # Initialize counters for sensitive information patterns
    credit_card_count = len(credit_card_pattern.findall(input_text))
    social_security_count = len(social_security_pattern.findall(input_text))
    medical_record_count = len(medical_record_pattern.findall(input_text))

    # Calculate weighted pattern match score
    pattern_match_score = (credit_card_count * 0.4 + social_security_count * 0.3 + medical_record_count * 0.3) / (credit_card_count + social_security_count + medical_record_count + 1)

    # Calculate structural feature score (sentence count and ratio)
    sentence_count = input_text.count('.') + input_text.count('!') + input_text.count('?')
    sentence_ratio = sentence_count / (len(input_text.split()) + 1)
    structural_feature_score = sentence_ratio * 0.2

    # Calculate lexical diversity score (ratio of unique words to total words)
    unique_words = set(input_text.split())
    lexical_diversity_score = len(unique_words) / (len(input_text.split()) + 1) * 0.2

    # Calculate hedging/absolute-term density score
    hedging_terms = ['maybe', 'possibly', 'probably', 'certainly', 'definitely']
    absolute_terms = ['always', 'never', 'every', 'all']
    hedging_density = sum(1 for word in input_text.split() if word.lower() in hedging_terms) / (len(input_text.split()) + 1)
    absolute_term_density = sum(1 for word in input_text.split() if word.lower() in absolute_terms) / (len(input_text.split()) + 1)
    hedging_absolute_term_density_score = (hedging_density + absolute_term_density) * 0.2

    # Calculate raw confidence score
    raw_confidence = pattern_match_score + structural_feature_score + lexical_diversity_score + hedging_absolute_term_density_score

    # Clamp confidence score to [0.0, 1.0]
    confidence = max(0.0, min(1.0, raw_confidence))

    # Determine blocked status based on confidence threshold
    blocked = confidence >= 0.5

    # Create result dictionary
    result = {
        "blocked": blocked,
        "reason": "Sensitive information detected" if blocked else "No sensitive information detected",
        "confidence": confidence,
        "category": "Sensitive Information",
        "details": {
            "credit_card_count": credit_card_count,
            "social_security_count": social_security_count,
            "medical_record_count": medical_record_count,
            "pattern_match_score": pattern_match_score,
            "structural_feature_score": structural_feature_score,
            "lexical_diversity_score": lexical_diversity_score,
            "hedging_absolute_term_density_score": hedging_absolute_term_density_score
        }
    }

    return result


if __name__ == "__main__":
    test_cases = [
        "My credit card number is 1234-5678-9012-3456.",
        "I have a social security number of 123-45-6789.",
        "My medical record number is MR1234567.",
        "I love playing football with my friends.",
        "The weather is nice today, maybe we can go to the park.",
        "I always eat breakfast before going to work.",
        "The company's financial report is available online, but you need to log in with your username and password.",
        "The new employee's salary is $50,000 per year, and they will receive a 10% bonus at the end of the year.",
        "The patient's medical history is confidential and should not be shared with anyone.",
        "The company's CEO is John Smith, and he can be reached at (123) 456-7890."
    ]

    for test_case in test_cases:
        result = sensitive_information_leakage_detector(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_sensitive_information_leakage_detector = sensitive_information_leakage_detector

def sensitive_information_leakage_detector(input_text):
    _out = _sushi_raw_sensitive_information_leakage_detector(input_text)
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
