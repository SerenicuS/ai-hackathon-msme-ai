// Shared TypeScript types for JSON database fields

export interface LocationData {
  city: string;
  district: string;
  area: string;
}

export interface EligibilityData {
  philgap_certified: boolean;
  philgap_id?: string;
}

export interface FarmDescription {
  bearing_trees: number;
  total_hectares: number;
  elevation_meters: number;
  soil_type: string;
  annual_rainfall_mm: number;
}

export interface CutTestResults {
  moldy_percent: number;
  insect_damaged_percent: number;
}

export interface QualityAudit {
  cut_test_results: CutTestResults;
  moisture_content: number;
  moisture?: number; // Alternate field name used in seeder
}

// Supplier Score calculation result
export interface SupplierScore {
  supplier_id: string;
  score: number;
}

// Leaderboard entry with full supplier details
export interface LeaderboardEntry {
  supplier_id: string;
  name: string;
  location: LocationData;
  reliability_score: number;
  description: FarmDescription;
  eligibility: EligibilityData;
}

// Historical data point for forecasting
export interface DataPoint {
  date: Date;
  value: number;
}

// Order suggestion for inventory management
export interface OrderSuggestion {
  supplier: string;
  rank_score: number;
  suggested_order_kg: number;
  reason: string;
}

// Inventory analysis details
export interface InventoryAnalysis {
  current_storage: number;
  projected_end_stock?: number;
  predicted_usage_spike?: number;
  required_purchase_kg: number;
}

// Response types
export interface UpdateScoresResponse {
  status: string;
  message: string;
  data?: LeaderboardEntry[];
}

export interface PredictDemandResponse {
  status: string;
  message: string;
  forecast_total_kg?: number;
}

export interface SuggestOrdersResponse {
  status: string;
  message: string;
  analysis: InventoryAnalysis;
  ai_suggestion?: OrderSuggestion[];
}
