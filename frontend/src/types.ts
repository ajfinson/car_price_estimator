export interface VehicleInput {
  make: string;
  model: string;
  year: number;
}

export interface VehicleInfo {
  make: string;
  model: string;
  year: number;
}

export interface Lifetime {
  totalCost: number;
  costPerMonth: number;
  months: number;
  endReason: "maxYears" | "maxKm";
}

export interface Breakdown {
  depreciation: number;
  fuel: number;
  maintenance: number;
  fees: number;
}

export interface Assumptions {
  kmPerYear: number;
  fuelPricePerLiter: number;
  maxYears: number;
  maxKm: number;
}

export interface Source {
  title: string;
  url: string;
  snippet: string;
}

export interface TcoResult {
  vehicle: VehicleInfo;
  lifetime: Lifetime;
  breakdown: Breakdown;
  assumptionsUsed: Assumptions;
  sourcesUsed: Source[];
  confidence: "low" | "medium" | "high";
  notes: string[];
}
