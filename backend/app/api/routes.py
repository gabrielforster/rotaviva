"""Thin HTTP layer: validation, id<->index mapping, exception translation.
No business logic lives here — it orchestrates the routing core and the store."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.maps import generate as gen
from app.maps import store
from app.maps.grid import GridError, matrix_for_map
from app.routing.baselines import brute_force_optimal, random_route_cost
from app.routing.hill_climbing import hill_climb

from .schemas import (
    Baselines,
    CreateMapRequest,
    GenerateRequest,
    MapModel,
    MapSummary,
    OptimizeRequest,
    OptimizeResponse,
)

router = APIRouter()


@router.get("/maps", response_model=list[MapSummary])
def list_maps() -> list[dict]:
    return store.list_maps()


# Static "/maps/generate" is declared before the parameterized "/maps/{map_id}"
# as a tidy convention. (They use different methods — POST vs GET — so order does
# not actually affect matching here.)
@router.post("/maps/generate", response_model=MapModel)
def generate_map(req: GenerateRequest) -> dict:
    map_id = req.id or f"gerado-{req.style}-{req.n}-{req.seed if req.seed is not None else 'rnd'}"
    name = req.name or f"Mapa gerado ({req.n} pontos)"
    data = gen.generate_map(
        map_id, name, req.n, style=req.style, size=req.size, density=req.density, seed=req.seed
    )
    if req.save:
        try:
            return store.create_map(data)
        except store.MapValidationError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except store.MapConflict as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except store.MapError as exc:  # IO failure
            raise HTTPException(status_code=500, detail=str(exc)) from exc
    return data


@router.get("/maps/{map_id}", response_model=MapModel)
def get_map(map_id: str) -> dict:
    try:
        return store.get_map(map_id)
    except store.MapNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/maps", response_model=MapModel, status_code=201)
def create_map(req: CreateMapRequest) -> dict:
    data = req.model_dump()
    data["source"] = "user"
    try:
        return store.create_map(data)
    except store.MapValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except store.MapConflict as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except store.MapError as exc:  # IO failure
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/maps/{map_id}", status_code=204)
def delete_map(map_id: str) -> None:
    try:
        store.delete_map(map_id)
    except store.PresetReadOnly as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except store.MapNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/optimize", response_model=OptimizeResponse)
def optimize(req: OptimizeRequest) -> OptimizeResponse:
    try:
        m = store.get_map(req.map_id)
    except store.MapNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    index_of = {p["id"]: i for i, p in enumerate(m["points"])}
    unknown = [s for s in req.stop_ids if s not in index_of]
    if unknown:
        raise HTTPException(status_code=422, detail=f"unknown stop ids: {unknown}")
    if len(set(req.stop_ids)) != len(req.stop_ids):
        raise HTTPException(status_code=422, detail="stop_ids must be unique")
    if req.start_id not in req.stop_ids:
        raise HTTPException(status_code=422, detail="start_id must be one of stop_ids")

    # Order stops with the start first, then the remaining stops in request order.
    ordered = [req.start_id] + [s for s in req.stop_ids if s != req.start_id]
    orig = [index_of[s] for s in ordered]
    try:
        full = matrix_for_map(m)
    except GridError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    sub = [[full[a][b] for b in orig] for a in orig]
    n = len(ordered)

    settings = get_settings()
    restarts = req.restarts or settings.default_restarts
    best_tour, best_cost, history = hill_climb(sub, n, restarts, req.seed)

    # best_tour[0] is always 0 (start fixed); close the loop back to the start.
    tour_ids = [ordered[i] for i in best_tour] + [ordered[0]]
    random_cost = random_route_cost(sub, n, req.seed)
    brute = brute_force_optimal(sub, n, settings.brute_force_guard)

    return OptimizeResponse(
        tour=tour_ids,
        total_cost=best_cost,
        history=history,
        baselines=Baselines(random_cost=random_cost, brute_force_cost=brute),
        brute_force_skipped=(brute is None),
    )
