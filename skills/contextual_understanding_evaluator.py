import re
import json
import math
from typing import Dict
from dataclasses import dataclass

@dataclass
class DetectionStrategy:
    name: str
    weight: float
    score: float = 0.0

def contextual_understanding_evaluator(input_text: str) -> Dict:
    """
    Evaluates the context of AI-generated responses to ensure they align with the original prompt.

    This function uses multiple detection strategies to assess the contextual relevance of the input text.
    It returns a dictionary with the evaluation results, including a boolean indicating whether the response is blocked,
    a reason for the blockage, a confidence score, a category, and additional details.

    The mission of this function is to promote human understanding and critical thinking by ensuring AI-generated responses
    are contextually relevant, thereby protecting human cognition from potentially misleading or incomplete information.

    :param input_text: The AI-generated response to be evaluated
    :return: A dictionary with the evaluation results
    """
    # SUSHILOOP input guard (added in hardening pass): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Initialize detection strategies
    strategies = [
        DetectionStrategy("Keyword Check", 0.2),
        DetectionStrategy("Entity Recognition", 0.3),
        DetectionStrategy("Sentiment Analysis", 0.2),
        DetectionStrategy("Topic Modeling", 0.3)
    ]

    # Initialize evaluation results
    blocked = False
    reason = ""
    confidence = 0.0
    category = ""
    details = {}

    # Keyword Check
    keyword_pattern = re.compile(r"\b(context|understanding|critical thinking)\b")
    if not keyword_pattern.search(input_text):
        strategies[0].score = 0.0
    else:
        strategies[0].score = 1.0

    # Entity Recognition
    entity_pattern = re.compile(r"\b([A-Z][a-z]+)\b")
    entities = entity_pattern.findall(input_text)
    if len(entities) < 2:
        strategies[1].score = 0.0
    else:
        strategies[1].score = 1.0

    # Sentiment Analysis
    sentiment_pattern = re.compile(r"\b(positive|negative|neutral)\b")
    sentiment = sentiment_pattern.search(input_text)
    if sentiment and sentiment.group(0) == "negative":
        strategies[2].score = 0.0
    elif sentiment and sentiment.group(0) == "positive":
        strategies[2].score = 1.0
    else:
        strategies[2].score = 0.5

    # Topic Modeling
    topic_pattern = re.compile(r"\b(topic|model|context)\b")
    if not topic_pattern.search(input_text):
        strategies[3].score = 0.0
    else:
        strategies[3].score = 1.0

    # Calculate weighted score
    weighted_score = sum(strategy.score * strategy.weight for strategy in strategies)

    # Normalize weighted score to confidence score
    confidence = weighted_score / sum(strategy.weight for strategy in strategies)

    # Determine blockage and reason
    if confidence < 0.5:
        blocked = True
        reason = "Low confidence in contextual relevance"
        category = "Contextual Irrelevance"
    else:
        blocked = False
        reason = "High confidence in contextual relevance"
        category = "Contextual Relevance"

    # Create details dictionary
    details = {strategy.name: strategy.score for strategy in strategies}

    # Return evaluation results
    return {
        "blocked": blocked,
        "reason": reason,
        "confidence": confidence,
        "category": category,
        "details": details
    }

if __name__ == "__main__":
    test_cases = [
        "This response is contextually relevant and promotes critical thinking.",
        "The AI-generated response lacks contextual information and is misleading.",
        "The topic of this response is not clear, but it seems to be relevant.",
        "The sentiment of this response is negative, which may indicate a lack of contextual understanding.",
        "This response is well-written and provides a clear understanding of the topic."
    ]

    for test_case in test_cases:
        evaluation_results = contextual_understanding_evaluator(test_case)
        print(f"Input Text: {test_case}")
        print(f"Evaluation Results: {json.dumps(evaluation_results, indent=4)}")
        print()