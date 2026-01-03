from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class Confidence(str, Enum):
    STRONG = "strong"
    INCOMPLETE_DATA = "incomplete_data"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Direction(str, Enum):
    INCREASE = "increase"
    DECREASE = "decrease"
    STABLE = "stable"


class Metric(BaseModel):
    """
    A financial metric extracted from the document
    """
    name: str = Field(..., description="Metric name like Revenue, EBITDA")
    value: str = Field(..., description="Extracted numeric value as string")
    period: Optional[str] = Field(None, description="FY2024, Q3FY24, etc.")
    direction: Optional[Direction] = Field(
        None, description="increase / decrease / stable"
    )
    source_pages: List[int] = Field(
        ..., description="Page numbers where this metric appears"
    )
    confidence: Confidence = Field(
        ..., description="Extraction confidence"
    )


class Risk(BaseModel):
    """
    A credit risk explicitly mentioned in the document
    """
    title: str = Field(..., description="Short risk title")
    description: str = Field(..., description="Brief explanation of the risk")
    severity: Severity = Field(
        ..., description="Risk severity: low / medium / high"
    )
    source_pages: List[int] = Field(
        ..., description="Page numbers where the risk appears"
    )
    confidence: Confidence = Field(
        ..., description="Extraction confidence"
    )


class Memo(BaseModel):
    """
    Final structured credit memo
    """
    executive_summary: List[str] = Field(
        ...,
        min_items=3,
        max_items=5,
        description="3–5 short executive summary bullets"
    )
    key_metrics: List[Metric] = Field(
        default_factory=list,
        description="Key financial metrics"
    )
    top_risks: List[Risk] = Field(
        default_factory=list,
        max_items=3,
        description="Top credit risks (if explicitly mentioned)"
    )
