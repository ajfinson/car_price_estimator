from pydantic import BaseModel
from typing import List, Literal


class VehicleInput(BaseModel):
    make: str
    model: str
    year: int


class VehicleInfo(BaseModel):
    make: str
    model: str
    year: int


class Lifetime(BaseModel):
    totalCost: float
    costPerMonth: float
    months: int
    endReason: Literal["maxYears", "maxKm"]


class Breakdown(BaseModel):
    depreciation: float
    fuel: float
    maintenance: float
    fees: float


class Assumptions(BaseModel):
    kmPerYear: int
    fuelPricePerLiter: float
    maxYears: int
    maxKm: int


class Source(BaseModel):
    title: str
    url: str
    snippet: str


class TcoResult(BaseModel):
    vehicle: VehicleInfo
    lifetime: Lifetime
    breakdown: Breakdown
    assumptionsUsed: Assumptions
    sourcesUsed: List[Source]
    confidence: Literal["low", "medium", "high"]
    notes: List[str]
