import { useMemo } from "react";
import type { MapModel } from "@/types";
import { bfsPath, cellCenter } from "@/lib/grid";
import { SPRITE_EMOJI } from "@/lib/sprites";

const THEME = {
  city: { surface: "#eef2f7", block: "#c8cfda", blockStroke: "#aab2c0" },
  warehouse: { surface: "#efece5", block: "#b08968", blockStroke: "#8a6d52" },
} as const;

interface Props {
  map: MapModel;
  selected: Set<string>;
  startId: string | null;
  tour: string[] | null;
  onToggle: (id: string) => void;
}

export function MapCanvas({ map, selected, startId, tour, onToggle }: Props) {
  const { grid, points, style } = map;
  const theme = THEME[style] ?? THEME.city;
  const s = grid.cell_size;
  const rows = grid.cells.length;
  const cols = grid.cells[0]?.length ?? 0;

  const byId = useMemo(() => new Map(points.map((p) => [p.id, p])), [points]);

  const order = useMemo(() => {
    const m = new Map<string, number>();
    if (tour) tour.slice(0, -1).forEach((id, i) => m.set(id, i + 1));
    return m;
  }, [tour]);

  // Trace the street path between consecutive stops into one polyline, and drop
  // direction chevrons along it so the travel direction is easy to follow.
  const route = useMemo(() => {
    const empty = { line: "", arrows: [] as { x: number; y: number; angle: number }[] };
    if (!tour || tour.length < 2) return empty;
    const pts: [number, number][] = [];
    for (let i = 0; i < tour.length - 1; i++) {
      const from = byId.get(tour[i])?.cell;
      const to = byId.get(tour[i + 1])?.cell;
      if (!from || !to) continue;
      const path = bfsPath(grid, from, to);
      if (!path) continue;
      const leg = i === 0 ? path : path.slice(1); // avoid duplicating shared endpoint
      for (const cell of leg) pts.push(cellCenter(grid, cell));
    }
    const line = pts.map(([x, y]) => `${x},${y}`).join(" ");
    // One chevron every couple of cells, oriented along the local travel direction.
    const arrows: { x: number; y: number; angle: number }[] = [];
    const step = 2;
    for (let i = step; i < pts.length; i += step) {
      const [x0, y0] = pts[i - 1];
      const [x1, y1] = pts[i];
      arrows.push({
        x: (x0 + x1) / 2,
        y: (y0 + y1) / 2,
        angle: (Math.atan2(y1 - y0, x1 - x0) * 180) / Math.PI,
      });
    }
    return { line, arrows };
  }, [tour, grid, byId]);

  if (cols === 0) return <div className="h-full w-full rounded-lg border bg-card" />;

  return (
    <svg
      viewBox={`0 0 ${cols * s} ${rows * s}`}
      className="h-full w-full rounded-lg border"
      style={{ background: theme.surface }}
      role="img"
      aria-label={`Mapa ${map.name}`}
    >
      {grid.cells.flatMap((row, r) =>
        row.split("").map((ch, c) =>
          ch === "#" ? (
            <rect
              key={`${r}-${c}`}
              x={c * s + 1}
              y={r * s + 1}
              width={s - 2}
              height={s - 2}
              rx={style === "city" ? 2 : 0}
              fill={theme.block}
              stroke={theme.blockStroke}
              strokeWidth={1}
            />
          ) : null,
        ),
      )}

      {route.line && (
        <polyline
          points={route.line}
          fill="none"
          stroke="hsl(142 71% 45%)"
          strokeWidth={4}
          strokeLinejoin="round"
          strokeLinecap="round"
        />
      )}

      {/* Direction chevrons (">") pointing the way the route travels */}
      {route.arrows.map((a, i) => (
        <path
          key={i}
          d={`M ${-s * 0.12} ${-s * 0.13} L ${s * 0.11} 0 L ${-s * 0.12} ${s * 0.13}`}
          fill="none"
          stroke="white"
          strokeWidth={2.4}
          strokeLinecap="round"
          strokeLinejoin="round"
          transform={`translate(${a.x} ${a.y}) rotate(${a.angle})`}
        />
      ))}

      {points.map((p) => {
        const [x, y] = cellCenter(grid, p.cell);
        const isSel = selected.has(p.id);
        const isStart = startId === p.id;
        return (
          <g key={p.id} className="cursor-pointer" onClick={() => onToggle(p.id)}>
            <circle
              cx={x}
              cy={y}
              r={s * 0.42}
              fill={isStart ? "hsl(43 96% 56%)" : isSel ? "hsl(217 91% 60%)" : "white"}
              stroke={isSel || isStart ? "hsl(222 47% 11%)" : "hsl(215 16% 47%)"}
              strokeWidth={isSel || isStart ? 3 : 1.5}
            />
            <text x={x} y={y + s * 0.14} textAnchor="middle" fontSize={s * 0.4}>
              {SPRITE_EMOJI[p.sprite] ?? "📍"}
            </text>
            {order.has(p.id) && (
              <>
                <circle
                  cx={x + s * 0.3}
                  cy={y - s * 0.3}
                  r={s * 0.2}
                  fill="hsl(222 47% 11%)"
                  stroke="white"
                  strokeWidth={1.5}
                />
                <text
                  x={x + s * 0.3}
                  y={y - s * 0.3 + s * 0.09}
                  textAnchor="middle"
                  fontSize={s * 0.26}
                  fontWeight="bold"
                  fill="white"
                >
                  {order.get(p.id)}
                </text>
              </>
            )}
          </g>
        );
      })}
    </svg>
  );
}
