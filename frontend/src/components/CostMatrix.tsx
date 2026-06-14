import { useState } from "react";

interface Props {
  labels: string[];
  matrix: number[][];
  onHover?: (cell: { i: number; j: number } | null) => void;
}

export function CostMatrix({ labels, matrix, onHover }: Props) {
  const max = Math.max(1, ...matrix.flat());
  const [hover, setHover] = useState<{ i: number; j: number } | null>(null);

  const enter = (i: number, j: number) => {
    setHover({ i, j });
    onHover?.({ i, j });
  };
  const leave = () => {
    setHover(null);
    onHover?.(null);
  };

  return (
    <div className="overflow-auto">
      <table className="border-collapse text-xs" onMouseLeave={leave}>
        <thead>
          <tr>
            <th className="p-1" />
            {labels.map((l, j) => (
              <th
                key={j}
                className={`p-1 text-center font-medium ${hover?.j === j ? "text-orange-600" : ""}`}
              >
                {l}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {matrix.map((row, i) => (
            <tr key={i}>
              <th
                className={`p-1 text-left font-medium whitespace-nowrap ${hover?.i === i ? "text-orange-600" : ""}`}
              >
                {labels[i]}
              </th>
              {row.map((v, j) => {
                const active = hover?.i === i && hover?.j === j;
                return (
                  <td
                    key={j}
                    onMouseEnter={() => (i === j ? leave() : enter(i, j))}
                    className={`p-1 text-center font-mono ${i === j ? "" : "cursor-pointer"}`}
                    style={{
                      background: `hsl(142 71% ${95 - (v / max) * 45}%)`,
                      outline: active ? "2px solid hsl(25 95% 53%)" : undefined,
                      outlineOffset: "-2px",
                    }}
                  >
                    {v}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
