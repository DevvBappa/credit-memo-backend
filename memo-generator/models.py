from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class Confidence(str, Enum):
    STRONG = "strong"
    INCOMPLETE_DATA = "incomplete_data"

class Metric(BaseModel):
    name: str = Field(..., description="Metric name like 'Revenue'")
    value: str = Field(..., description="Extracted value as string")
    period: Optional[str] = Field(None, description="FY2024 etc.")
    direction: Optional[str] = Field(None, description="increase/decrease/stable")
    source_pages: List[int] = Field(..., description="Page numbers")
    confidence: Confidence

class Risk(BaseModel):
    title: str = Field(..., description="Risk title")
    description: str = Field(..., description="Short explanation")
    severity: str = Field(..., description="low/medium/high")
    source_pages: List[int] = Field(..., description="Page numbers")
    confidence: Confidence

class Memo(BaseModel):
    """Credit memo structure"""
    executive_summary: List[str] = Field(..., max_items=5, description="3-5 bullets")
    key_metrics: List[Metric] = Field(default_factory=list)
    top_risks: List[Risk] = Field(..., max_items=3)