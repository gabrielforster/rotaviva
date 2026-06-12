import type { MapModel } from "@/types";
import { Button } from "@/components/ui/button";

interface Props {
  map: MapModel;
  selected: string[];
  startId: string | null;
  onSetStart: (id: string) => void;
  onRemove: (id: string) => void;
}

export function StopList({ map, selected, startId, onSetStart, onRemove }: Props) {
  const labelOf = (id: string) =>
    map.points.find((p) => p.id === id)?.label ?? id;

  if (selected.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        Clique nos pontos do mapa para adicioná-los como paradas.
      </p>
    );
  }

  return (
    <ul className="space-y-2">
      {selected.map((id) => (
        <li
          key={id}
          className="flex items-center justify-between gap-2 rounded-md border px-3 py-2"
        >
          <label className="flex items-center gap-2 text-sm">
            <input
              type="radio"
              name="start"
              checked={startId === id}
              onChange={() => onSetStart(id)}
            />
            <span>{labelOf(id)}</span>
            {startId === id && (
              <span className="text-xs font-medium text-green-600">início</span>
            )}
          </label>
          <Button variant="ghost" size="sm" onClick={() => onRemove(id)}>
            Remover
          </Button>
        </li>
      ))}
    </ul>
  );
}
