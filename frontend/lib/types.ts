// Shared API types — mirror the backend Pydantic schemas (app/models/schemas.py).

export type FreshnessLevel = "fresh" | "aging" | "expiring" | "expired";

export interface Freshness {
  score: number;
  level: FreshnessLevel;
  days_remaining: number;
}

export interface InventoryItem {
  id: number;
  name: string;
  category: string;
  quantity: number;
  unit: string;
  status: "active" | "depleted" | "removed";
  first_seen_at: string;
  last_seen_at: string;
  freshness: Freshness;
}

export interface DetectedItem {
  name: string;
  category: string;
  count: number;
  confidence: number;
  freshness: number | null;
}

export interface IngestResult {
  source: string;
  simulated: boolean;
  detections: number;
  items_created: number;
  items_updated: number;
  items_depleted: number;
  detected_items: DetectedItem[];
}

export type AlertType = "expiring" | "expired" | "low_stock" | "out_of_stock";

export interface Alert {
  id: number;
  fridge_item_id: number;
  item_name: string;
  alert_type: AlertType;
  severity: "info" | "warning" | "critical";
  message: string;
  acknowledged: boolean;
  created_at: string;
}

export interface RecipeSuggestion {
  id: number;
  name: string;
  description: string;
  cuisine: string;
  prep_minutes: number;
  image_ref: string | null;
  match_score: number;
  owned_count: number;
  required_count: number;
  uses_expiring: boolean;
}

export interface IngredientStatus {
  name: string;
  quantity: number;
  unit: string;
  optional: boolean;
  owned: boolean;
  owned_quantity: number;
}

export interface RecipeDetail {
  id: number;
  name: string;
  description: string;
  cuisine: string;
  prep_minutes: number;
  image_ref: string | null;
  steps: string[];
  ingredients: IngredientStatus[];
  owned_count: number;
  required_count: number;
  missing: IngredientStatus[];
}

export type ShoppingSource = "auto_low_stock" | "auto_out" | "manual";

export interface ShoppingItem {
  id: number;
  name: string;
  quantity: number;
  unit: string;
  source: ShoppingSource;
  status: "needed" | "purchased";
  created_at: string;
}

export interface Envelope<T> {
  data: T;
  meta: Record<string, unknown>;
}
