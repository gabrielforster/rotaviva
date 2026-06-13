"""Pydantic request/response models. These mirror the TypeScript types in
``frontend/src/types.ts`` — keep both in sync."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

Style = Literal["city", "warehouse"]


class Cell(BaseModel):
    row: int = Field(ge=0)
    col: int = Field(ge=0)


class Point(BaseModel):
    id: str
    label: str
    sprite: str = "pin"
    cell: Cell


class GridModel(BaseModel):
    cell_size: int = Field(default=40, gt=0)
    cells: list[str] = Field(min_length=1)


class MapModel(BaseModel):
    id: str
    name: str
    source: Literal["preset", "user", "generated"] = "user"
    style: Style = "city"
    grid: GridModel
    points: list[Point]


class MapSummary(BaseModel):
    id: str
    name: str
    source: str
    point_count: int


class CreateMapRequest(BaseModel):
    id: str
    name: str
    style: Style = "city"
    grid: GridModel
    points: list[Point]


class GenerateRequest(BaseModel):
    style: Style = "city"
    size: Literal["small", "medium", "large"] = "medium"
    density: float = Field(default=0.6, ge=0.0, le=1.0)
    n: int = Field(ge=2, le=50)
    name: Optional[str] = None
    id: Optional[str] = None
    seed: Optional[int] = None
    save: bool = False


class OptimizeRequest(BaseModel):
    map_id: str
    stop_ids: list[str] = Field(min_length=2)
    start_id: str
    restarts: Optional[int] = Field(default=None, ge=1, le=1000)
    seed: Optional[int] = None


class Baselines(BaseModel):
    random_cost: float
    brute_force_cost: Optional[float] = None


class OptimizeResponse(BaseModel):
    run_id: int
    tour: list[str]
    total_cost: float
    baselines: Baselines
    brute_force_skipped: bool
    matrix: list[list[int]]
    stop_order: list[str]
    stop_labels: list[str]


class RunSummary(BaseModel):
    id: int
    created_at: str
    map_id: str
    map_name: str
    total_cost: float
    stop_count: int


class RunDetail(BaseModel):
    id: int
    created_at: str
    map_id: str
    map_name: str
    start_id: str
    restarts: int
    seed: Optional[int] = None
    total_cost: float
    baselines: Baselines
    tour: list[str]
    stop_order: list[str]
    stop_labels: list[str]
    matrix: list[list[int]]
