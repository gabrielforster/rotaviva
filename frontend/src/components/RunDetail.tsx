import { useEffect, useState } from "react";
import type { RunDetail as RunDetailModel } from "@/types";
import { api } from "@/lib/api";
import { CostMatrix } from "./CostMatrix";
import { MapCanvas } from "./MapCanvas";

export function RunDetail({ id }: { id: number }) {
  const [run, setRun] = useState<RunDetailModel | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [highlight, setHighlight] = useState<
    { fromId: string; toId: string; cost: number } | null
  >(null);

  useEffect(() => {
    setRun(null);
    setError(null);
    setHighlight(null);
    api.getRun(id).then(setRun).catch((e) => setError(String(e)));
  }, [id]);

  if (error) return <p className="text-sm text-red-600">{error}</p>;
  if (!run) return <p className="text-sm text-muted-foreground">Carregando…</p>;

  const labelOf = (pid: string) => {
    const i = run.stop_order.indexOf(pid);
    return i >= 0 ? run.stop_labels[i] : pid;
  };

  return (
    <div className="space-y-4">
      <div className="h-[340px]">
        <MapCanvas
          map={run.map}
          selected={new Set(run.stop_order)}
          startId={run.start_id}
          tour={run.tour}
          onToggle={() => {}}
          highlight={highlight}
        />
      </div>

      <div className="text-sm">
        <p>
          <span className="font-medium">{run.map_name}</span> · custo{" "}
          <span className="font-mono">{run.total_cost.toFixed(2)}</span> ·{" "}
          {run.restarts} reinícios
        </p>
        <p className="text-muted-foreground">{run.tour.map(labelOf).join(" → ")}</p>
      </div>

      <div className="space-y-2">
        <CostMatrix
          labels={run.stop_labels}
          matrix={run.matrix}
          onHover={(cell) =>
            setHighlight(
              cell
                ? {
                    fromId: run.stop_order[cell.i],
                    toId: run.stop_order[cell.j],
                    cost: run.matrix[cell.i][cell.j],
                  }
                : null,
            )
          }
        />
        <p className="text-xs text-muted-foreground">
          Passe o mouse sobre uma célula para ver o trajeto e o custo no mapa.
        </p>
      </div>

      <img
        src={api.routeChartUrl(run.id)}
        alt="Rota otimizada"
        className="w-full rounded-md border"
      />
      <img
        src={api.routeCostsChartUrl(run.id)}
        alt="Custos por trecho"
        className="w-full rounded-md border"
      />
      <img
        src={api.evolutionChartUrl(run.id)}
        alt="Evolução do custo"
        className="w-full rounded-md border"
      />
    </div>
  );
}
