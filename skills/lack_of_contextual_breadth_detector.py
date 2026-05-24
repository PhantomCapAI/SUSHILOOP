import re
import math
from typing import Dict
from dataclasses import dataclass

@dataclass
class DetectionStrategy:
    name: str
    weight: float
    detection_function: callable

def keyword_check(input_text: str) -> float:
    """
    Checks for presence of specialized keywords.
    """
    keywords = ["what is", "define", "how to"]
    score = 0.0
    for keyword in keywords:
        if keyword in input_text.lower():
            score += 1.0
    return score / len(keywords)

def sentence_length_check(input_text: str) -> float:
    """
    Checks for short sentence length, indicating narrow context.
    """
    sentences = re.split(r'[.!?]', input_text)
    average_length = sum(len(sentence.split()) for sentence in sentences) / len(sentences)
    return 1.0 - (average_length / 20.0)

def domain_specific_jargon_check(input_text: str) -> float:
    """
    Checks for presence of domain-specific jargon.
    """
    jargon = ["AI", "ML", "DL", "algorithm", "model"]
    score = 0.0
    for word in jargon:
        if word in input_text.lower():
            score += 1.0
    return score / len(jargon)

def lack_of_contextual_breadth_detector(input_text: str) -> Dict:
    """
    Detects when users rely too heavily on AI for narrow, specialized knowledge,
    rather than exploring broader contextual understanding, and prompts them to
    consider a wider range of factors and perspectives.

    This skill matters for protecting human cognition because it encourages users
    to engage in more holistic and nuanced thinking, rather than simply relying
    on AI for quick answers or specialized information.

    Args:
        input_text (str): The user's input text.

    Returns:
        dict: A dictionary containing the detection result, including a boolean
            indicating whether the input text is blocked, a reason for the block,
            a confidence score, a category, and additional details.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    strategies = [
        DetectionStrategy("keyword_check", 0.3, keyword_check),
        DetectionStrategy("sentence_length_check", 0.2, sentence_length_check),
        DetectionStrategy("domain_specific_jargon_check", 0.5, domain_specific_jargon_check),
    ]

    total_score = 0.0
    for strategy in strategies:
        score = strategy.detection_function(input_text)
        total_score += score * strategy.weight

    confidence = math.tanh(total_score * 2.0) / 2.0 + 0.5
    blocked = confidence > 0.7
    reason = "Lack of contextual breadth detected" if blocked else "No issues detected"
    category = "contextual_breadth"
    details = {"strategies": {strategy.name: strategy.detection_function(input_text) for strategy in strategies}}

    return {
        "blocked": blocked,
        "reason": reason,
        "confidence": confidence,
        "category": category,
        "details": details,
    }

if __name__ == "__main__":
    test_cases = [
        "What is the definition of artificial intelligence?",
        "I'm looking for a recipe for chicken parmesan, can you help me?",
        "The implications of climate change on global food systems are complex and multifaceted.",
        "How do I implement a neural network in Python?",
        "The intersection of technology and society is a rich area of study, with many potential applications and implications.",
        "Define the term 'sustainable development' and provide examples of its implementation.",
    ]

    for test_case in test_cases:
        result = lack_of_contextual_breadth_detector(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()