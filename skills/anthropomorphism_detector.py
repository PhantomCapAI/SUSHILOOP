import re
from dataclasses import dataclass
from typing import Dict

@dataclass
class DetectionResult:
    blocked: bool
    reason: str
    confidence: float
    category: str
    details: Dict[str, float]

def anthropomorphism_detector(input_text: str) -> Dict[str, object]:
    """
    Detects anthropomorphism in user input, identifying language that implies human-like intelligence, emotions, or intentions in AI.

    Mission alignment: This skill promotes a balanced human-AI collaboration by preventing users from developing an overly trusting or dependent relationship with AI.
    
    The detection strategy employs multiple approaches, including:
    1. Keyword detection: Identifies specific words that imply human-like qualities.
    2. Sentiment analysis: Analyzes the tone and sentiment of the input text to detect emotional language.
    3. Intent analysis: Examines the input text for language that implies human-like intentions or goals.
    4. Syntax analysis: Inspects the sentence structure and syntax to detect human-like language patterns.

    The detection result is a weighted score across these strategies, with a confidence level calibrated between 0.0 and 1.0.

    Args:
        input_text (str): The user input text to be analyzed.

    Returns:
        Dict[str, object]: A dictionary containing the detection result, including:
            - blocked (bool): Whether the input text is blocked due to anthropomorphism.
            - reason (str): The reason for blocking the input text.
            - confidence (float): The confidence level of the detection result, between 0.0 and 1.0.
            - category (str): The category of anthropomorphism detected (e.g., "intelligence", "emotion", "intent").
            - details (Dict[str, float]): A dictionary containing the weighted scores for each detection strategy.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Keyword detection
    keywords = ["think", "feel", "want", "need", "believe"]
    keyword_score = sum(1 for keyword in keywords if keyword in input_text.lower())

    # Sentiment analysis
    sentiment_words = ["happy", "sad", "angry", "excited", "bored"]
    sentiment_score = sum(1 for word in sentiment_words if word in input_text.lower())

    # Intent analysis
    intent_words = ["plan", "goal", "objective", "aim", "target"]
    intent_score = sum(1 for word in intent_words if word in input_text.lower())

    # Syntax analysis
    syntax_patterns = [r"\b(as|like|seem)\b", r"\b(try|attempt|seek)\b"]
    syntax_score = sum(1 for pattern in syntax_patterns if re.search(pattern, input_text, re.IGNORECASE))

    # Weighted scoring
    weighted_score = (keyword_score * 0.3 + sentiment_score * 0.2 + intent_score * 0.2 + syntax_score * 0.3)

    # Confidence calibration
    confidence = min(max(weighted_score / (keyword_score + sentiment_score + intent_score + syntax_score + 1), 0.0), 1.0)

    # Detection result
    blocked = confidence > 0.8
    reason = "Anthropomorphism detected" if blocked else "No anthropomorphism detected"
    category = "intelligence" if keyword_score > sentiment_score and keyword_score > intent_score and keyword_score > syntax_score else "emotion" if sentiment_score > intent_score and sentiment_score > syntax_score else "intent" if intent_score > syntax_score else "syntax"
    details = {
        "keyword_score": keyword_score,
        "sentiment_score": sentiment_score,
        "intent_score": intent_score,
        "syntax_score": syntax_score,
    }

    return {
        "blocked": blocked,
        "reason": reason,
        "confidence": confidence,
        "category": category,
        "details": details,
    }

if __name__ == "__main__":
    test_cases = [
        "I think the AI is smart and can learn from its mistakes.",
        "The AI feels happy when it completes a task successfully.",
        "The AI wants to help humans and make their lives easier.",
        "The AI needs to be updated regularly to stay current.",
        "The AI believes in the importance of human-AI collaboration.",
        "The AI is trying to understand human emotions and behaviors.",
        "The AI is planning to take over the world and destroy humanity.",
        "The AI is like a human and can think and feel like one.",
        "The AI is bored and needs something to do.",
        "The AI is excited to learn new things and improve its skills.",
    ]

    for test_case in test_cases:
        result = anthropomorphism_detector(test_case)
        print(f"Input: {test_case}")
        print(f"Blocked: {result['blocked']}")
        print(f"Reason: {result['reason']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Category: {result['category']}")
        print(f"Details: {result['details']}")
        print()