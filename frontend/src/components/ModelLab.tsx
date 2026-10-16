import { Chart, Section } from "../Charts";
import type { Key } from "../i18n";
import type { ViewContext, Trial } from "../types";
import { useState } from "react";

export default function ModelLab({ data, t, format, percent }: ViewContext) {
  const report = data.report;
  const [curveIndex, setCurveIndex] = useState(30);
  const families = [...new Set(report.cv_trials.map((r) => r.family))].map(
    (family) =>
      report.cv_trials
        .filter((r) => r.family === family)
        .sort((a, b) => b.ap - a.ap)[0],
  );
  const trade =
    report.curves.oof.thresholds[
      Math.min(curveIndex, report.curves.oof.thresholds.length - 1)
    ];
  const trialTable = (trials: Trial[], detailed = false) => (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>{t("family")}</th>
            {detailed && <th>{t("settings")}</th>}
            <th>{t("ap")}</th>
            <th>{t("recall")}</th>
            <th>{t("precision")}</th>
            <th>{t("f1")}</th>
            <th>{t("roc")}</th>
            <th>{t("threshold")}</th>
          </tr>
        </thead>
        <tbody>
          {trials.map((r, i) => (
            <tr
              key={`${r.family}-${i}`}
              className={
                r.family === report?.selected.family &&
                r.threshold === report.selected.threshold
                  ? "chosen"
                  : ""
              }
            >
              <th scope="row">
                {r.family}
                {r.family === report?.selected.family &&
                  r.threshold === report.selected.threshold && (
                    <small className="tag">{t("selected")}</small>
                  )}
              </th>
              {detailed && (
                <td>
                  <code>{JSON.stringify(r.params)}</code>
                </td>
              )}
              <td>{format(r.ap, 3)}</td>
              <td>{percent(r.recall)}</td>
              <td>{percent(r.precision)}</td>
              <td>{format(r.f1, 3)}</td>
              <td>{format(r.roc_auc, 3)}</td>
              <td>{format(r.threshold, 3)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
  return (
    <Section id="lab" number="03" title={t("lab")}>
      <p className="section-intro">{t("labIntro")}</p>
      <p className="caption">
        {t("development")}: {report.split.development_rows} {t("rows")},{" "}
        {report.split.development_positive} {t("positiveCount")}. {t("holdout")}
        : {report.split.holdout_rows} {t("rows")},{" "}
        {report.split.holdout_positive} {t("positiveCount")}.
      </p>
      <h3>{t("cv")}</h3>
      {trialTable(families)}
      <details className="all-trials">
        <summary>{t("details")}</summary>
        {trialTable(report.cv_trials, true)}
      </details>
      <p className="caption">{t("apHelp")}</p>
      <div className="grid-two">
        <article className="card">
          <p className="eyebrow">
            {t("selected")} · {report.selected.family}
          </p>
          <h3>{t("holdout")}</h3>
          <div className="metric-grid">
            {(
              ["ap", "recall", "precision", "f1", "roc_auc", "brier"] as const
            ).map((key) => (
              <div key={key}>
                <strong>{format(report.holdout[key], 3)}</strong>
                <span>{t(key === "roc_auc" ? "roc" : key)}</span>
              </div>
            ))}
          </div>
          <p>{t("holdoutBody")}</p>
          <p className="caption">
            {t("uncertainty")}:{" "}
            {report.holdout.recall_wilson_95!.map(percent).join(" – ")}
          </p>
          <p className="caption">
            {t("baseline")}: AP {format(report.baseline.ap, 3)} · {t("recall")}{" "}
            {percent(report.baseline.recall)} · {t("accuracy")}{" "}
            {percent(report.baseline.accuracy)} · {t("brier")}{" "}
            {format(report.baseline.brier, 3)}
          </p>
        </article>
        <article className="card">
          <h3>{t("matrix")}</h3>
          <p className="caption">
            {t("actual")} ↓ · {t("predicted")} →
          </p>
          <div className="confusion">
            {(["tn", "fp", "fn", "tp"] as Key[]).map((key, i) => (
              <div
                className={key === "fn" || key === "fp" ? "error-cell" : ""}
                key={key}
              >
                <span>{t(key)}</span>
                <strong>
                  {report.holdout.confusion[Math.floor(i / 2)][i % 2]}
                </strong>
              </div>
            ))}
          </div>
        </article>
      </div>
      <div className="grid-two">
        <article className="card">
          <h3>
            {t("pr")} · {t("holdout")}
          </h3>
          <Chart
            rows={report.curves.holdout.pr}
            x="recall"
            xLabel={t("recall")}
            yLabel={t("precision")}
            domain={[0, 1]}
            series={[
              {
                key: "precision",
                label: report.selected.family,
                color: "#087f78",
              },
            ]}
          />
        </article>
        <article className="card">
          <h3>{t("tradeoff")}</h3>
          <Chart
            rows={report.curves.oof.thresholds}
            x="threshold"
            xLabel={t("threshold")}
            yLabel={t("precision") + " / " + t("recall")}
            domain={[0, 1]}
            series={[
              { key: "precision", label: t("precision"), color: "#087f78" },
              { key: "recall", label: t("recall"), color: "#b46c4b" },
            ]}
          />
          <label className="range-label">
            {t("thresholdExplore")}
            <input
              type="range"
              min="0"
              max={report.curves.oof.thresholds.length - 1}
              value={Math.min(
                curveIndex,
                report.curves.oof.thresholds.length - 1,
              )}
              onChange={(e) => setCurveIndex(Number(e.target.value))}
              aria-label={t("thresholdExplore")}
            />
          </label>
          <output className="caption">
            {t("thresholdValue")}: {format(trade!.threshold, 3)} ·{" "}
            {t("precision")} {percent(trade!.precision)} · {t("recall")}{" "}
            {percent(trade!.recall)}
          </output>
          <p className="caption">{t("thresholdHelp")}</p>
        </article>
      </div>
      <article className="card calibration">
        <div>
          <h3>{t("calibration")}</h3>
          <p>{t("calibrationBody")}</p>
          <p className="caption">
            {t("brier")}: {format(report.selected.brier, 3)} · {t("threshold")}:{" "}
            {format(report.selected.threshold, 4)}
          </p>
        </div>
        <Chart
          rows={report.curves.oof.calibration}
          x="predicted"
          xLabel={t("score")}
          yLabel={t("observed")}
          domain={[0, 1]}
          series={[
            { key: "observed", label: t("observed"), color: "#087f78" },
            { key: "predicted", label: t("score"), color: "#b4ceca" },
          ]}
        />
      </article>
    </Section>
  );
}
