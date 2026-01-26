from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class VehicleInput(BaseModel):
    make: str
    model: str
    year: int


class Lifetime(BaseModel):
    months: int
    endReason: Literal["maxYears", "maxKm"]
    totalCost: float
    costPerMonth: float


class Breakdown(BaseModel):
    depreciation: float
    fuel: float
    maintenance: float
    fees: float


class Trigger(BaseModel):
    ageYears: Optional[float] = None
    km: Optional[int] = None


class Window(BaseModel):
    kmMin: Optional[int] = None
    kmMax: Optional[int] = None
    ageMin: Optional[float] = None
    ageMax: Optional[float] = None


class CostRange(BaseModel):
    low: float
    mid: float
    high: float


class TimelineItem(BaseModel):
    item: str
    category: Literal["scheduled", "wear", "failure-driven", "fees"]
    trigger: Trigger
    window: Window
    description: str
    cost: CostRange
    confidence: Literal["low", "medium", "high"]
    notes: List[str]


class AuditBlock(BaseModel):
    timelineSorted: bool
    totalsConsistent: bool
    maintenanceMatchesTimelineMid: bool
    flags: List[str]


class TcoResult(BaseModel):
    lifetime: Lifetime
    breakdown: Breakdown
    timeline: List[TimelineItem]
    audit: AuditBlock
    overallConfidence: Literal["low", "medium", "high"]


class Assumptions(BaseModel):
    kmPerYear: int
    fuelPricePerLiter: float
    maxYears: int
    maxKm: int
