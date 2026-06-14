import type {
  CreateMapRequest,
  GenerateRequest,
  MapModel,
  MapSummary,
  OptimizeRequest,
  OptimizeResponse,
  RunDetail,
  RunSummary,
} from "@/types";

const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "content-type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    let detail: unknown = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      // non-JSON error body; keep the status text
    }
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  listMaps: () => request<MapSummary[]>("/maps"),
  getMap: (id: string) => request<MapModel>(`/maps/${id}`),
  createMap: (body: CreateMapRequest) =>
    request<MapModel>("/maps", { method: "POST", body: JSON.stringify(body) }),
  deleteMap: (id: string) =>
    request<void>(`/maps/${id}`, { method: "DELETE" }),
  generateMap: (body: GenerateRequest) =>
    request<MapModel>("/maps/generate", { method: "POST", body: JSON.stringify(body) }),
  optimize: (body: OptimizeRequest) =>
    request<OptimizeResponse>("/optimize", { method: "POST", body: JSON.stringify(body) }),
  listRuns: () => request<RunSummary[]>("/runs"),
  getRun: (id: number) => request<RunDetail>(`/runs/${id}`),
  deleteRun: (id: number) =>
    request<void>(`/runs/${id}`, { method: "DELETE" }),
  routeChartUrl: (id: number) => `${BASE}/runs/${id}/route.png`,
  evolutionChartUrl: (id: number) => `${BASE}/runs/${id}/evolution.png`,
};
