export type Metric = {
  ap: number;
  recall: number;
  precision: number;
  f1: number;
  roc_auc: number;
  accuracy: number;
  brier: number;
  confusion: number[][];
  recall_wilson_95?: number[];
};
export type Trial = Metric & {
  family: string;
  params: Record<string, number | string>;
  threshold: number;
  fold_ap: number[];
};
export type Curves = {
  pr: { recall: number; precision: number }[];
  thresholds: { threshold: number; recall: number; precision: number }[];
  calibration: { predicted: number; observed: number }[];
};
export type Report = {
  version: string;
  selected: Trial;
  cv_trials: Trial[];
  holdout: Metric;
  baseline: Metric;
  curves: { oof: Curves; holdout: Curves };
  importance: { feature: string; mean: number; std: number }[];
  split: {
    development_rows: number;
    holdout_rows: number;
    development_positive: number;
    holdout_positive: number;
  };
};
export type Bin = {
  label: string;
  count: number;
  positive: number;
  rate: number | null;
};
export type Eda = {
  rows: number;
  positive: number;
  prevalence: number;
  missing: Record<string, number>;
  histograms: Record<string, Bin[]>;
};
export type Overview = {
  version: string;
  threshold: number;
  family: string;
  schema: {
    categories: Record<string, string[]>;
    ranges: Record<string, [number, number]>;
  };
  provenance: { source: string };
};
export type Prediction = {
  score: number;
  threshold: number;
  above_threshold: boolean;
  version: string;
  family: string;
  bmi_imputed: boolean;
  local: { feature: string; value: number }[] | null;
  intercept: number | null;
  log_odds: number | null;
  warnings: string[];
};
export type Data = { overview: Overview; eda: Eda; report: Report };
export type ViewContext = {
  data: Data;
  t: (key: import("./i18n").Key) => string;
  format: (value: number, digits?: number) => string;
  percent: (value: number) => string;
};
