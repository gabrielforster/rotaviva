interface Props {
  labels: string[];
  matrix: number[][];
}

export function CostMatrix({ labels, matrix }: Props) {
  const max = Math.max(1, ...matrix.flat());
  return (
    <div className="overflow-auto">
      <table className="border-collapse text-xs">
        <thead>
          <tr>
            <th className="p-1" />
            {labels.map((l, i) => (
              <th key={i} className="p-1 text-center font-medium">
                {l}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {matrix.map((row, i) => (
            <tr key={i}>
              <th className="p-1 text-left font-medium whitespace-nowrap">{labels[i]}</th>
              {row.map((v, j) => (
                <td
                  key={j}
                  className="p-1 text-center font-mono"
                  style={{ background: `hsl(142 71% ${95 - (v / max) * 45}%)` }}
                >
                  {v}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
