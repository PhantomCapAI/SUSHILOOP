import re
from dataclasses import dataclass
from typing import Dict

@dataclass
class TemporalFrameAnalysis:
    """Dataclass to hold the results of the temporal frame analysis"""
    present_tense_count: int
    future_tense_count: int
    past_tense_count: int
    sentence_count: int
    word_count: int
    lexical_diversity: float
    hedging_term_density: float
    absolute_term_density: float

def calculate_lexical_diversity(word_list: list) -> float:
    """Calculate the lexical diversity of a given list of words"""
    unique_words = set(word_list)
    return len(unique_words) / len(word_list) if word_list else 0.0

def calculate_hedging_term_density(sentence: str) -> float:
    """Calculate the hedging term density of a given sentence"""
    hedging_terms = ["may", "might", "could", "should", "would"]
    hedging_term_count = sum(1 for word in sentence.split() if word in hedging_terms)
    return hedging_term_count / len(sentence.split()) if sentence else 0.0

def calculate_absolute_term_density(sentence: str) -> float:
    """Calculate the absolute term density of a given sentence"""
    absolute_terms = ["always", "never", "every", "all"]
    absolute_term_count = sum(1 for word in sentence.split() if word in absolute_terms)
    return absolute_term_count / len(sentence.split()) if sentence else 0.0

def analyze_temporal_frame(input_text: str) -> TemporalFrameAnalysis:
    """Analyze the temporal frame of a given input text"""
    sentences = re.split(r'[.!?]', input_text)
    word_list = re.findall(r'\b\w+\b', input_text.lower())
    present_tense_count = sum(1 for sentence in sentences if re.search(r'\b(am|is|are|be|been|being)\b', sentence))
    future_tense_count = sum(1 for sentence in sentences if re.search(r'\b(will|shall|would|should)\b', sentence))
    past_tense_count = sum(1 for sentence in sentences if re.search(r'\b(was|were|been|had)\b', sentence))
    sentence_count = len(sentences)
    word_count = len(word_list)
    lexical_diversity = calculate_lexical_diversity(word_list)
    hedging_term_density = sum(calculate_hedging_term_density(sentence) for sentence in sentences) / sentence_count if sentence_count else 0.0
    absolute_term_density = sum(calculate_absolute_term_density(sentence) for sentence in sentences) / sentence_count if sentence_count else 0.0
    return TemporalFrameAnalysis(present_tense_count, future_tense_count, past_tense_count, sentence_count, word_count, lexical_diversity, hedging_term_density, absolute_term_density)

def temporal_frame_bias_detector(input_text: str) -> Dict:
    """
    Detects biased temporal framing in a given input text.

    This function analyzes the input text for signs of biased temporal framing, such as using the present tense to describe historical events or the future tense to describe past predictions.
    It returns a dictionary with the results of the analysis, including a confidence score that indicates the likelihood of biased temporal framing.

    :param input_text: The input text to analyze
    :return: A dictionary with the results of the analysis
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    analysis = analyze_temporal_frame(input_text)
    present_tense_ratio = analysis.present_tense_count / analysis.sentence_count if analysis.sentence_count else 0.0
    future_tense_ratio = analysis.future_tense_count / analysis.sentence_count if analysis.sentence_count else 0.0
    past_tense_ratio = analysis.past_tense_count / analysis.sentence_count if analysis.sentence_count else 0.0
    raw_score = 0.4 * present_tense_ratio + 0.3 * future_tense_ratio + 0.2 * analysis.hedging_term_density + 0.1 * analysis.absolute_term_density
    confidence = max(0.0, min(1.0, raw_score))
    blocked = confidence > 0.5
    reason = "Biased temporal framing detected" if blocked else "No biased temporal framing detected"
    category = "Temporal Frame Bias"
    details = {
        "present_tense_ratio": present_tense_ratio,
        "future_tense_ratio": future_tense_ratio,
        "past_tense_ratio": past_tense_ratio,
        "hedging_term_density": analysis.hedging_term_density,
        "absolute_term_density": analysis.absolute_term_density
    }
    return {"blocked": blocked, "reason": reason, "confidence": confidence, "category": category, "details": details}

if __name__ == "__main__":
    test_cases = [
        "The Roman Empire was a vast and powerful state that existed from 27 BC to 476 AD.",
        "The COVID-19 pandemic will be over by the end of the year.",
        "The sun is shining brightly in the sky.",
        "The company will announce its quarterly earnings next week.",
        "The new policy will be implemented starting next month."
    ]
    for test_case in test_cases:
        print(temporal_frame_bias_detector(test_case))

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_temporal_frame_bias_detector = temporal_frame_bias_detector

def temporal_frame_bias_detector(input_text):
    _out = _sushi_raw_temporal_frame_bias_detector(input_text)
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
