export type MapSource = "preset" | "user" | "generated";

export interface Point {
  id: string;
  label: string;
  sprite: string;
  x: number;
  y: number;
}

export interface MapModel {
  id: string;
  name: string;
  source: MapSource;
  symmetric: boolean;
  points: Point[];
  matrix: number[][];
}

export interface MapSummary {
  id: string;
  name: string;
  source: MapSource;
  point_count: number;
}

export interface Baselines {
  random_cost: number;
  brute_force_cost: number | null;
}

export interface OptimizeResponse {
  tour: string[];
  total_cost: number;
  history: number[];
  baselines: Baselines;
  brute_force_skipped: boolean;
}

export interface OptimizeRequest {
  map_id: string;
  stop_ids: string[];
  start_id: string;
  restarts?: number;
  seed?: number;
}

export interface CreateMapRequest {
  id: string;
  name: string;
  symmetric: boolean;
  points: Point[];
  matrix: number[][];
}

export interface GenerateRequest {
  n: number;
  name?: string;
  id?: string;
  seed?: number;
  save?: boolean;
}
