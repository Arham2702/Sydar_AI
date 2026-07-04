// Typed client for the fridge platform API. All responses are unwrapped from
// the { data, meta } envelope. Runs client-side (browser -> FastAPI).
import type {
  Alert,
  Envelope,
  IngestResult,
  InventoryItem,
  RecipeDetail,
  RecipeSuggestion,
  ShoppingItem,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function errorMessage(res: Response): Promise<string> {
  // FastAPI errors are { detail: "..." }; fall back to status text.
  try {
    const body = await res.json();
    if (typeof body?.detail === "string") return body.detail;
    return JSON.stringify(body);
  } catch {
    return res.statusText || `Request failed (${res.status})`;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<Envelope<T>> {
  const res = await fetch(`${BASE}${path}`, {
    cache: "no-store",
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) throw new Error(await errorMessage(res));
  if (res.status === 204) return { data: undefined as T, meta: {} };
  return res.json();
}

export const api = {
  ingest: (sample?: string) =>
    request<IngestResult>(`/api/ingest${sample ? `?sample=${sample}` : ""}`, {
      method: "POST",
    }),

  ingestFile: async (file: File): Promise<Envelope<IngestResult>> => {
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(`${BASE}/api/ingest`, { method: "POST", body: form });
    if (!res.ok) throw new Error(await errorMessage(res));
    return res.json();
  },

  inventory: () => request<InventoryItem[]>("/api/inventory"),
  adjustItem: (id: number, quantity: number) =>
    request<InventoryItem>(`/api/inventory/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ quantity }),
    }),

  alerts: () => request<Alert[]>("/api/alerts"),
  ackAlert: (id: number) => request<Alert>(`/api/alerts/${id}/ack`, { method: "POST" }),

  suggestions: () => request<RecipeSuggestion[]>("/api/recipes/suggestions"),
  recipe: (id: number) => request<RecipeDetail>(`/api/recipes/${id}`),
  addMissing: (id: number) =>
    request<ShoppingItem[]>(`/api/recipes/${id}/add-missing`, { method: "POST" }),

  shopping: () => request<ShoppingItem[]>("/api/shopping"),
  addShopping: (name: string, quantity: number) =>
    request<ShoppingItem>("/api/shopping", {
      method: "POST",
      body: JSON.stringify({ name, quantity }),
    }),
  updateShopping: (id: number, body: { status?: string; quantity?: number }) =>
    request<ShoppingItem>(`/api/shopping/${id}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  deleteShopping: (id: number) =>
    request<void>(`/api/shopping/${id}`, { method: "DELETE" }),
};

export const SAMPLE_SCENES = [
  { id: "fridge_full", label: "Well-stocked fridge" },
  { id: "fridge_low", label: "Running low" },
  { id: "fridge_expiring", label: "Items expiring" },
];
