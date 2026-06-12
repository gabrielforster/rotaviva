import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface Props {
  history: number[];
}

export function ConvergenceChart({ history }: Props) {
  const data = history.map((cost, i) => ({
    restart: i + 1,
    cost: Number(cost.toFixed(2)),
  }));

  return (
    <div className="h-56 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 16, bottom: 16, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="restart"
            label={{ value: "reinício", position: "insideBottom", offset: -8 }}
          />
          <YAxis />
          <Tooltip />
          <Line
            type="stepAfter"
            dataKey="cost"
            stroke="hsl(142 71% 45%)"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
