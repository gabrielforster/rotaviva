import type { MapModel, OptimizeResponse } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CostMatrix } from "./CostMatrix";
import { api } from "@/lib/api";

interface Props {
  map: MapModel;
  result: OptimizeResponse;
  onHover?: (h: { fromId: string; toId: string; cost: number } | null) => void;
}

function Row({ name, value }: { name: string; value: number }) {
  return (
    <div className="flex justify-between">
      <span>{name}</span>
      <span className="font-mono">{value.toFixed(2)}</span>
    </div>
  );
}

export function ResultsPanel({ map, result, onHover }: Props) {
  const labelOf = (id: string) => map.points.find((p) => p.id === id)?.label ?? id;
  const { baselines } = result;
  const improvement =
    baselines.random_cost > 0
      ? (1 - result.total_cost / baselines.random_cost) * 100
      : 0;

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Rota otimizada</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="text-sm">{result.tour.map(labelOf).join(" → ")}</p>
          <p className="text-2xl font-semibold">
            Custo total: {result.total_cost.toFixed(2)}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Matriz de custos</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <CostMatrix
            labels={result.stop_labels}
            matrix={result.matrix}
            onHover={(cell) =>
              onHover?.(
                cell
                  ? {
                      fromId: result.stop_order[cell.i],
                      toId: result.stop_order[cell.j],
                      cost: result.matrix[cell.i][cell.j],
                    }
                  : null,
              )
            }
          />
          <p className="text-xs text-muted-foreground">
            Passe o mouse sobre uma célula para ver o trajeto e o custo no mapa.
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Comparação</CardTitle>
        </CardHeader>
        <CardContent className="space-y-1 text-sm">
          <Row name="Agente (Hill Climbing)" value={result.total_cost} />
          <Row name="Rota aleatória" value={baselines.random_cost} />
          {result.brute_force_skipped || baselines.brute_force_cost === null ? (
            <p className="text-muted-foreground">Força bruta: ignorada (muitas paradas)</p>
          ) : (
            <Row name="Força bruta (ótimo)" value={baselines.brute_force_cost} />
          )}
          <p
            className={`pt-2 font-medium ${improvement >= 0 ? "text-green-600" : "text-red-600"}`}
          >
            {Math.abs(improvement).toFixed(1)}% {improvement >= 0 ? "melhor" : "pior"} que a
            rota aleatória
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Gráficos</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <img
            src={api.routeChartUrl(result.run_id)}
            alt="Rota otimizada"
            className="w-full rounded-md border"
          />
          <img
            src={api.routeCostsChartUrl(result.run_id)}
            alt="Custos por trecho"
            className="w-full rounded-md border"
          />
          <img
            src={api.evolutionChartUrl(result.run_id)}
            alt="Evolução do custo"
            className="w-full rounded-md border"
          />
        </CardContent>
      </Card>
    </div>
  );
}
