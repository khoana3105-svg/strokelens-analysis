# Portfolio package

## English description

StrokeLens is a bilingual educational ML case study that rebuilds an observational stroke dataset into a reproducible classification experiment and an interactive full-stack application. It investigates decimal-import corruption, compares five classifier families without holdout tuning, and exposes an actual saved pipeline through FastAPI with transparent threshold trade-offs and model explanations. It is not a clinical risk tool.

## Mô tả tiếng Việt

StrokeLens là dự án ML phục vụ học tập với giao diện Anh–Việt, xây dựng lại thí nghiệm phân loại trên dữ liệu đột quỵ quan sát. Dự án kiểm tra lỗi mất dấu thập phân, so sánh năm họ mô hình với tiền xử lý trong fold và giữ riêng holdout; FastAPI chạy pipeline thật, hiển thị đánh đổi ngưỡng và giải thích mô hình. Không sử dụng để chẩn đoán hay đánh giá nguy cơ cá nhân.

## CV bullets — adapt to your actual reviewed contribution

- Rebuilt a 5,110-record classification workflow from publisher CSV after reproducing decimal-loss anomalies in the reference notebook; preserved all rows and documented hashes, missingness and source-use conditions.
- Compared five classifier families using three-fold development CV and OOF threshold selection; selected balanced Logistic Regression with holdout AP .1715, recall .82 and precision .1470, while reporting 238 false positives and calibration limitations.
- Implemented an inference-only FastAPI service and React/TypeScript EN/VI explorer with interactive metrics, validated inputs, exact linear model terms, automated checks and single-service static serving.

## Five interview talking points

1. **Data integrity:** describe why dividing all glucose/age values by 100 would corrupt integer and one-decimal values; reconstruct decimal loss and explain why reloading authoritative CSV is safer. Explain unknown source sampling and glucose units.
2. **Imbalance and leakage:** contrast majority accuracy with AP/recall/precision; explain fold-fitted imputation/scaling/one-hot and why ordinary SMOTE over nominal integer labels invents categories. Explain retained `Other` and `Unknown`.
3. **Model and threshold selection:** describe the predeclared OOF recall floor, precision trade-off, AP ranking, bounded settings and simplicity preference. Holdout was never used for any choice; OOF selection estimates can be optimistic.
4. **Uncertainty and explanation:** discuss only 50 holdout positives, recall Wilson interval .692–.902, false positives, Brier worse than baseline, and exact intercept-plus-feature log-odds decomposition. Importance cannot justify a medical intervention.
5. **Deployment and trade-offs:** explain one service serving both SPA and API, load-once trusted pipeline, fixed version/threshold, validation, CI and tests; distinguish executed local checks from configured but unexecuted remote CI/container deployment.

## Honest ownership

This deliverable was implemented with AI assistance. Before using first-person claims, run it, review the source audit, reproduce key results, understand the fitted pipeline and be able to explain every CV bullet. No production users, patient outcomes, screening benefits or business savings were measured.
