"""Pydantic request/response models. These mirror the TypeScript types in
``frontend/src/types.ts`` — keep both in sync."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class Point(BaseModel):
    id: str
    label: str
    sprite: str = "pin"
    x: float
    y: float


class MapModel(BaseModel):
    id: str
    name: str
    source: Literal["preset", "user", "generated"] = "user"
    symmetric: bool = True
    points: list[Point]
    matrix: list[list[float]]


class MapSummary(BaseModel):
    id: str
    name: str
    source: str
    point_count: int


class CreateMapRequest(BaseModel):
    id: str
    name: str
    symmetric: bool = True
    points: list[Point]
    matrix: list[list[float]]


class GenerateRequest(BaseModel):
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
    tour: list[str]
    total_cost: float
    history: list[float]
    baselines: Baselines
    brute_force_skipped: bool
