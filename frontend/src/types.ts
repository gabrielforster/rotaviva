export type MapSource = "preset" | "user" | "generated";
export type MapStyle = "city" | "warehouse";
export type MapSize = "small" | "medium" | "large";

export interface Cell {
  row: number;
  col: number;
}

export interface Point {
  id: string;
  label: string;
  sprite: string;
  cell: Cell;
}

export interface GridModel {
  cell_size: number;
  cells: string[];
}

export interface MapModel {
  id: string;
  name: string;
  source: MapSource;
  style: MapStyle;
  grid: GridModel;
  points: Point[];
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
  style: MapStyle;
  grid: GridModel;
  points: Point[];
}

export interface GenerateRequest {
  style: MapStyle;
  size: MapSize;
  density: number;
  n: number;
  name?: string;
  id?: string;
  seed?: number;
  save?: boolean;
}
