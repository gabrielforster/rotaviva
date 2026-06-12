import { useState } from "react";
import type { CreateMapRequest, Point } from "@/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const SPRITES = ["shop", "home", "factory", "park", "school", "hospital", "pin"];

function euclid(a: Point, b: Point): number {
  return Math.round(Math.hypot(a.x - b.x, a.y - b.y) * 100) / 100;
}

function recompute(points: Point[]): number[][] {
  return points.map((a) =>
    points.map((b) => (a.id === b.id ? 0 : euclid(a, b))),
  );
}

interface Props {
  onCancel: () => void;
  onSave: (body: CreateMapRequest) => Promise<void>;
}

export function MapEditor({ onCancel, onSave }: Props) {
  const [id, setId] = useState("");
  const [name, setName] = useState("");
  const [points, setPoints] = useState<Point[]>([
    { id: "a", label: "Ponto A", sprite: "shop", x: 80, y: 80 },
    { id: "b", label: "Ponto B", sprite: "home", x: 300, y: 120 },
  ]);
  const [matrix, setMatrix] = useState<number[][]>(() => recompute(points));
  const [error, setError] = useState<string | null>(null);
  // Monotonic counter for new point ids so removing then re-adding never collides.
  const [nextIdx, setNextIdx] = useState(points.length);

  const setPoint = (i: number, patch: Partial<Point>) => {
    const next = points.map((p, idx) => (idx === i ? { ...p, ...patch } : p));
    setPoints(next);
    setMatrix(recompute(next));
  };

  const addPoint = () => {
    const letter = String.fromCharCode(97 + nextIdx);
    const next: Point[] = [
      ...points,
      { id: letter, label: `Ponto ${letter.toUpperCase()}`, sprite: "pin", x: 150, y: 200 },
    ];
    setPoints(next);
    setMatrix(recompute(next));
    setNextIdx(nextIdx + 1);
  };

  const removePoint = (i: number) => {
    const next = points.filter((_, idx) => idx !== i);
    setPoints(next);
    setMatrix(recompute(next));
  };

  const setCell = (i: number, j: number, value: number) => {
    setMatrix(matrix.map((row, r) => row.map((c, k) => (r === i && k === j ? value : c))));
  };

  const submit = async () => {
    setError(null);
    if (!id.trim() || !name.trim()) {
      setError("ID e Nome são obrigatórios.");
      return;
    }
    try {
      await onSave({ id, name, symmetric: true, points, matrix });
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-2">
        <div className="space-y-1">
          <Label htmlFor="m-id">ID (slug)</Label>
          <Input
            id="m-id"
            value={id}
            onChange={(e) => setId(e.target.value)}
            placeholder="meu-mapa"
          />
        </div>
        <div className="space-y-1">
          <Label htmlFor="m-name">Nome</Label>
          <Input
            id="m-name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Meu Mapa"
          />
        </div>
      </div>

      <div className="space-y-2">
        <p className="text-sm font-medium">Pontos</p>
        {points.map((p, i) => (
          <div key={p.id} className="flex items-center gap-2">
            <Input
              value={p.label}
              onChange={(e) => setPoint(i, { label: e.target.value })}
              className="flex-1"
            />
            <select
              className="h-9 rounded-md border px-2 text-sm"
              value={p.sprite}
              onChange={(e) => setPoint(i, { sprite: e.target.value })}
            >
              {SPRITES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
            <Input
              type="number"
              value={p.x}
              onChange={(e) => setPoint(i, { x: Number(e.target.value) })}
              className="w-20"
            />
            <Input
              type="number"
              value={p.y}
              onChange={(e) => setPoint(i, { y: Number(e.target.value) })}
              className="w-20"
            />
            <Button
              variant="ghost"
              size="sm"
              onClick={() => removePoint(i)}
              disabled={points.length <= 2}
            >
              ✕
            </Button>
          </div>
        ))}
        <Button variant="outline" size="sm" onClick={addPoint}>
          + Ponto
        </Button>
      </div>

      <div className="space-y-2">
        <p className="text-sm font-medium">
          Matriz de distâncias (editável; padrão = Euclidiana)
        </p>
        <div className="overflow-auto">
          <table className="text-xs">
            <tbody>
              {matrix.map((row, i) => (
                <tr key={i}>
                  {row.map((cell, j) => (
                    <td key={j} className="p-0.5">
                      <input
                        className="w-14 rounded border px-1 py-0.5 text-right"
                        value={cell}
                        onChange={(e) => setCell(i, j, Number(e.target.value))}
                        disabled={i === j}
                      />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <div className="flex gap-2">
        <Button onClick={submit}>Salvar mapa</Button>
        <Button variant="outline" onClick={onCancel}>
          Cancelar
        </Button>
      </div>
    </div>
  );
}
