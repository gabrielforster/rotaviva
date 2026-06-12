import { useState } from "react";
import type { MapSummary } from "@/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface Props {
  maps: MapSummary[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onGenerate: (n: number, seed: number | undefined) => void;
  onDelete: (id: string) => void;
  onOpenEditor: () => void;
}

export function MapPicker({
  maps,
  selectedId,
  onSelect,
  onGenerate,
  onDelete,
  onOpenEditor,
}: Props) {
  const [n, setN] = useState(6);
  const [seed, setSeed] = useState("");
  const selected = maps.find((m) => m.id === selectedId);

  return (
    <div className="space-y-4">
      <div className="space-y-1">
        <Label htmlFor="map-select">Mapa</Label>
        <select
          id="map-select"
          className="flex h-9 w-full rounded-md border bg-transparent px-3 py-1 text-sm shadow-sm"
          value={selectedId ?? ""}
          onChange={(e) => onSelect(e.target.value)}
        >
          <option value="" disabled>
            Escolha um mapa…
          </option>
          {maps.map((m) => (
            <option key={m.id} value={m.id}>
              {m.name} ({m.point_count} pontos · {m.source})
            </option>
          ))}
        </select>
      </div>

      {selected && selected.source !== "preset" && (
        <Button
          variant="destructive"
          size="sm"
          onClick={() => onDelete(selected.id)}
        >
          Excluir mapa
        </Button>
      )}

      <div className="space-y-2 rounded-md border p-3">
        <p className="text-sm font-medium">Gerar mapa aleatório</p>
        <div className="flex items-end gap-2">
          <div className="space-y-1">
            <Label htmlFor="gen-n">Pontos</Label>
            <Input
              id="gen-n"
              type="number"
              min={2}
              max={50}
              value={n}
              onChange={(e) => setN(Number(e.target.value))}
              className="w-20"
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="gen-seed">Seed</Label>
            <Input
              id="gen-seed"
              value={seed}
              onChange={(e) => setSeed(e.target.value)}
              placeholder="opcional"
              className="w-24"
            />
          </div>
          <Button
            size="sm"
            onClick={() => onGenerate(n, seed === "" ? undefined : Number(seed))}
          >
            Gerar
          </Button>
        </div>
      </div>

      <Button variant="outline" size="sm" onClick={onOpenEditor}>
        Registrar novo mapa…
      </Button>
    </div>
  );
}
