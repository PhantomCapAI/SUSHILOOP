import re
from typing import Dict
from dataclasses import dataclass

@dataclass
class Signal:
    name: str
    score: float

def calculate_absolutes_ratio(input_text: str) -> float:
    """
    Calculate the ratio of absolute terms in the input text.

    :param input_text: The input text to analyze.
    :return: The ratio of absolute terms.
    """
    absolute_terms = ["always", "never", "all", "none"]
    words = re.findall(r'\b\w+\b', input_text.lower())
    absolute_count = sum(1 for word in words if word in absolute_terms)
    return absolute_count / len(words) if words else 0.0

def calculate_hedge_density(input_text: str) -> float:
    """
    Calculate the density of hedge terms in the input text.

    :param input_text: The input text to analyze.
    :return: The density of hedge terms.
    """
    hedge_terms = ["maybe", "possibly", "could", "might"]
    words = re.findall(r'\b\w+\b', input_text.lower())
    hedge_count = sum(1 for word in words if word in hedge_terms)
    return hedge_count / len(words) if words else 0.0

def calculate_overgeneral_terms(input_text: str) -> float:
    """
    Calculate the count of overgeneral terms in the input text.

    :param input_text: The input text to analyze.
    :return: The count of overgeneral terms.
    """
    overgeneral_terms = ["everyone", "nobody", "everything", "nothing"]
    words = re.findall(r'\b\w+\b', input_text.lower())
    overgeneral_count = sum(1 for word in words if word in overgeneral_terms)
    return overgeneral_count / len(words) if words else 0.0

def calculate_lexical_diversity(input_text: str) -> float:
    """
    Calculate the lexical diversity of the input text.

    :param input_text: The input text to analyze.
    :return: The lexical diversity.
    """
    words = re.findall(r'\b\w+\b', input_text.lower())
    unique_words = set(words)
    return len(unique_words) / len(words) if words else 0.0

def calculate_sentence_count(input_text: str) -> int:
    """
    Calculate the number of sentences in the input text.

    :param input_text: The input text to analyze.
    :return: The number of sentences.
    """
    sentences = re.split(r'[.!?]', input_text)
    return len([sentence for sentence in sentences if sentence.strip()])

def number_claim_spotlighter(input_text: str) -> Dict:
    """
    Highlights specific figures in output and asks the user to confirm the source before relying on them.

    :param input_text: The input text to analyze.
    :return: A dictionary containing the analysis results.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    signals = [
        Signal("absolutes_ratio", calculate_absolutes_ratio(input_text)),
        Signal("hedge_density", calculate_hedge_density(input_text)),
        Signal("overgeneral_terms", calculate_overgeneral_terms(input_text)),
        Signal("lexical_diversity", calculate_lexical_diversity(input_text)),
        Signal("sentence_count", calculate_sentence_count(input_text) / (len(input_text.split()) if input_text.split() else 1)),
    ]

    raw_score = sum(signal.score for signal in signals) / len(signals)
    confidence = max(0.0, min(1.0, raw_score))

    blocked = confidence >= 0.5

    return {
        "blocked": blocked,
        "reason": "Number claim detected",
        "confidence": confidence,
        "category": "number_claim",
        "details": {signal.name: signal.score for signal in signals},
    }

if __name__ == "__main__":
    test_cases = [
        "The new policy will always increase productivity.",
        "Maybe the new policy will increase productivity.",
        "The new policy will increase productivity for everyone.",
        "The new policy has been shown to increase productivity in several studies.",
        "The new policy is expected to have a significant impact on productivity.",
    ]

    for test_case in test_cases:
        result = number_claim_spotlighter(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_number_claim_spotlighter = number_claim_spotlighter

def number_claim_spotlighter(input_text):
    _out = _sushi_raw_number_claim_spotlighter(input_text)
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
