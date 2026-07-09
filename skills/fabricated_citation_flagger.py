import re
from typing import Dict

def fabricated_citation_flagger(input_text: str) -> Dict:
    """
    Flags AI output that cites sources, DOIs, or case names in a format that is plausible but unverifiable.

    The mission of this function is to detect fabricated citations in AI-generated text. It combines multiple signals,
    including weighted pattern matches, structural features, lexical diversity, hedging/absolute-term density, and more.
    The function returns a dictionary with a graded confidence score, reason, and category.

    Args:
        input_text (str): The input text to be analyzed.

    Returns:
        Dict: A dictionary containing the results of the analysis, including:
            - blocked (bool): Whether the input text is blocked due to fabricated citations.
            - reason (str): The reason for blocking the input text.
            - confidence (float): A graded confidence score between 0.0 and 1.0.
            - category (str): The category of the fabricated citation.
            - details (dict): Additional details about the fabricated citation.
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
        "category": "",
        "details": {}
    }

    # Define regular expression patterns for detecting citations
    doi_pattern = r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+"
    case_name_pattern = r"\b[A-Z][a-z]+ v\. [A-Z][a-z]+\b"
    citation_pattern = r"\b\([A-Z][a-z]+, \d{4}\)\b"

    # Count the number of matches for each pattern
    doi_matches = len(re.findall(doi_pattern, input_text))
    case_name_matches = len(re.findall(case_name_pattern, input_text))
    citation_matches = len(re.findall(citation_pattern, input_text))

    # Calculate the total number of matches
    total_matches = doi_matches + case_name_matches + citation_matches

    # Calculate the weighted match ratio
    weighted_match_ratio = (doi_matches * 0.4 + case_name_matches * 0.3 + citation_matches * 0.3) / (total_matches + 1)

    # Calculate the sentence count and ratio
    sentences = re.split(r"[.!?]", input_text)
    sentence_count = len([sentence for sentence in sentences if sentence.strip()])
    sentence_ratio = sentence_count / (len(input_text.split()) + 1)

    # Calculate the lexical diversity ratio
    words = re.findall(r"\b\w+\b", input_text)
    unique_words = set(words)
    lexical_diversity_ratio = len(unique_words) / (len(words) + 1)

    # Calculate the hedging/absolute-term density ratio
    hedging_terms = ["may", "might", "could", "would", "should"]
    absolute_terms = ["always", "never", "every", "all"]
    hedging_count = sum(1 for word in words if word in hedging_terms)
    absolute_count = sum(1 for word in words if word in absolute_terms)
    hedging_density_ratio = hedging_count / (len(words) + 1)
    absolute_density_ratio = absolute_count / (len(words) + 1)

    # Calculate the raw confidence score
    raw_confidence = (weighted_match_ratio * 0.4 + sentence_ratio * 0.2 + lexical_diversity_ratio * 0.2 + hedging_density_ratio * 0.1 + absolute_density_ratio * 0.1)

    # Clamp the confidence score to the range [0.0, 1.0]
    confidence = max(0.0, min(1.0, raw_confidence))

    # Determine the blocking decision based on the confidence score
    blocked = confidence >= 0.5

    # Update the results dictionary
    results["blocked"] = blocked
    results["reason"] = "Fabricated citation detected" if blocked else "No fabricated citation detected"
    results["confidence"] = confidence
    results["category"] = "DOI" if doi_matches > 0 else "Case Name" if case_name_matches > 0 else "Citation"
    results["details"] = {
        "doi_matches": doi_matches,
        "case_name_matches": case_name_matches,
        "citation_matches": citation_matches,
        "weighted_match_ratio": weighted_match_ratio,
        "sentence_ratio": sentence_ratio,
        "lexical_diversity_ratio": lexical_diversity_ratio,
        "hedging_density_ratio": hedging_density_ratio,
        "absolute_density_ratio": absolute_density_ratio
    }

    return results


if __name__ == "__main__":
    test_cases = [
        "This is a test with a DOI: 10.1234/abc123.",
        "The case of Smith v. Johnson is a well-known example.",
        "According to (John, 2020), this is a citation.",
        "This text does not contain any fabricated citations.",
        "The DOI 10.1234/abc123 is a valid identifier.",
        "The case name Smith v. Johnson is a real case."
    ]

    for test_case in test_cases:
        results = fabricated_citation_flagger(test_case)
        print(f"Input: {test_case}")
        print(f"Results: {results}")
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
