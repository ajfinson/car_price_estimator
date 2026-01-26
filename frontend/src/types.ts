export interface VehicleInput {
  make: string;
  model: string;
  year: number;
}

export interface Lifetime {
  months: number;
  endReason: "maxYears" | "maxKm";
  totalCost: number;
  costPerMonth: number;
}

export interface Breakdown {
  depreciation: number;
  fuel: number;
  maintenance: number;
  fees: number;
}

export interface Trigger {
  ageYears: number | null;
  km: number | null;
}

export interface Window {
  kmMin: number | null;
  kmMax: number | null;
  ageMin: number | null;
  ageMax: number | null;
}

export interface CostRange {
  low: number;
  mid: number;
  high: number;
}

export interface TimelineItem {
  item: string;
  category: "scheduled" | "wear" | "failure-driven" | "fees";
  trigger: Trigger;
  window: Window;
  description: string;
  cost: CostRange;
  confidence: "low" | "medium" | "high";
  notes: string[];
}

export interface AuditBlock {
  timelineSorted: boolean;
  totalsConsistent: boolean;
  maintenanceMatchesTimelineMid: boolean;
  flags: string[];
}

export interface TcoResult {
  lifetime: Lifetime;
  breakdown: Breakdown;
  timeline: TimelineItem[];
  audit: AuditBlock;
  overallConfidence: "low" | "medium" | "high";
}
