import type { MapModel } from "@/types";
import { cellCenter } from "@/lib/grid";

const SPRITE_EMOJI: Record<string, string> = {
  shop: "🛒",
  home: "🏠",
  factory: "🏭",
  park: "🌳",
  school: "🏫",
  hospital: "🏥",
  pin: "📍",
};

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

export function MapCanvas({ map, selected, startId, onToggle }: Props) {
  const { grid, points, style } = map;
  const theme = THEME[style] ?? THEME.city;
  const s = grid.cell_size;
  const rows = grid.cells.length;
  const cols = grid.cells[0]?.length ?? 0;

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
              fill={isStart ? "hsl(142 71% 45%)" : isSel ? "hsl(217 91% 60%)" : "white"}
              stroke={isSel || isStart ? "hsl(222 47% 11%)" : "hsl(215 16% 47%)"}
              strokeWidth={isSel || isStart ? 3 : 1.5}
            />
            <text x={x} y={y + s * 0.14} textAnchor="middle" fontSize={s * 0.4}>
              {SPRITE_EMOJI[p.sprite] ?? "📍"}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
