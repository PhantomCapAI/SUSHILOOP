"""Core data schemas for SUSHI LOOP"""
from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import uuid4
from datetime import datetime

class ProposalType(str, Enum):
    NEW_SKILL = "NEW_SKILL"

class CycleResult(str, Enum):
    SUCCESS = "SUCCESS"
    REJECTED = "REJECTED"
    TEST_FAILED = "TEST_FAILED"
    ERROR = "ERROR"

class SkillCategory(str, Enum):
    INPUT_VALIDATION = "INPUT_VALIDATION"
    OUTPUT_FILTERING = "OUTPUT_FILTERING"
    RATE_LIMITING = "RATE_LIMITING"
    CONTENT_SAFETY = "CONTENT_SAFETY"
    PII_DETECTION = "PII_DETECTION"
    COGNITIVE_PROTECTION = "COGNITIVE_PROTECTION"
    VERIFICATION_PROMPT = "VERIFICATION_PROMPT"
    BIAS_DETECTION = "BIAS_DETECTION"

class Proposal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    proposal_type: ProposalType
    category: SkillCategory
    title: str
    description: str
    rationale: str
    success_criteria: List[str]
    tests_required: List[str]
    estimated_complexity: int = Field(ge=1, le=8)
    rollback_plan: str
    created_at: datetime = Field(default_factory=datetime.now)

class TestResult(BaseModel):
    passed: bool
    test_name: str
    message: str
    duration_seconds: float = 0.0

class CycleHistory(BaseModel):
    cycle_number: int
    proposal: Proposal
    result: CycleResult
    skill_generated: Optional[str] = None
    test_results: List[TestResult] = []
    timestamp: datetime = Field(default_factory=datetime.now)
    error_message: Optional[str] = None

class LoopState(BaseModel):
    cycle_count: int = 0
    total_skills: int = 0
    success_count: int = 0
    failure_count: int = 0
    last_run: Optional[datetime] = None
    history: List[CycleHistory] = []
