import { useState } from "react";
import type { MapSize, MapStyle } from "@/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export interface GenerateOpts {
  style: MapStyle;
  size: MapSize;
  density: number;
  n: number;
  seed?: number;
}

interface Props {
  onGenerate: (opts: GenerateOpts) => void | Promise<void>;
}

export function MapGenerator({ onGenerate }: Props) {
  const [style, setStyle] = useState<MapStyle>("city");
  const [size, setSize] = useState<MapSize>("medium");
  const [density, setDensity] = useState(0.6);
  const [n, setN] = useState(6);
  const [seed, setSeed] = useState("");

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-2">
        <div className="space-y-1">
          <Label htmlFor="gen-style">Estilo</Label>
          <select
            id="gen-style"
            className="h-9 w-full rounded-md border px-2 text-sm"
            value={style}
            onChange={(e) => setStyle(e.target.value as MapStyle)}
          >
            <option value="city">Cidade</option>
            <option value="warehouse">Galpão</option>
          </select>
        </div>
        <div className="space-y-1">
          <Label htmlFor="gen-size">Tamanho</Label>
          <select
            id="gen-size"
            className="h-9 w-full rounded-md border px-2 text-sm"
            value={size}
            onChange={(e) => setSize(e.target.value as MapSize)}
          >
            <option value="small">Pequeno</option>
            <option value="medium">Médio</option>
            <option value="large">Grande</option>
          </select>
        </div>
      </div>

      <div className="space-y-1">
        <Label htmlFor="gen-density">Densidade ({Math.round(density * 100)}%)</Label>
        <input
          id="gen-density"
          type="range"
          min={0}
          max={1}
          step={0.1}
          value={density}
          onChange={(e) => setDensity(Number(e.target.value))}
          className="w-full"
        />
      </div>

      <div className="flex items-end gap-2">
        <div className="space-y-1">
          <Label htmlFor="gen-n">Pontos</Label>
          <Input id="gen-n" type="number" min={2} max={50} value={n}
            onChange={(e) => setN(Number(e.target.value))} className="w-20" />
        </div>
        <div className="space-y-1">
          <Label htmlFor="gen-seed">Seed</Label>
          <Input id="gen-seed" value={seed} onChange={(e) => setSeed(e.target.value)}
            placeholder="opcional" className="w-24" />
        </div>
        <Button
          onClick={() =>
            onGenerate({ style, size, density, n, seed: seed === "" ? undefined : Number(seed) })
          }
        >
          Gerar mapa
        </Button>
      </div>
    </div>
  );
}
