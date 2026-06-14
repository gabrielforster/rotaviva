import type * as React from "react";
import type { MapModel } from "@/types";
import { SPRITE_EMOJI, SPRITE_LABELS } from "@/lib/sprites";

function Row({ swatch, label }: { swatch: React.ReactNode; label: string }) {
  return (
    <li className="flex items-center gap-2">
      <span className="flex w-5 justify-center">{swatch}</span>
      <span className="text-muted-foreground">{label}</span>
    </li>
  );
}

export function MapLegend({ map }: { map: MapModel }) {
  const sprites = Array.from(new Set(map.points.map((p) => p.sprite)));
  return (
    <div className="space-y-3 rounded-lg border bg-card p-3 text-sm">
      <p className="font-medium">Legenda</p>
      <ul className="space-y-1">
        {sprites.map((s) => (
          <Row
            key={s}
            swatch={<span className="text-base">{SPRITE_EMOJI[s] ?? "📍"}</span>}
            label={SPRITE_LABELS[s] ?? s}
          />
        ))}
      </ul>
      <ul className="space-y-1 border-t pt-2">
        <Row
          swatch={
            <span
              className="inline-block h-3 w-3 rounded-full"
              style={{ background: "hsl(43 96% 56%)" }}
            />
          }
          label="Ponto de partida"
        />
        <Row
          swatch={
            <span
              className="inline-block h-3 w-3 rounded-full"
              style={{ background: "hsl(217 91% 60%)" }}
            />
          }
          label="Parada selecionada"
        />
        <Row
          swatch={
            <span
              className="inline-block h-1 w-4 rounded"
              style={{ background: "hsl(142 71% 45%)" }}
            />
          }
          label="Rota otimizada"
        />
        <Row
          swatch={
            <span className="flex h-4 w-4 items-center justify-center rounded-full bg-slate-900 text-[9px] font-bold text-white">
              1
            </span>
          }
          label="Ordem de visita"
        />
      </ul>
    </div>
  );
}
