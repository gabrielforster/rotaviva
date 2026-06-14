import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type {
  CreateMapRequest,
  MapModel,
  MapStyle,
  MapSummary,
  OptimizeResponse,
  RunSummary,
} from "@/types";
import { MapPicker } from "@/components/MapPicker";
import { MapGenerator } from "@/components/MapGenerator";
import type { GenerateOpts } from "@/components/MapGenerator";
import { MapCanvas } from "@/components/MapCanvas";
import { StopList } from "@/components/StopList";
import { ResultsPanel } from "@/components/ResultsPanel";
import { GridPainter } from "@/components/GridPainter";
import { MapLegend } from "@/components/MapLegend";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { RunsList } from "@/components/RunsList";
import { RunDetail } from "@/components/RunDetail";

export default function App() {
  const [maps, setMaps] = useState<MapSummary[]>([]);
  const [map, setMap] = useState<MapModel | null>(null);
  const [stops, setStops] = useState<string[]>([]);
  const [startId, setStartId] = useState<string | null>(null);
  const [result, setResult] = useState<OptimizeResponse | null>(null);
  const [editing, setEditing] = useState(false);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [openRunId, setOpenRunId] = useState<number | null>(null);
  const [createMode, setCreateMode] = useState<"generate" | "paint">("generate");
  const [highlight, setHighlight] = useState<
    { fromId: string; toId: string; cost: number } | null
  >(null);

  const reloadMaps = () => api.listMaps().then(setMaps);
  const reloadRuns = () => api.listRuns().then(setRuns);

  useEffect(() => {
    reloadMaps().catch((e) => setError(String(e)));
    reloadRuns().catch((e) => setError(String(e)));
  }, []);

  const selectMapModel = (m: MapModel) => {
    setMap(m);
    setStops([]);
    setStartId(null);
    setResult(null);
    setHighlight(null);
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
    setHighlight(null);
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
      await reloadRuns();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setRunning(false);
    }
  };

  const handleDeleteRun = async (id: number) => {
    try {
      await api.deleteRun(id);
      if (openRunId === id) setOpenRunId(null);
      await reloadRuns();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  };

  const saveMap = async (body: CreateMapRequest) => {
    await api.createMap(body);
    await reloadMaps();
    selectMapModel(await api.getMap(body.id));
    setEditing(false);
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
              <CardTitle>Mapa</CardTitle>
            </CardHeader>
            <CardContent>
              <MapPicker
                maps={maps}
                selectedId={map?.id ?? null}
                onSelect={handleSelect}
                onDelete={handleDelete}
                onOpenEditor={() => setEditing(true)}
              />
            </CardContent>
          </Card>

          {map && (
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

          <Card>
            <CardHeader>
              <CardTitle>Histórico</CardTitle>
            </CardHeader>
            <CardContent>
              <RunsList runs={runs} onOpen={setOpenRunId} onDelete={handleDeleteRun} />
            </CardContent>
          </Card>
        </aside>

        <main className="space-y-6">
          {map ? (
            <>
              <div className="grid gap-4 lg:grid-cols-[1fr_210px]">
                <div className="h-[480px]">
                  <MapCanvas
                    map={map}
                    selected={new Set(stops)}
                    startId={startId}
                    tour={result?.tour ?? null}
                    onToggle={toggleStop}
                    highlight={highlight}
                  />
                </div>
                <MapLegend map={map} />
              </div>
              {result && <ResultsPanel map={map} result={result} onHover={setHighlight} />}
            </>
          ) : (
            <p className="text-sm text-muted-foreground">
              Selecione, gere ou registre um mapa para começar.
            </p>
          )}
        </main>
      </div>

      <Dialog open={editing} onOpenChange={setEditing}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Novo mapa</DialogTitle>
          </DialogHeader>
          <div className="flex gap-2">
            <Button
              size="sm"
              variant={createMode === "generate" ? "default" : "outline"}
              onClick={() => setCreateMode("generate")}
            >
              Gerar
            </Button>
            <Button
              size="sm"
              variant={createMode === "paint" ? "default" : "outline"}
              onClick={() => setCreateMode("paint")}
            >
              Pintar
            </Button>
          </div>
          {createMode === "generate" ? (
            <MapGenerator onGenerate={handleGenerate} />
          ) : (
            <GridPainter onCancel={() => setEditing(false)} onSave={saveMap} />
          )}
        </DialogContent>
      </Dialog>

      <Dialog open={openRunId !== null} onOpenChange={(o) => !o && setOpenRunId(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Otimização #{openRunId}</DialogTitle>
          </DialogHeader>
          {openRunId !== null && <RunDetail id={openRunId} />}
        </DialogContent>
      </Dialog>
    </div>
  );
}
