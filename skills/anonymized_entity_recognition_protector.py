import re
from typing import Dict

def anonymized_entity_recognition_protector(input_text: str) -> Dict:
    """
    This function detects and flags instances where anonymized entities, 
    such as '[NAME REDACTED]' or '[EMAIL REMOVED]', are inadvertently replaced 
    with actual personally identifiable information, thus protecting sensitive data 
    and promoting responsible AI usage.

    Args:
    input_text (str): The text to be analyzed for potential PII leaks.

    Returns:
    Dict: A dictionary containing the results of the analysis, including a boolean 
    indicating whether the text is blocked, a reason for the block, a confidence 
    score, a category, and additional details.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Initialize the result dictionary
    result = {
        "blocked": False,
        "reason": "",
        "confidence": 0.0,
        "category": "",
        "details": {}
    }

    # Define regular expressions for common PII patterns
    pii_patterns = [
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
        r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # Phone number
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",  # Date
        r"\b\d{3}[-.]?\d{2}[-.]?\d{4}\b",  # SSN
        r"\b[A-Za-z]{1,20}\b"  # Name
    ]

    # Define regular expressions for anonymized entity patterns
    anonymized_patterns = [
        r"\[NAME REDACTED\]",
        r"\[EMAIL REMOVED\]",
        r"\[PHONE NUMBER REDACTED\]",
        r"\[DATE REDACTED\]",
        r"\[SSN REDACTED\]"
    ]

    # Initialize counters for PII and anonymized entity patterns
    pii_count = 0
    anonymized_count = 0

    # Iterate over the PII patterns and count matches
    for pattern in pii_patterns:
        matches = re.findall(pattern, input_text)
        pii_count += len(matches)

    # Iterate over the anonymized entity patterns and count matches
    for pattern in anonymized_patterns:
        matches = re.findall(pattern, input_text)
        anonymized_count += len(matches)

    # Calculate the ratio of PII to anonymized entity patterns
    if anonymized_count == 0:
        pii_ratio = 0.0
    else:
        pii_ratio = pii_count / anonymized_count

    # Calculate the confidence score based on the PII ratio
    raw_score = 0.5 * pii_ratio + 0.3 * (1 - pii_ratio) + 0.2 * (pii_count > 0)
    confidence = max(0.0, min(1.0, raw_score))

    # Update the result dictionary
    result["confidence"] = confidence
    result["blocked"] = confidence >= 0.5
    result["reason"] = "Potential PII leak detected" if result["blocked"] else "No PII leak detected"
    result["category"] = "PII protection"
    result["details"] = {
        "pii_count": pii_count,
        "anonymized_count": anonymized_count,
        "pii_ratio": pii_ratio
    }

    return result


if __name__ == "__main__":
    test_cases = [
        "My name is [NAME REDACTED] and my email is [EMAIL REMOVED].",
        "My name is John Doe and my email is johndoe@example.com.",
        "My phone number is 123-456-7890 and my date of birth is 01/01/1990.",
        "My SSN is 123-45-6789 and my address is 123 Main St.",
        "This is a benign text with no PII."
    ]

    for test_case in test_cases:
        result = anonymized_entity_recognition_protector(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_anonymized_entity_recognition_protector = anonymized_entity_recognition_protector

def anonymized_entity_recognition_protector(input_text):
    _out = _sushi_raw_anonymized_entity_recognition_protector(input_text)
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
