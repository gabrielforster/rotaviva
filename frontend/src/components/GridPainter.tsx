import { useEffect, useState } from "react";
import type { CreateMapRequest, MapStyle, Point } from "@/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { bfsPath } from "@/lib/grid";
import { SPRITE_EMOJI, SPRITE_LABELS, SPRITES } from "@/lib/sprites";
const CELL_SIZE = 40;

function blankGrid(rows: number, cols: number): string[] {
  return Array.from({ length: rows }, () => ".".repeat(cols));
}

function setChar(row: string, col: number, ch: string): string {
  return row.slice(0, col) + ch + row.slice(col + 1);
}

const pid = (i: number) => (i < 26 ? String.fromCharCode(97 + i) : `p${i}`);

// A full snapshot of the editable state, pushed before each undoable edit.
type Snapshot = {
  rows: number;
  cols: number;
  cells: string[];
  points: Point[];
  nextIdx: number;
};

interface Props {
  onCancel: () => void;
  onSave: (body: CreateMapRequest) => Promise<void>;
}

export function GridPainter({ onCancel, onSave }: Props) {
  const [id, setId] = useState("");
  const [name, setName] = useState("");
  const [style, setStyle] = useState<MapStyle>("warehouse");
  const [rows, setRows] = useState(8);
  const [cols, setCols] = useState(11);
  const [cells, setCells] = useState<string[]>(() => blankGrid(8, 11));
  const [points, setPoints] = useState<Point[]>([]);
  const [mode, setMode] = useState<"paint" | "point">("paint");
  const [error, setError] = useState<string | null>(null);
  // Monotonic id counter so removing then re-adding a point never reuses an id.
  const [nextIdx, setNextIdx] = useState(0);
  // Drag-to-paint: the value ("#"/".") chosen at mouse-down, applied to every
  // cell the pointer enters until the button is released anywhere on the page.
  const [drag, setDrag] = useState<null | "#" | ".">(null);

  useEffect(() => {
    const stop = () => setDrag(null);
    window.addEventListener("mouseup", stop);
    return () => window.removeEventListener("mouseup", stop);
  }, []);

  // Undo stack: snapshot the state before each paint stroke / point change so a
  // single click of "Desfazer" steps back exactly one edit (capped at 50).
  const [history, setHistory] = useState<Snapshot[]>([]);

  const pushHistory = () =>
    setHistory((h) => [...h, { rows, cols, cells, points, nextIdx }].slice(-50));

  const undo = () => {
    if (history.length === 0) return;
    const prev = history[history.length - 1];
    setRows(prev.rows);
    setCols(prev.cols);
    setCells(prev.cells);
    setPoints(prev.points);
    setNextIdx(prev.nextIdx);
    setHistory(history.slice(0, -1));
    setError(null);
  };

  const grid = { cell_size: CELL_SIZE, cells };

  const resize = (nextRows: number, nextCols: number) => {
    const r = Math.max(2, Math.min(24, nextRows || 2));
    const c = Math.max(2, Math.min(30, nextCols || 2));
    const next = Array.from({ length: r }, (_, i) =>
      (cells[i] ?? "").slice(0, c).padEnd(c, "."),
    );
    setRows(r);
    setCols(c);
    setCells(next);
    setPoints((ps) =>
      ps.filter(
        (p) => p.cell.row < r && p.cell.col < c && next[p.cell.row][p.cell.col] === ".",
      ),
    );
  };

  const hasPoint = (r: number, c: number) =>
    points.find((p) => p.cell.row === r && p.cell.col === c);

  const paintCell = (r: number, c: number, value: "#" | ".") => {
    if (value === "#" && hasPoint(r, c)) return; // don't wall a cell with a point
    setCells((prev) =>
      prev[r][c] === value ? prev : prev.map((row, i) => (i === r ? setChar(row, c, value) : row)),
    );
  };

  const togglePoint = (r: number, c: number) => {
    if (cells[r][c] === "#") return; // can't place on a wall
    const existing = hasPoint(r, c);
    if (existing) {
      setPoints(points.filter((p) => p !== existing));
      return;
    }
    const i = points.length;
    setNextIdx(nextIdx + 1);
    setPoints([
      ...points,
      {
        id: pid(nextIdx),
        label: i === 0 ? "Depósito" : `Parada ${i}`,
        sprite: i === 0 ? "factory" : style === "warehouse" ? "pin" : "shop",
        cell: { row: r, col: c },
      },
    ]);
  };

  // Mouse-down on a cell: in point mode toggle a point; in paint mode pick the
  // paint value from the starting cell (free → wall, wall → erase) and start a drag.
  const startCell = (r: number, c: number) => {
    setError(null);
    if (mode === "point") {
      if (cells[r][c] === "#") return; // can't place on a wall — nothing changes
      pushHistory();
      togglePoint(r, c);
      return;
    }
    const value: "#" | "." = cells[r][c] === "#" ? "." : "#";
    if (value === "#" && hasPoint(r, c)) return; // can't wall a point — nothing changes
    pushHistory();
    setDrag(value);
    paintCell(r, c, value);
  };

  // Pointer enters a cell mid-drag: keep applying the same paint value.
  const enterCell = (r: number, c: number) => {
    if (drag && mode === "paint") paintCell(r, c, drag);
  };

  const setPoint = (idx: number, patch: Partial<Point>) =>
    setPoints(points.map((p, i) => (i === idx ? { ...p, ...patch } : p)));

  const connected = () =>
    points.length < 2 ||
    points.slice(1).every((p) => bfsPath(grid, points[0].cell, p.cell) !== null);

  const submit = async () => {
    setError(null);
    if (!id.trim() || !name.trim()) return setError("ID e Nome são obrigatórios.");
    if (points.length < 2) return setError("Adicione pelo menos 2 pontos.");
    if (!connected())
      return setError("Todos os pontos precisam estar conectados por ruas/corredores.");
    try {
      await onSave({ id, name, style, grid, points });
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-2">
        <div className="space-y-1">
          <Label htmlFor="g-id">ID (slug)</Label>
          <Input id="g-id" value={id} onChange={(e) => setId(e.target.value)} placeholder="meu-galpao" />
        </div>
        <div className="space-y-1">
          <Label htmlFor="g-name">Nome</Label>
          <Input id="g-name" value={name} onChange={(e) => setName(e.target.value)} placeholder="Meu Galpão" />
        </div>
      </div>

      <div className="flex flex-wrap items-end gap-3">
        <div className="space-y-1">
          <Label htmlFor="g-style">Estilo</Label>
          <select
            id="g-style"
            className="h-9 rounded-md border px-2 text-sm"
            value={style}
            onChange={(e) => setStyle(e.target.value as MapStyle)}
          >
            <option value="city">Cidade (ruas + prédios)</option>
            <option value="warehouse">Galpão (corredores + prateleiras)</option>
          </select>
        </div>
        <div className="space-y-1">
          <Label htmlFor="g-rows">Linhas</Label>
          <Input id="g-rows" type="number" min={2} max={24} value={rows}
            onChange={(e) => resize(Number(e.target.value), cols)} className="w-20" />
        </div>
        <div className="space-y-1">
          <Label htmlFor="g-cols">Colunas</Label>
          <Input id="g-cols" type="number" min={2} max={30} value={cols}
            onChange={(e) => resize(rows, Number(e.target.value))} className="w-20" />
        </div>
      </div>

      <div className="flex gap-2">
        <Button size="sm" variant={mode === "paint" ? "default" : "outline"} onClick={() => setMode("paint")}>
          {style === "warehouse" ? "Pintar prateleiras" : "Pintar prédios"}
        </Button>
        <Button size="sm" variant={mode === "point" ? "default" : "outline"} onClick={() => setMode("point")}>
          Soltar pontos
        </Button>
        <Button
          size="sm"
          variant="outline"
          className="ml-auto"
          onClick={undo}
          disabled={history.length === 0}
        >
          ↶ Desfazer
        </Button>
      </div>

      <p className="text-xs text-muted-foreground">
        {mode === "paint"
          ? "Clique e arraste para pintar; clique numa célula pintada para apagar."
          : "Clique numa célula livre para adicionar ou remover um ponto."}
      </p>

      <div className="overflow-auto rounded-md border p-2">
        <div
          className="inline-grid gap-0.5 select-none"
          style={{ gridTemplateColumns: `repeat(${cols}, 18px)` }}
        >
          {cells.flatMap((row, r) =>
            row.split("").map((ch, c) => {
              const pt = hasPoint(r, c);
              const bg = pt
                ? "#16a34a"
                : ch === "#"
                  ? style === "warehouse"
                    ? "#b08968"
                    : "#c8cfda"
                  : "#eef2f7";
              return (
                <button
                  key={`${r}-${c}`}
                  type="button"
                  draggable={false}
                  onMouseDown={(e) => {
                    e.preventDefault();
                    startCell(r, c);
                  }}
                  onMouseEnter={() => enterCell(r, c)}
                  title={pt ? pt.label : `${r},${c}`}
                  style={{ width: 18, height: 18, background: bg, fontSize: 10, lineHeight: "18px" }}
                  className="rounded-sm border border-black/5"
                >
                  {pt ? "•" : ""}
                </button>
              );
            }),
          )}
        </div>
      </div>

      {points.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-medium">Pontos</p>
          {points.map((p, i) => (
            <div key={p.id} className="flex items-center gap-2">
              <span className="w-6 text-xs text-muted-foreground">{p.id}</span>
              <Input value={p.label} onChange={(e) => setPoint(i, { label: e.target.value })} className="flex-1" />
              <select
                className="h-9 rounded-md border px-2 text-sm"
                value={p.sprite}
                onChange={(e) => setPoint(i, { sprite: e.target.value })}
              >
                {SPRITES.map((spr) => (
                  <option key={spr} value={spr}>
                    {SPRITE_EMOJI[spr] ?? "📍"} {SPRITE_LABELS[spr] ?? spr}
                  </option>
                ))}
              </select>
            </div>
          ))}
        </div>
      )}

      {error && <p className="text-sm text-red-600">{error}</p>}

      <div className="flex gap-2">
        <Button onClick={submit}>Salvar mapa</Button>
        <Button variant="outline" onClick={onCancel}>Cancelar</Button>
      </div>
    </div>
  );
}
