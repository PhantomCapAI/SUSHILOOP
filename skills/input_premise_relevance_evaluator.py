import re
import math
from typing import Dict
from dataclasses import dataclass

@dataclass
class PremiseRelevanceEvaluation:
    blocked: bool
    reason: str
    confidence: float
    category: str
    details: Dict[str, float]

def input_premise_relevance_evaluator(input_text: str) -> Dict[str, object]:
    """
    Evaluates the relevance of input premises to the problem being addressed.

    This function assesses the input premises based on their novelty, diversity, and pertinence to the problem at hand.
    It protects human cognition by preventing information overload and promoting a more focused and efficient decision-making process.
    The function integrates seamlessly with existing skills and provides informative feedback on premise relevance.

    Args:
        input_text (str): The input text to be evaluated.

    Returns:
        Dict[str, object]: A dictionary containing the evaluation results, including:
            - blocked (bool): Whether the input premise is blocked.
            - reason (str): The reason for blocking the input premise.
            - confidence (float): The confidence level of the evaluation (0.0-1.0).
            - category (str): The category of the input premise.
            - details (Dict[str, float]): A dictionary containing detailed evaluation metrics.

    Mission Alignment:
        This function aligns with the mission of promoting AI safety by ensuring that humans are not overwhelmed with irrelevant information.
        It enhances critical thinking and problem-solving abilities by distinguishing between relevant and irrelevant information.
    """

    # Detection Strategy 1: Keyword Check
    keyword_check = re.search(r"\b(irrelevant|off-topic|unrelated)\b", input_text, re.IGNORECASE)
    keyword_score = 0.0 if keyword_check else 1.0

    # Detection Strategy 2: Novelty Check
    novelty_check = re.search(r"\b(new|novel|innovative)\b", input_text, re.IGNORECASE)
    novelty_score = 1.0 if novelty_check else 0.5

    # Detection Strategy 3: Diversity Check
    diversity_check = re.search(r"\b(diverse|varied|multiple)\b", input_text, re.IGNORECASE)
    diversity_score = 1.0 if diversity_check else 0.5

    # Detection Strategy 4: Pertinence Check
    pertinence_check = re.search(r"\b(relevant|pertinent|related)\b", input_text, re.IGNORECASE)
    pertinence_score = 1.0 if pertinence_check else 0.0

    # Weighted Scoring
    weighted_score = (0.3 * keyword_score) + (0.2 * novelty_score) + (0.2 * diversity_score) + (0.3 * pertinence_score)

    # Confidence Calibration
    confidence = math.tanh(weighted_score * 2)

    # Evaluation Results
    blocked = confidence < 0.5
    reason = "Input premise is blocked due to low relevance" if blocked else "Input premise is allowed due to high relevance"
    category = "relevant" if not blocked else "irrelevant"
    details = {
        "keyword_score": keyword_score,
        "novelty_score": novelty_score,
        "diversity_score": diversity_score,
        "pertinence_score": pertinence_score,
        "weighted_score": weighted_score
    }

    return {
        "blocked": blocked,
        "reason": reason,
        "confidence": confidence,
        "category": category,
        "details": details
    }

if __name__ == "__main__":
    test_cases = [
        "This is a relevant input premise.",
        "This input premise is off-topic and should be blocked.",
        "The new innovative solution is relevant to the problem.",
        "The diverse range of options is pertinent to the task.",
        "The unrelated information should be ignored.",
        "The novel approach is not relevant to the current problem.",
        "The multiple solutions are varied but not diverse.",
        "The relevant information is crucial to the decision-making process.",
        "The irrelevant data should be filtered out.",
        "The pertinent details are essential to the task."
    ]

    for test_case in test_cases:
        evaluation = input_premise_relevance_evaluator(test_case)
        print(f"Input Text: {test_case}")
        print(f"Blocked: {evaluation['blocked']}")
        print(f"Reason: {evaluation['reason']}")
        print(f"Confidence: {evaluation['confidence']}")
        print(f"Category: {evaluation['category']}")
        print(f"Details: {evaluation['details']}")
        print("-" * 50)