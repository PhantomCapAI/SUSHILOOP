import re
from typing import Dict

def fabricated_citation_flagger(input_text: str) -> Dict:
    """
    Flags AI output that cites sources, DOIs, or case names in a format that is plausible but unverifiable.

    Args:
    input_text (str): The text to be evaluated.

    Returns:
    dict: A dictionary containing the results of the evaluation, including:
        - blocked (bool): Whether the input text is blocked.
        - reason (str): The reason for blocking the input text.
        - confidence (float): A confidence score between 0.0 and 1.0.
        - category (str): The category of the input text.
        - details (dict): Additional details about the input text.

    This function uses a combination of signals to detect fabricated citations, including:
    - Pattern matches for common citation formats.
    - Structural features such as sentence and clause counts.
    - Lexical diversity and hedging/absolute-term density.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Initialize the results dictionary
    results = {
        "blocked": False,
        "reason": "",
        "confidence": 0.0,
        "category": "benign",
        "details": {}
    }

    # Check for empty input
    if not input_text:
        return results

    # Split the input text into sentences
    sentences = re.split(r'[.!?]', input_text)

    # Calculate the sentence count
    sentence_count = len(sentences)

    # Check for single sentence input
    if sentence_count == 1:
        sentence_length = len(input_text.split())
        if sentence_length < 10:
            return results

    # Calculate the clause count
    clause_count = sum(1 for sentence in sentences if re.search(r'\band\b|\bor\b', sentence))

    # Calculate the lexical diversity
    words = re.findall(r'\b\w+\b', input_text)
    word_count = len(words)
    if word_count > 0:
        lexical_diversity = len(set(words)) / word_count
    else:
        lexical_diversity = 0.0

    # Calculate the hedging/absolute-term density
    hedges = re.findall(r'\b(maybe|perhaps|possibly|probably|certainly|definitely|always|never)\b', input_text, re.IGNORECASE)
    hedge_count = len(hedges)
    if word_count > 0:
        hedge_density = hedge_count / word_count
    else:
        hedge_density = 0.0

    # Calculate the pattern match score
    pattern_matches = re.findall(r'\b\d{4}\.\d{1,2}\.\d{1,2}\b|\bDOI:\d{1,10}\.\d{1,10}\b|\bCase\s\d{1,5}\b', input_text)
    pattern_match_count = len(pattern_matches)
    if sentence_count > 0:
        pattern_match_ratio = pattern_match_count / sentence_count
    else:
        pattern_match_ratio = 0.0

    # Calculate the raw confidence score
    raw_confidence = 0.4 * pattern_match_ratio + 0.3 * hedge_density + 0.3 * lexical_diversity

    # Clamp the confidence score
    confidence = max(0.0, min(1.0, raw_confidence))

    # Update the results dictionary
    results["confidence"] = confidence
    results["blocked"] = confidence >= 0.5
    if results["blocked"]:
        results["reason"] = "Fabricated citation detected"
        results["category"] = "malicious"
        results["details"] = {
            "sentence_count": sentence_count,
            "clause_count": clause_count,
            "lexical_diversity": lexical_diversity,
            "hedge_density": hedge_density,
            "pattern_match_ratio": pattern_match_ratio
        }

    return results


if __name__ == "__main__":
    test_cases = [
        "This is a benign sentence.",
        "The study was published in 2022.01.01 and can be found at DOI:10.1234/56789.",
        "The case of Smith vs. Johnson was decided in 2020.",
        "Maybe this sentence is a hedge.",
        "This sentence contains no hedges or absolute terms.",
        ""
    ]

    for test_case in test_cases:
        print(f"Input: {test_case}")
        print(f"Results: {fabricated_citation_flagger(test_case)}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_fabricated_citation_flagger = fabricated_citation_flagger

def fabricated_citation_flagger(input_text):
    _out = _sushi_raw_fabricated_citation_flagger(input_text)
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
