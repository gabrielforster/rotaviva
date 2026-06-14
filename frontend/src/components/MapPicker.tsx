import type { MapSummary } from "@/types";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";

interface Props {
  maps: MapSummary[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
  onOpenEditor: () => void;
}

export function MapPicker({ maps, selectedId, onSelect, onDelete, onOpenEditor }: Props) {
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
          <option value="" disabled>Escolha um mapa…</option>
          {maps.map((m) => (
            <option key={m.id} value={m.id}>
              {m.name} ({m.point_count} pontos · {m.source})
            </option>
          ))}
        </select>
      </div>

      {selected && selected.source !== "preset" && (
        <Button variant="destructive" size="sm" onClick={() => onDelete(selected.id)}>
          Excluir mapa
        </Button>
      )}

      <Button variant="outline" size="sm" className="w-full" onClick={onOpenEditor}>
        Novo mapa…
      </Button>
    </div>
  );
}
