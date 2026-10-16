import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { Key } from "./i18n";
import type { ReactNode } from "react";

export function Section({
  id,
  number,
  title,
  children,
}: {
  id: string;
  number: string;
  title: string;
  children: ReactNode;
}) {
  return (
    <section id={id} className="section">
      <div className="section-heading">
        <span className="section-number">{number}</span>
        <h2>{title}</h2>
      </div>
      {children}
    </section>
  );
}

export type ChartRow = Record<string, string | number | null>;
type Series = { key: string; label: string; color: string };

export function Chart({
  rows,
  x,
  series,
  kind = "line",
  xLabel,
  yLabel,
  domain,
}: {
  rows: ChartRow[];
  x: string;
  series: Series[];
  kind?: "line" | "bar";
  xLabel: string;
  yLabel: string;
  domain?: [number, number];
}) {
  const content = (
    <>
      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#dfe9e6" />
      <XAxis
        dataKey={x}
        type={kind === "line" ? "number" : "category"}
        domain={kind === "line" ? [0, 1] : undefined}
        tickFormatter={(value) =>
          typeof value === "number"
            ? value.toLocaleString(document.documentElement.lang, {
                maximumFractionDigits: 2,
              })
            : value
        }
        tick={{ fontSize: 11 }}
        label={{ value: xLabel, position: "insideBottom", offset: -4 }}
        height={52}
      />
      <YAxis
        domain={domain}
        tick={{ fontSize: 11 }}
        label={{
          value: yLabel,
          angle: -90,
          position: "insideLeft",
          fontSize: 11,
        }}
      />
      <Tooltip
        formatter={(value) =>
          typeof value === "number"
            ? value.toLocaleString(document.documentElement.lang, {
                maximumFractionDigits: 3,
              })
            : value
        }
      />
      <Legend wrapperStyle={{ fontSize: 12 }} />
      {series.map((s) =>
        kind === "bar" ? (
          <Bar
            key={s.key}
            dataKey={s.key}
            name={s.label}
            fill={s.color}
            radius={[3, 3, 0, 0]}
          />
        ) : (
          <Line
            key={s.key}
            type="linear"
            dataKey={s.key}
            name={s.label}
            stroke={s.color}
            strokeWidth={2}
            dot={false}
          />
        ),
      )}
    </>
  );
  return (
    <div className="chart" role="img" aria-label={`${xLabel} / ${yLabel}`}>
      <ResponsiveContainer width="100%" height="100%">
        {kind === "bar" ? (
          <BarChart
            data={rows}
            margin={{ top: 12, right: 12, bottom: 12, left: 15 }}
          >
            {content}
          </BarChart>
        ) : (
          <LineChart
            data={rows}
            margin={{ top: 12, right: 12, bottom: 12, left: 15 }}
          >
            {content}
          </LineChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}

export function Contributions({
  values,
  t,
  unit,
}: {
  values: { feature: string; value: number; std?: number }[];
  t: (key: Key) => string;
  unit: string;
}) {
  const max = Math.max(...values.map((v) => Math.abs(v.value)), 0.001);
  return (
    <div className="contributions">
      <p className="caption">{unit}</p>
      {values.map((v) => (
        <div className="contribution" key={v.feature}>
          <span>{t(v.feature as Key)}</span>
          <div className="track">
            <span
              className={v.value < 0 ? "minus" : ""}
              style={{ width: `${(Math.abs(v.value) / max) * 100}%` }}
            />
          </div>
          <span>
            {v.value.toFixed(3)}
            {v.std !== undefined && (
              <small title={t("spread")}> ± {v.std.toFixed(3)}</small>
            )}
          </span>
        </div>
      ))}
    </div>
  );
}
