import {
  Area,
  CartesianGrid,
  ComposedChart,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { meanRuns, rollingAverageRuns } from "@/lib/stats";

/** @param {{ innings: object[] }} props */
export function RunsTrendChart({ innings }) {
  const careerAvg = meanRuns(innings);
  const roll10 = rollingAverageRuns(innings, 10);

  const data = innings.map((row, i) => ({
    label: `#${row.index}`,
    runs: row.runs,
    roll10: Math.round(roll10[i] * 10) / 10,
    out: row.out,
  }));

  return (
    <div className="h-[320px] w-full min-w-0">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="runsFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--chart-runs)" stopOpacity={0.35} />
              <stop offset="100%" stopColor="var(--chart-runs)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="var(--chart-grid)" strokeDasharray="3 6" vertical={false} />
          <XAxis
            dataKey="label"
            tick={{ fill: "var(--muted)", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            interval="preserveStartEnd"
          />
          <YAxis
            tick={{ fill: "var(--muted)", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            width={36}
          />
          <Tooltip
            contentStyle={{
              background: "var(--surface-elevated)",
              border: "1px solid var(--border)",
              borderRadius: "10px",
              color: "var(--foreground)",
            }}
            labelStyle={{ color: "var(--muted)" }}
            formatter={(value, name) => {
              const v = value ?? "—";
              if (name === "runs") return [v, "Runs"];
              if (name === "roll10") return [v, "10-inn. avg"];
              return [v, String(name)];
            }}
          />
          <ReferenceLine
            y={careerAvg}
            stroke="var(--accent)"
            strokeDasharray="4 4"
            label={{
              value: `Career avg ${careerAvg.toFixed(1)}`,
              fill: "var(--accent)",
              fontSize: 11,
              position: "insideTopRight",
            }}
          />
          <Area type="monotone" dataKey="runs" stroke="none" fill="url(#runsFill)" />
          <Line
            type="monotone"
            dataKey="runs"
            stroke="var(--chart-runs)"
            strokeWidth={2}
            dot={{ r: 3, fill: "var(--chart-runs)", strokeWidth: 0 }}
            activeDot={{ r: 5 }}
          />
          <Line
            type="monotone"
            dataKey="roll10"
            stroke="var(--chart-roll)"
            strokeWidth={2}
            dot={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
