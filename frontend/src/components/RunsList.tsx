import type { RunSummary } from "@/types";
import { Button } from "@/components/ui/button";

interface Props {
  runs: RunSummary[];
  onOpen: (id: number) => void;
  onDelete: (id: number) => void;
}

export function RunsList({ runs, onOpen, onDelete }: Props) {
  if (runs.length === 0)
    return <p className="text-sm text-muted-foreground">Nenhuma otimização ainda.</p>;
  return (
    <ul className="space-y-2">
      {runs.map((r) => (
        <li key={r.id} className="flex items-center justify-between gap-2 text-sm">
          <button
            className="flex-1 text-left hover:underline"
            onClick={() => onOpen(r.id)}
          >
            <span className="font-medium">#{r.id}</span> · {r.map_name} ·{" "}
            <span className="font-mono">{r.total_cost.toFixed(0)}</span>
            <span className="text-muted-foreground"> ({r.stop_count} paradas)</span>
          </button>
          <Button size="sm" variant="ghost" onClick={() => onDelete(r.id)}>
            ✕
          </Button>
        </li>
      ))}
    </ul>
  );
}
