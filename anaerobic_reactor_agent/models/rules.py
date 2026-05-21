"""Rule and condition data models for the rule engine."""

from typing import List, Union, Literal, Optional
from pydantic import BaseModel, Field


class Condition(BaseModel):
    """A single condition within a fault rule."""

    parameter: str
    operator: Literal[">", "<", ">=", "<=", "==", "!=", "between", "not_between", "trend"]
    value: Union[float, List[float]]
    weight: float = Field(default=1.0, ge=0, le=1)
    fuzzy: bool = Field(default=False, description="Use fuzzy evaluation near threshold")


class Recommendation(BaseModel):
    """A graded recommendation with urgency level."""

    text: str
    level: Literal["immediate", "long_term", "preventive"] = "long_term"


class FaultRule(BaseModel):
    """A fault diagnosis rule with multiple weighted conditions."""

    name: str
    description: str
    fault_type: str
    priority: int = Field(default=10, ge=1)
    conditions: List[Condition]
    min_confidence: float = Field(default=0.5, ge=0, le=1)
    recommendations: List[Recommendation]
    severity: Literal["warning", "alarm", "critical"] = "warning"
    causal_chain: Optional[str] = Field(default=None, description="Causal explanation")
