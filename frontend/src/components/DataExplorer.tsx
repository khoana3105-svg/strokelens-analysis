import { Chart, Section } from "../Charts";
import type { Key } from "../i18n";
import type { ViewContext } from "../types";
import { useState } from "react";

export default function DataExplorer({ data, t, format }: ViewContext) {
  const [variable, setVariable] = useState("age");
  const [measure, setMeasure] = useState("count");
  const bins = data.eda.histograms[variable] ?? [];
  const rows = bins.map((b) => ({
    ...b,
    negative: b.count - b.positive,
    rate: b.rate === null ? null : b.rate * 100,
  }));
  return (
    <Section id="explorer" number="02" title={t("explorer")}>
      <p className="section-intro">{t("explorerIntro")}</p>
      <div className="grid-two">
        <article className="card">
          <div className="controls">
            <label>
              {t("variable")}
              <select
                aria-label={t("variable")}
                value={variable}
                onChange={(e) => setVariable(e.target.value)}
              >
                {["age", "avg_glucose_level", "bmi"].map((field) => (
                  <option key={field} value={field}>
                    {t(field as Key)}
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t("measure")}
              <select
                aria-label={t("measure")}
                value={measure}
                onChange={(e) => setMeasure(e.target.value)}
              >
                <option value="count">{t("count")}</option>
                <option value="rate">{t("rate")}</option>
              </select>
            </label>
          </div>
          <Chart
            kind="bar"
            rows={rows}
            x="label"
            xLabel={t(variable as Key)}
            yLabel={t(measure === "count" ? "count" : "rate")}
            domain={measure === "rate" ? [0, 100] : undefined}
            series={
              measure === "count"
                ? [
                    { key: "negative", label: t("negative"), color: "#b4ceca" },
                    { key: "positive", label: t("positive"), color: "#087f78" },
                  ]
                : [{ key: "rate", label: t("rate"), color: "#087f78" }]
            }
          />
          <p className="caption">{t("binHelp")}</p>
          <details>
            <summary>{t("denominator")}</summary>
            <table>
              <thead>
                <tr>
                  <th>{t("variable")}</th>
                  <th>{t("count")}</th>
                  <th>{t("positive")}</th>
                </tr>
              </thead>
              <tbody>
                {bins.map((b) => (
                  <tr key={b.label}>
                    <th>{b.label}</th>
                    <td>{b.count}</td>
                    <td>{b.positive}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </details>
        </article>
        <article className="card">
          <p className="eyebrow">{t("missing")}</p>
          <h3>
            {data.eda.missing.bmi} / {format(data.eda.rows, 0)}
          </h3>
          <p>{t("missingBody")}</p>
          <div
            className="prevalence-bar"
            role="img"
            aria-label={`${t("prevalence")}: ${format(data.eda.prevalence * 100)}%`}
          >
            <span style={{ width: `${data.eda.prevalence * 100}%` }} />
          </div>
          <p className="caption">
            {t("positive")}: {data.eda.positive} / {data.eda.rows} ·{" "}
            {t("negative")}: {data.eda.rows - data.eda.positive} /{" "}
            {data.eda.rows}
          </p>
          <table>
            <thead>
              <tr>
                <th>{t("variable")}</th>
                <th>{t("missing")}</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(data.eda.missing).map(([field, count]) => (
                <tr key={field}>
                  <th scope="row">{t(field as Key)}</th>
                  <td>
                    {count} / {data.eda.rows}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </article>
      </div>
    </Section>
  );
}
