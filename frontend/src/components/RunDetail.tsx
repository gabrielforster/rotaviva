import { useEffect, useState } from "react";
import type { RunDetail as RunDetailModel } from "@/types";
import { api } from "@/lib/api";
import { CostMatrix } from "./CostMatrix";

export function RunDetail({ id }: { id: number }) {
  const [run, setRun] = useState<RunDetailModel | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setRun(null);
    setError(null);
    api.getRun(id).then(setRun).catch((e) => setError(String(e)));
  }, [id]);

  if (error) return <p className="text-sm text-red-600">{error}</p>;
  if (!run) return <p className="text-sm text-muted-foreground">Carregando…</p>;

  const labelOf = (id: string) => {
    const i = run.stop_order.indexOf(id);
    return i >= 0 ? run.stop_labels[i] : id;
  };

  return (
    <div className="space-y-4">
      <div className="text-sm">
        <p>
          <span className="font-medium">{run.map_name}</span> · custo{" "}
          <span className="font-mono">{run.total_cost.toFixed(2)}</span> ·{" "}
          {run.restarts} reinícios
        </p>
        <p className="text-muted-foreground">{run.tour.map(labelOf).join(" → ")}</p>
      </div>
      <CostMatrix labels={run.stop_labels} matrix={run.matrix} />
      <img
        src={api.routeChartUrl(run.id)}
        alt="Rota otimizada"
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
