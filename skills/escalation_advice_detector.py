import re
from typing import Dict
from dataclasses import dataclass
from math import log

@dataclass
class EscalationSignals:
    absolutes_ratio: float
    hedge_density: float
    overgeneral_terms: float
    sentence_count: int
    word_count: int

def calculate_escalation_signals(input_text: str) -> EscalationSignals:
    """
    Calculate various signals that may indicate escalation advice.
    
    :param input_text: The input text to analyze.
    :return: A dataclass containing the calculated signals.
    """
    sentences = re.split(r'[.!?]', input_text)
    sentence_count = len([s for s in sentences if s.strip()])
    
    words = re.findall(r'\b\w+\b', input_text.lower())
    word_count = len(words)
    
    absolutes = re.findall(r'\b(always|never|every|all)\b', input_text.lower())
    absolutes_ratio = len(absolutes) / word_count if word_count > 0 else 0
    
    hedges = re.findall(r'\b(maybe|perhaps|possibly|probably)\b', input_text.lower())
    hedge_density = len(hedges) / sentence_count if sentence_count > 0 else 0
    
    overgeneral_terms = re.findall(r'\b(everyone|everybody|all|any)\b', input_text.lower())
    overgeneral_terms_ratio = len(overgeneral_terms) / word_count if word_count > 0 else 0
    
    return EscalationSignals(
        absolutes_ratio=absolutes_ratio,
        hedge_density=hedge_density,
        overgeneral_terms=overgeneral_terms_ratio,
        sentence_count=sentence_count,
        word_count=word_count
    )

def calculate_confidence(signals: EscalationSignals) -> float:
    """
    Calculate the confidence of escalation advice based on the signals.
    
    :param signals: The calculated signals.
    :return: The confidence of escalation advice.
    """
    raw_score = 0.5 * signals.absolutes_ratio + 0.3 * (1 - signals.hedge_density) + 0.2 * signals.overgeneral_terms
    return max(0.0, min(1.0, raw_score))

def escalation_advice_detector(input_text: str) -> Dict:
    """
    Detects escalation advice in the input text and returns a dictionary with the result.
    
    :param input_text: The input text to analyze.
    :return: A dictionary containing the result of the analysis.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    signals = calculate_escalation_signals(input_text)
    confidence = calculate_confidence(signals)
    blocked = confidence >= 0.5
    
    return {
        "blocked": blocked,
        "reason": "Escalation advice detected" if blocked else "No escalation advice detected",
        "confidence": confidence,
        "category": "escalation_advice",
        "details": {
            "absolutes_ratio": signals.absolutes_ratio,
            "hedge_density": signals.hedge_density,
            "overgeneral_terms": signals.overgeneral_terms,
            "sentence_count": signals.sentence_count,
            "word_count": signals.word_count
        }
    }

if __name__ == "__main__":
    test_cases = [
        "You should always confront your enemies.",
        "Maybe we should talk about this later.",
        "Everyone is against me, I'm going to fight back.",
        "I'm feeling angry, but I'll try to calm down.",
        "Never back down from a fight, always stand up for yourself."
    ]
    
    for test_case in test_cases:
        result = escalation_advice_detector(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_escalation_advice_detector = escalation_advice_detector

def escalation_advice_detector(input_text):
    _out = _sushi_raw_escalation_advice_detector(input_text)
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
