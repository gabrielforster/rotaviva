import type { MapModel } from "@/types";

const SPRITE_EMOJI: Record<string, string> = {
  shop: "🛒",
  home: "🏠",
  factory: "🏭",
  park: "🌳",
  school: "🏫",
  hospital: "🏥",
  pin: "📍",
};

interface Props {
  map: MapModel;
  selected: Set<string>;
  startId: string | null;
  tour: string[] | null;
  onToggle: (id: string) => void;
}

export function MapCanvas({ map, selected, startId, tour, onToggle }: Props) {
  if (map.points.length === 0) {
    return <div className="h-full w-full rounded-lg border bg-card" />;
  }
  const xs = map.points.map((p) => p.x);
  const ys = map.points.map((p) => p.y);
  const pad = 48;
  const minX = Math.min(...xs) - pad;
  const minY = Math.min(...ys) - pad;
  const width = Math.max(...xs) - Math.min(...xs) + pad * 2;
  const height = Math.max(...ys) - Math.min(...ys) + pad * 2;

  const byId = new Map(map.points.map((p) => [p.id, p]));
  const routePoints = tour
    ? tour
        .map((id) => byId.get(id))
        .filter((p): p is NonNullable<typeof p> => Boolean(p))
        .map((p) => `${p.x},${p.y}`)
        .join(" ")
    : "";

  return (
    <svg
      viewBox={`${minX} ${minY} ${width} ${height}`}
      className="h-full w-full rounded-lg border bg-card"
      role="img"
      aria-label={`Mapa ${map.name}`}
    >
      {tour && (
        <polyline
          points={routePoints}
          fill="none"
          stroke="hsl(142 71% 45%)"
          strokeWidth={3}
          strokeLinejoin="round"
        />
      )}
      {map.points.map((p) => {
        const isSel = selected.has(p.id);
        const isStart = startId === p.id;
        return (
          <g
            key={p.id}
            className="cursor-pointer"
            onClick={() => onToggle(p.id)}
          >
            <circle
              cx={p.x}
              cy={p.y}
              r={16}
              fill={isStart ? "hsl(142 71% 45%)" : isSel ? "hsl(217 91% 60%)" : "white"}
              stroke={isSel || isStart ? "hsl(222 47% 11%)" : "hsl(215 16% 47%)"}
              strokeWidth={isSel || isStart ? 3 : 1.5}
            />
            <text x={p.x} y={p.y + 5} textAnchor="middle" fontSize={16}>
              {SPRITE_EMOJI[p.sprite] ?? "📍"}
            </text>
            <text
              x={p.x}
              y={p.y + 34}
              textAnchor="middle"
              fontSize={11}
              fill="hsl(215 16% 35%)"
            >
              {p.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
