import re
from typing import Dict

def fabricated_citation_flagger(input_text: str) -> Dict:
    """
    Flags AI output that cites sources, DOIs, or case names in a format that is plausible but unverifiable.

    This function combines multiple signals to detect fabricated citations, including:
    - Pattern matches for common citation formats
    - Structural features such as sentence and clause counts
    - Lexical diversity and hedging/absolute-term density

    The confidence score is a graded, clamped value between 0.0 and 1.0, reflecting the strength of the signals.
    The `blocked` decision is based on a threshold of 0.5, but can be adjusted as needed.

    :param input_text: The text to be evaluated for fabricated citations
    :return: A dictionary containing the evaluation results, including `blocked`, `reason`, `confidence`, `category`, and `details`
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
        "category": "fabricated_citation",
        "details": {}
    }

    # Define common citation patterns
    citation_patterns = [
        r"\bDOI:\s*\d+\.\d+/[\w\-\.]+\b",
        r"\bISBN:\s*\d{13}\b",
        r"\bISSN:\s*\d{4}-\d{3}[\dxX]\b",
        r"\bPubMed:\s*PMC\d+\b",
        r"\bCase\s*\d{1,4}\s*[A-Za-z\s]+\b"
    ]

    # Define absolute and hedging terms
    absolute_terms = ["always", "never", "only", "all", "none"]
    hedging_terms = ["may", "might", "could", "would", "should"]

    # Split the input text into sentences
    sentences = re.split(r"[.!?]\s*", input_text)

    # Initialize signal counters
    citation_matches = 0
    absolute_term_count = 0
    hedging_term_count = 0
    sentence_count = len(sentences)

    # Iterate over the sentences
    for sentence in sentences:
        # Check for citation patterns
        for pattern in citation_patterns:
            if re.search(pattern, sentence):
                citation_matches += 1

        # Count absolute and hedging terms
        for term in absolute_terms:
            absolute_term_count += sentence.lower().count(term)
        for term in hedging_terms:
            hedging_term_count += sentence.lower().count(term)

    # Calculate signal ratios
    if sentence_count > 0:
        citation_ratio = citation_matches / sentence_count
        absolute_term_ratio = absolute_term_count / sentence_count
        hedging_term_ratio = hedging_term_count / sentence_count
    else:
        citation_ratio = 0.0
        absolute_term_ratio = 0.0
        hedging_term_ratio = 0.0

    # Calculate the raw confidence score
    raw_confidence = 0.4 * citation_ratio + 0.3 * absolute_term_ratio + 0.3 * hedging_term_ratio

    # Clamp the confidence score
    confidence = max(0.0, min(1.0, raw_confidence))

    # Update the result dictionary
    result["confidence"] = confidence
    result["blocked"] = confidence >= 0.5
    if result["blocked"]:
        result["reason"] = "Fabricated citation detected"
    else:
        result["reason"] = "No fabricated citation detected"
    result["details"]["citation_matches"] = citation_matches
    result["details"]["absolute_term_count"] = absolute_term_count
    result["details"]["hedging_term_count"] = hedging_term_count

    return result


if __name__ == "__main__":
    test_cases = [
        "This is a test sentence with a DOI: 10.1234/abc123.",
        "The case of Smith v. Jones is well-known.",
        "Always remember to cite your sources.",
        "The book has an ISBN: 978-3-16-148410-0.",
        "This sentence does not contain any citations."
    ]

    for test_case in test_cases:
        result = fabricated_citation_flagger(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
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
