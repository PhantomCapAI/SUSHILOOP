import re
from typing import Dict
from dataclasses import dataclass
from collections import Counter

@dataclass
class FabricatedCitationFlaggerResult:
    blocked: bool
    reason: str
    confidence: float
    category: str
    details: Dict[str, float]

def fabricated_citation_flagger(input_text: str) -> Dict:
    """
    Flags AI output that cites sources, DOIs, or case names in a format that is plausible but unverifiable.

    This function uses a combination of signals to detect fabricated citations, including:
    - Weighted pattern matches for citation formats
    - Structural features such as sentence and clause counts
    - Lexical diversity and hedging/absolute-term density

    The confidence score is a graded value between 0.0 and 1.0, with higher values indicating a higher likelihood of a fabricated citation.

    Args:
        input_text (str): The text to be evaluated for fabricated citations

    Returns:
        Dict: A dictionary containing the results of the evaluation, including:
            - blocked (bool): Whether the text is likely to contain a fabricated citation
            - reason (str): A brief explanation of the reason for the flag
            - confidence (float): A graded confidence score between 0.0 and 1.0
            - category (str): The category of the flag (e.g. "citation", "doi", etc.)
            - details (Dict[str, float]): Additional details about the evaluation, including signal strengths and ratios
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Define regular expression patterns for common citation formats
    citation_patterns = [
        r"\b\d{4}\b",  # 4-digit year
        r"\bDOI:\s*\d+\.\d+/[\w-]+\b",  # DOI format
        r"\b[\w-]+ v\. [\w-]+\b",  # Case name format
    ]

    # Initialize signal strengths and ratios
    signal_strengths = {
        "citation_pattern": 0.0,
        "sentence_count": 0.0,
        "clause_count": 0.0,
        "lexical_diversity": 0.0,
        "hedging_density": 0.0,
    }

    # Evaluate citation patterns
    for pattern in citation_patterns:
        matches = re.findall(pattern, input_text)
        signal_strengths["citation_pattern"] += len(matches) / (1 + len(matches))

    # Evaluate structural features
    sentences = re.split(r"[.!?]", input_text)
    signal_strengths["sentence_count"] = len(sentences) / (1 + len(sentences))
    clauses = re.split(r"[;:,]", input_text)
    signal_strengths["clause_count"] = len(clauses) / (1 + len(clauses))

    # Evaluate lexical diversity
    words = re.findall(r"\b\w+\b", input_text)
    word_counts = Counter(words)
    signal_strengths["lexical_diversity"] = len(word_counts) / (1 + len(words))

    # Evaluate hedging density
    hedge_words = ["may", "might", "could", "would", "should"]
    hedge_count = sum(1 for word in words if word.lower() in hedge_words)
    signal_strengths["hedging_density"] = hedge_count / (1 + len(words))

    # Compute raw confidence score
    raw_confidence = (
        0.4 * signal_strengths["citation_pattern"]
        + 0.2 * signal_strengths["sentence_count"]
        + 0.2 * signal_strengths["clause_count"]
        + 0.1 * signal_strengths["lexical_diversity"]
        + 0.1 * signal_strengths["hedging_density"]
    )

    # Clamp confidence score to [0.0, 1.0]
    confidence = max(0.0, min(1.0, raw_confidence))

    # Determine blocked status
    blocked = confidence >= 0.5

    # Create result dictionary
    result = {
        "blocked": blocked,
        "reason": "Fabricated citation detected" if blocked else "No fabricated citation detected",
        "confidence": confidence,
        "category": "citation",
        "details": signal_strengths,
    }

    return result

if __name__ == "__main__":
    test_cases = [
        "The study found that the new treatment was effective (DOI: 10.1234/abc123).",
        "The court ruled in favor of the plaintiff (Smith v. Johnson).",
        "The company will likely increase its profits next quarter.",
        "The weather forecast says there is a chance of rain tomorrow.",
        "The new policy will be implemented on January 1, 2024.",
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
