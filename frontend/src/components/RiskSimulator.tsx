import { Section } from "../Charts";
import type { Key } from "../i18n";
import type { ViewContext, Prediction } from "../types";
import { useState } from "react";
import type { FormEvent } from "react";
const initial = {
  age: "25",
  hypertension: "0",
  heart_disease: "0",
  avg_glucose_level: "85",
  bmi: "22",
  gender: "Female",
  ever_married: "No",
  work_type: "Private",
  Residence_type: "Rural",
  smoking_status: "never smoked",
};
type FormValues = typeof initial;

export default function RiskSimulator({
  data,
  t,
  format,
  percent,
  prediction,
  setPrediction,
}: ViewContext & {
  prediction: Prediction | null;
  setPrediction: (value: Prediction | null) => void;
}) {
  const [values, setValues] = useState<FormValues>(initial);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<"validation" | "error" | null>(null);
  const [invalid, setInvalid] = useState<string[]>([]);

  function change(field: keyof FormValues, value: string) {
    setValues((current) => ({ ...current, [field]: value }));
    setPrediction(null);
    setError(null);
    setInvalid((current) => current.filter((f) => f !== field));
  }
  function example(older: boolean) {
    setValues(
      older
        ? {
            ...initial,
            age: "75",
            gender: "Male",
            hypertension: "1",
            heart_disease: "1",
            avg_glucose_level: "200",
            bmi: "35",
            ever_married: "Yes",
            Residence_type: "Urban",
            smoking_status: "formerly smoked",
          }
        : initial,
    );
    setPrediction(null);
    setError(null);
    setInvalid([]);
  }
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!data) return;
    const bad = Object.entries(data.overview.schema.ranges)
      .filter(
        ([field, [low, high]]) =>
          !(field === "bmi" && values.bmi === "") &&
          (values[field as keyof FormValues] === "" ||
            !Number.isFinite(Number(values[field as keyof FormValues])) ||
            Number(values[field as keyof FormValues]) < low ||
            Number(values[field as keyof FormValues]) > high),
      )
      .map(([field]) => field);
    setInvalid(bad);
    if (bad.length) {
      setError("validation");
      return;
    }
    setPending(true);
    setError(null);
    setPrediction(null);
    const body = {
      ...values,
      age: Number(values.age),
      avg_glucose_level: Number(values.avg_glucose_level),
      bmi: values.bmi === "" ? null : Number(values.bmi),
      hypertension: Number(values.hypertension),
      heart_disease: Number(values.heart_disease),
    };
    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (response.status === 422) {
        const detail = (await response.json()) as {
          detail: { field: string }[];
        };
        setInvalid(detail.detail.map((e) => e.field));
        setError("validation");
      } else if (!response.ok) setError("error");
      else setPrediction((await response.json()) as Prediction);
    } catch {
      setError("error");
    } finally {
      setPending(false);
    }
  }

  return (
    <Section id="simulator" number="04" title={t("simulator")}>
      <p className="section-intro">{t("simIntro")}</p>
      <p className="caption">{t("synthetic")}</p>
      <div className="grid-two simulator">
        <form className="card" onSubmit={submit} noValidate>
          <fieldset disabled={pending}>
            <div className="examples">
              <button type="button" onClick={() => example(false)}>
                {t("profileA")}
              </button>
              <button type="button" onClick={() => example(true)}>
                {t("profileB")}
              </button>
            </div>
            <div className="form-grid">
              {(["age", "avg_glucose_level", "bmi"] as const).map((field) => (
                <label
                  key={field}
                  className={invalid.includes(field) ? "invalid" : ""}
                >
                  {t(field)}
                  <input
                    type="number"
                    step="any"
                    min={data.overview.schema.ranges[field][0]}
                    max={data.overview.schema.ranges[field][1]}
                    required={field !== "bmi"}
                    value={values[field]}
                    onChange={(e) => change(field, e.target.value)}
                    aria-label={t(field)}
                    aria-invalid={invalid.includes(field)}
                    aria-describedby={error ? "form-error" : undefined}
                  />
                  <small>
                    {data.overview.schema.ranges[field].join(" – ")}
                  </small>
                </label>
              ))}
              {(["hypertension", "heart_disease"] as const).map((field) => (
                <label key={field}>
                  {t(field)}
                  <select
                    aria-label={t(field)}
                    value={values[field]}
                    onChange={(e) => change(field, e.target.value)}
                  >
                    <option value="0">{t("No")}</option>
                    <option value="1">{t("Yes")}</option>
                  </select>
                </label>
              ))}
              {Object.entries(data.overview.schema.categories).map(
                ([field, options]) => (
                  <label key={field}>
                    {t(field as Key)}
                    <select
                      aria-label={t(field as Key)}
                      value={values[field as keyof FormValues]}
                      onChange={(e) =>
                        change(field as keyof FormValues, e.target.value)
                      }
                    >
                      {options.map((option) => (
                        <option value={option} key={option}>
                          {t(option as Key)}
                        </option>
                      ))}
                    </select>
                  </label>
                ),
              )}
            </div>
            <p className="caption">{t("unitHelp")}</p>
            <button className="button submit" type="submit">
              {t(pending ? "loading" : "submit")}{" "}
              <span aria-hidden="true">→</span>
            </button>
          </fieldset>
          {error && (
            <p id="form-error" role="alert" className="error">
              {t(error)}
            </p>
          )}
        </form>
        <aside className="result card" aria-live="polite" aria-busy={pending}>
          <p className="eyebrow">{t("score")}</p>
          {prediction ? (
            <>
              <strong className="score">{percent(prediction.score)}</strong>
              <h3>{t(prediction.above_threshold ? "above" : "below")}</h3>
              <p>
                {t("threshold")}: {format(prediction.threshold, 4)}
              </p>
              <p>{t("resultHelp")}</p>
              {prediction.bmi_imputed && (
                <p className="caption">{t("imputed")}</p>
              )}
              {prediction.warnings.includes("rare_category") && (
                <p className="caption">{t("rare")}</p>
              )}
              {prediction.warnings.includes("unusual_combination") && (
                <p className="caption">{t("unusual")}</p>
              )}
              <p className="caption">
                {t("version")}: {prediction.version}
              </p>
              <a className="text-link" href="#explain">
                {t("local")} →
              </a>
            </>
          ) : (
            <>
              <div className="empty-lens" aria-hidden="true">
                ◎
              </div>
              <p>{t(pending ? "loading" : "resultHelp")}</p>
            </>
          )}
          <p className="result-safety">{t("safety")}</p>
        </aside>
      </div>
    </Section>
  );
}
