from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class CompanyInfo(BaseModel):
    """
    Seller/Company information for credit memo
    """
    name: str = Field(default="", description="Company name")
    address: str = Field(default="", description="Full address")
    gstin: str = Field(default="", description="GSTIN/Tax ID")
    state: str = Field(default="", description="State name")
    state_code: str = Field(default="", description="State code")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")


class BuyerInfo(BaseModel):
    """
    Buyer information for credit memo
    """
    name: str = Field(default="", description="Buyer name")
    address: str = Field(default="", description="Full address")
    gstin: str = Field(default="", description="GSTIN/Tax ID")
    state: str = Field(default="", description="State name")
    state_code: str = Field(default="", description="State code")


class MemoMeta(BaseModel):
    """
    Credit memo metadata
    """
    credit_note_no: str = Field(default="", description="Credit note number")
    date: str = Field(default="", description="Date of credit note")
    buyers_ref: str = Field(default="", description="Buyer's reference")
    buyers_order_no: str = Field(default="", description="Buyer's order number")
    order_date: str = Field(default="", description="Order date")
    dispatch_doc_no: str = Field(default="", description="Dispatch document number")
    dispatch_through: str = Field(default="", description="Dispatch method")
    destination: str = Field(default="", description="Destination")
    terms: str = Field(default="", description="Terms and conditions")


class MemoItem(BaseModel):
    """
    Line item in credit memo
    """
    description: str = Field(..., description="Item description")
    batch: Optional[str] = Field(None, description="Batch number")
    hsn: str = Field(default="", description="HSN/SAC code")
    quantity: float = Field(..., description="Quantity")
    rate: float = Field(..., description="Rate per unit")
    per: str = Field(default="Nos", description="Unit (Nos, Pcs, etc.)")
    amount: float = Field(..., description="Total amount (quantity * rate)")


class Confidence(str, Enum):
    STRONG = "strong"  # Directly extracted from document
    CALCULATED = "calculated"  # Computed from other metrics (e.g., ratios)
    INCOMPLETE_DATA = "incomplete_data"  # Missing or unclear data


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
    Complete credit memo with company info, buyer info, line items, and financial analysis
    """
    # Credit Memo Fields
    company_info: CompanyInfo = Field(default_factory=CompanyInfo, description="Seller/Company information")
    buyer_info: BuyerInfo = Field(default_factory=BuyerInfo, description="Buyer information")
    memo_meta: MemoMeta = Field(default_factory=MemoMeta, description="Credit memo metadata")
    memo_items: List[MemoItem] = Field(default_factory=list, description="Line items")
    cgst_rate: float = Field(default=0, description="CGST rate percentage")
    sgst_rate: float = Field(default=0, description="SGST rate percentage")
    
    # Financial Analysis Fields
    executive_summary: List[str] = Field(
        default_factory=list,
        description="3–5 short executive summary bullets"
    )
    key_metrics: List[Metric] = Field(
        default_factory=list,
        description="Key financial metrics"
    )
    top_risks: List[Risk] = Field(
        default_factory=list,
        description="Top credit risks (max 3)"
    )
