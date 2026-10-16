import { useEffect, useState } from "react";
import { dictionary } from "./i18n";
import type { Key, Lang } from "./i18n";
import type { Data, Eda, Overview, Prediction, Report } from "./types";

import DataExplorer from "./components/DataExplorer";
import ModelLab from "./components/ModelLab";
import RiskSimulator from "./components/RiskSimulator";
import Explainability from "./components/Explainability";

const sections: Key[] = ["story", "explorer", "lab", "simulator", "explain"];

async function get<T>(path: string): Promise<T> {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json() as Promise<T>;
}

export default function App() {
  const [lang, setLang] = useState<Lang>(() => {
    try {
      return localStorage.getItem("strokelens-language") === "vi" ? "vi" : "en";
    } catch {
      return "en";
    }
  });
  const t = (key: Key) => dictionary[lang][key];
  const format = (n: number, digits = 1) =>
    n.toLocaleString(lang === "vi" ? "vi-VN" : "en-US", {
      maximumFractionDigits: digits,
    });
  const percent = (n: number) => `${format(n * 100)}%`;
  const [data, setData] = useState<Data | null>(null);
  const [loadError, setLoadError] = useState(false);
  const [reload, setReload] = useState(0);
  const [prediction, setPrediction] = useState<Prediction | null>(null);

  useEffect(() => {
    document.documentElement.lang = lang;
    try {
      localStorage.setItem("strokelens-language", lang);
    } catch {
      /* Preference persistence can be unavailable in private browsing. */
    }
  }, [lang]);
  useEffect(() => {
    let alive = true;
    setLoadError(false);
    Promise.all([
      get<Overview>("/api/overview"),
      get<Eda>("/api/eda"),
      get<Report>("/api/metrics"),
    ])
      .then(([overview, eda, report]) => {
        if (alive) setData({ overview, eda, report });
      })
      .catch(() => {
        if (alive) setLoadError(true);
      });
    return () => {
      alive = false;
    };
  }, [reload]);

  return (
    <>
      <a className="skip" href="#main">
        {t("skip")}
      </a>
      <header className="header">
        <a href="#story" className="brand">
          <span className="brand-icon" aria-hidden="true">
            S
          </span>
          StrokeLens<span className="brand-dot">.</span>
        </a>
        <nav aria-label={t("story")}>
          {sections.map((key) => (
            <a href={`#${key}`} key={key}>
              {t(key)}
            </a>
          ))}
        </nav>
        <div className="languages" role="group" aria-label={t("language")}>
          {(["en", "vi"] as Lang[]).map((value) => (
            <button
              key={value}
              type="button"
              aria-pressed={lang === value}
              onClick={() => setLang(value)}
            >
              {value.toUpperCase()}
            </button>
          ))}
        </div>
      </header>
      <main id="main">
        <section id="story" className="hero">
          <div>
            <p className="eyebrow">{t("edition")}</p>
            <h1>{t("hero")}</h1>
            <p className="hero-intro">{t("intro")}</p>
            <div className="actions">
              <a className="button" href="#simulator">
                {t("try")} <span aria-hidden="true">↗</span>
              </a>
              <a className="text-link" href="#lab">
                {t("view")} <span aria-hidden="true">→</span>
              </a>
            </div>
          </div>
          <aside className="hero-panel">
            <p className="eyebrow">{t("question")}</p>
            <p className="serif">{t("questionBody")}</p>
            <div className="lens" aria-hidden="true">
              <div />
              <span>01 / 05</span>
            </div>
          </aside>
        </section>
        {!data && (
          <div className="notice" role={loadError ? "alert" : "status"}>
            {t(loadError ? "error" : "loadingData")}
            {loadError && (
              <button onClick={() => setReload((n) => n + 1)}>
                {t("retry")}
              </button>
            )}
          </div>
        )}
        {data && (
          <>
            <div className="stats">
              <div>
                <strong>{format(data.eda.rows, 0)}</strong>
                <span>{t("records")}</span>
              </div>
              <div>
                <strong>{percent(data.eda.prevalence)}</strong>
                <span>{t("prevalence")}</span>
              </div>
              <div>
                <strong>5</strong>
                <span>{t("families")}</span>
              </div>
            </div>
            <div className="safety">
              <strong>{t("safetyTitle")}</strong>
              <p>{t("safety")}</p>
              <p>{t("limits")}</p>
            </div>
            <article className="audit">
              <div>
                <p className="eyebrow">01 · {t("method")}</p>
                <h3>{t("auditTitle")}</h3>
              </div>
              <div>
                <p>{t("auditBody")}</p>
                <a
                  href={data.overview.provenance.source}
                  target="_blank"
                  rel="noreferrer"
                >
                  {t("source")} ↗
                </a>
              </div>
            </article>
            <DataExplorer data={data} t={t} format={format} percent={percent} />
            <ModelLab data={data} t={t} format={format} percent={percent} />
            <RiskSimulator
              data={data}
              t={t}
              format={format}
              percent={percent}
              prediction={prediction}
              setPrediction={setPrediction}
            />
            <Explainability
              data={data}
              t={t}
              format={format}
              percent={percent}
              prediction={prediction}
            />
          </>
        )}
      </main>
      <footer>
        <a className="brand" href="#story">
          StrokeLens.
        </a>
        <p>{t("footer")}</p>
        <a href="#main">↑</a>
      </footer>
    </>
  );
}
