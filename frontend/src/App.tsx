import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type {
  CreateMapRequest,
  MapModel,
  MapStyle,
  MapSummary,
  OptimizeResponse,
} from "@/types";
import { MapPicker } from "@/components/MapPicker";
import type { GenerateOpts } from "@/components/MapPicker";
import { MapCanvas } from "@/components/MapCanvas";
import { StopList } from "@/components/StopList";
import { ResultsPanel } from "@/components/ResultsPanel";
import { GridPainter } from "@/components/GridPainter";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function App() {
  const [maps, setMaps] = useState<MapSummary[]>([]);
  const [map, setMap] = useState<MapModel | null>(null);
  const [stops, setStops] = useState<string[]>([]);
  const [startId, setStartId] = useState<string | null>(null);
  const [result, setResult] = useState<OptimizeResponse | null>(null);
  const [editing, setEditing] = useState(false);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const reloadMaps = () => api.listMaps().then(setMaps);

  useEffect(() => {
    reloadMaps().catch((e) => setError(String(e)));
  }, []);

  const selectMapModel = (m: MapModel) => {
    setMap(m);
    setStops([]);
    setStartId(null);
    setResult(null);
    setEditing(false);
  };

  const handleSelect = async (id: string) => {
    if (!id) return;
    setError(null);
    try {
      selectMapModel(await api.getMap(id));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  };

  const handleGenerate = async (opts: GenerateOpts) => {
    setError(null);
    const realSeed = opts.seed ?? Math.floor(Math.random() * 1e9);
    const genId = `gerado-${opts.style}-${opts.n}-${realSeed}`;
    const styleLabel: Record<MapStyle, string> = { city: "Cidade", warehouse: "Galpão" };
    try {
      const generated = await api.generateMap({
        ...opts,
        seed: realSeed,
        save: true,
        id: genId,
        name: `${styleLabel[opts.style]} ${opts.n}p (seed ${realSeed})`,
      });
      await reloadMaps();
      selectMapModel(generated);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  };

  const handleDelete = async (id: string) => {
    setError(null);
    try {
      await api.deleteMap(id);
      await reloadMaps();
      if (map?.id === id) {
        setMap(null);
        setStops([]);
        setStartId(null);
        setResult(null);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  };

  const toggleStop = (id: string) => {
    setResult(null);
    if (stops.includes(id)) {
      const next = stops.filter((s) => s !== id);
      setStops(next);
      if (startId === id) setStartId(next[0] ?? null);
    } else {
      setStops([...stops, id]);
      if (startId === null) setStartId(id);
    }
  };

  const runOptimize = async () => {
    if (!map || !startId || stops.length < 2) return;
    setRunning(true);
    setError(null);
    try {
      const res = await api.optimize({
        map_id: map.id,
        stop_ids: stops,
        start_id: startId,
      });
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setRunning(false);
    }
  };

  const saveMap = async (body: CreateMapRequest) => {
    await api.createMap(body);
    await reloadMaps();
    selectMapModel(await api.getMap(body.id));
  };

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-6">
      <header className="space-y-1">
        <h1 className="text-3xl font-bold text-green-700">RotaViva</h1>
        <p className="text-sm text-muted-foreground">
          Otimização de rotas com Hill Climbing + Random Restart
        </p>
      </header>

      {error && (
        <div className="rounded-md border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[320px_1fr]">
        <aside className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>{editing ? "Novo mapa" : "Mapa"}</CardTitle>
            </CardHeader>
            <CardContent>
              {editing ? (
                <GridPainter onCancel={() => setEditing(false)} onSave={saveMap} />
              ) : (
                <MapPicker
                  maps={maps}
                  selectedId={map?.id ?? null}
                  onSelect={handleSelect}
                  onGenerate={handleGenerate}
                  onDelete={handleDelete}
                  onOpenEditor={() => setEditing(true)}
                />
              )}
            </CardContent>
          </Card>

          {map && !editing && (
            <Card>
              <CardHeader>
                <CardTitle>Paradas</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <StopList
                  map={map}
                  selected={stops}
                  startId={startId}
                  onSetStart={setStartId}
                  onRemove={toggleStop}
                />
                <Button
                  className="w-full"
                  disabled={running || stops.length < 2 || !startId}
                  onClick={runOptimize}
                >
                  {running ? "Otimizando…" : "Otimizar rota"}
                </Button>
              </CardContent>
            </Card>
          )}
        </aside>

        <main className="space-y-6">
          {map && !editing ? (
            <>
              <div className="h-[480px]">
                <MapCanvas
                  map={map}
                  selected={new Set(stops)}
                  startId={startId}
                  tour={result?.tour ?? null}
                  onToggle={toggleStop}
                />
              </div>
              {result && <ResultsPanel map={map} result={result} />}
            </>
          ) : (
            <p className="text-sm text-muted-foreground">
              Selecione, gere ou registre um mapa para começar.
            </p>
          )}
        </main>
      </div>
    </div>
  );
}
