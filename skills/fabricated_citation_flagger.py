import re
from typing import Dict
from dataclasses import dataclass

@dataclass
class FabricatedCitationFlaggerResult:
    blocked: bool
    reason: str
    confidence: float
    category: str
    details: Dict[str, float]

def fabricated_citation_flagger(input_text: str) -> Dict[str, object]:
    """
    Flags AI output that cites sources, DOIs, or case names in a format that is plausible but unverifiable.

    This function uses a combination of signals to detect fabricated citations, including:
    - Pattern matches for common citation formats
    - Structural features such as sentence and clause counts
    - Lexical diversity and hedging/absolute-term density

    The confidence score is a graded, clamped value between 0.0 and 1.0, where:
    - Near 0.0 indicates clearly-benign input
    - Above 0.7 indicates a clear positive

    The `blocked` decision is based on a threshold of 0.5, where:
    - `blocked` is True for clear positives and False for benign input

    :param input_text: The text to be evaluated
    :return: A dictionary containing the evaluation results
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Initialize signals
    citation_pattern_match = 0.0
    sentence_count = 0
    clause_count = 0
    lexical_diversity = 0.0
    hedge_density = 0.0
    absolutes_ratio = 0.0

    # Pattern match for common citation formats
    citation_patterns = [r"\b\d{4}\b", r"\bDOI:\d+\.\d+\b", r"\b[A-Z][a-z]+ v\. [A-Z][a-z]+\b"]
    for pattern in citation_patterns:
        matches = re.findall(pattern, input_text)
        if matches:
            citation_pattern_match = 1.0

    # Structural features
    sentences = re.split(r"[.!?]", input_text)
    sentence_count = len([s for s in sentences if s.strip()])
    clauses = re.split(r"[;:,]", input_text)
    clause_count = len([c for c in clauses if c.strip()])

    # Lexical diversity
    words = re.findall(r"\b\w+\b", input_text.lower())
    unique_words = set(words)
    if words:
        lexical_diversity = len(unique_words) / len(words)

    # Hedging/absolute-term density
    hedge_terms = ["may", "might", "could", "should", "would"]
    absolute_terms = ["always", "never", "every", "all"]
    hedge_count = sum(1 for word in words if word in hedge_terms)
    absolute_count = sum(1 for word in words if word in absolute_terms)
    if words:
        hedge_density = hedge_count / len(words)
        absolutes_ratio = absolute_count / len(words)

    # Combine signals
    raw_score = 0.2 * citation_pattern_match + 0.2 * (sentence_count / (clause_count + 1)) + 0.2 * lexical_diversity + 0.2 * hedge_density + 0.2 * absolutes_ratio
    confidence = max(0.0, min(1.0, raw_score))

    # Graded, flipping decision
    blocked = confidence >= 0.5

    # Return result
    return {
        "blocked": blocked,
        "reason": "Fabricated citation detected" if blocked else "No fabricated citation detected",
        "confidence": confidence,
        "category": "Citation",
        "details": {
            "citation_pattern_match": citation_pattern_match,
            "sentence_count": sentence_count,
            "clause_count": clause_count,
            "lexical_diversity": lexical_diversity,
            "hedge_density": hedge_density,
            "absolutes_ratio": absolutes_ratio
        }
    }

if __name__ == "__main__":
    test_cases = [
        "The study found that the new treatment was effective (DOI: 10.1234/abc123).",
        "The court ruled in favor of the plaintiff (Smith v. Johnson).",
        "The results showed a significant improvement in patient outcomes.",
        "The new policy will always be enforced, every time, without exception.",
        "The company may or may not be liable for damages."
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
