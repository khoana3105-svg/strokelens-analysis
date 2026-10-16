import { Contributions, Section } from "../Charts";
import type { ViewContext } from "../types";
import type { Prediction } from "../types";

export default function Explainability({
  data,
  t,
  format,
  prediction,
}: ViewContext & { prediction: Prediction | null }) {
  const report = data.report;
  return (
    <Section id="explain" number="05" title={t("explain")}>
      <div className="grid-two">
        <article className="card">
          <h3>{t("global")}</h3>
          <p>{t("globalBody")}</p>
          <Contributions
            values={[...report.importance]
              .sort((a, b) => b.mean - a.mean)
              .map((r) => ({ feature: r.feature, value: r.mean, std: r.std }))}
            t={t}
            unit={t("decrease")}
          />
        </article>
        <article className="card">
          <h3>{t("local")}</h3>
          {data.overview.family === "Logistic Regression" ? (
            <>
              <p>{t("localBody")}</p>
              {prediction?.local ? (
                <>
                  <Contributions
                    values={prediction.local}
                    t={t}
                    unit={t("localUnit")}
                  />
                  <p className="caption">
                    {t("intercept")}: {format(prediction.intercept!, 4)} ·{" "}
                    {t("logodds")}: {format(prediction.log_odds!, 4)}
                  </p>
                </>
              ) : (
                <p className="empty-message">{t("localEmpty")}</p>
              )}
            </>
          ) : (
            <p>{t("globalOnly")}</p>
          )}
        </article>
      </div>
      <div className="method">
        <h3>{t("method")}</h3>
        <p>{t("methodBody")}</p>
        <p>{t("limits")}</p>
      </div>
    </Section>
  );
}
