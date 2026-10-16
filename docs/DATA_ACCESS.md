# Tải dữ liệu / Data access

## Tiếng Việt

Nguồn: **Fedesoriano — Stroke Prediction Dataset**, Kaggle, phiên bản 1.

https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset

Điều kiện được ghi nhận trong provenance: dùng cho giáo dục, ghi công tác giả; metadata “Data files © Original Authors”. Đọc lại điều kiện hiện tại trước khi tải và sử dụng. Không đóng gói CSV, PDF bài nộp, bảng điểm hoặc tài liệu cá nhân trong portfolio này.

### Cách 1 — script đã có

Từ thư mục gốc `StrokeLens`, sau khi kiểm tra điều kiện nguồn:

```powershell
python scripts/download_data.py
```

Script kiểm tra mô tả điều kiện nguồn, lấy version 1, giải nén đúng file CSV, từ chối ghi đè dữ liệu khác và ghi provenance. Nếu Kaggle chặn truy cập hoặc yêu cầu đăng nhập, dùng cách thủ công; không thay CSV thật bằng dữ liệu giả.

### Cách 2 — tải thủ công

1. Mở trang nguồn, đăng nhập Kaggle nếu được yêu cầu.
2. Chọn dữ liệu version 1, tải archive và giải nén `healthcare-dataset-stroke-data.csv`.
3. Đặt file tại `StrokeLens/data/raw/healthcare-dataset-stroke-data.csv`.
4. Kiểm tra checksum rồi mở notebook và Run All.

```powershell
Get-FileHash -Algorithm SHA256 '.\data\raw\healthcare-dataset-stroke-data.csv'
```

SHA-256 mong đợi:

```text
644d473b05d2797006bd94865e4f8bb057f0c721617911613c82c8fcfc707420
```

Không mở/lưu lại CSV bằng Excel trước khi đối chiếu checksum vì thao tác này có thể thay đổi bytes và định dạng số. Nếu checksum khác, dừng để kiểm tra version/nguồn thay vì sửa dữ liệu cho khớp kết quả.

Chạy ứng dụng từ model đã lưu không bắt buộc tải CSV. Để tái lập notebook hoặc huấn luyện lại, cần CSV đúng nguồn. Các tham số môi trường tùy chọn phục vụ kiểm tra cục bộ được mô tả trong notebook; không ghi đường dẫn máy riêng vào code công khai.

## English

Download publisher **version 1** from the Kaggle page above, after reviewing the current terms. Either run `python scripts/download_data.py` from the project root or extract the original CSV manually to `data/raw/healthcare-dataset-stroke-data.csv`. Verify its SHA-256 against the value above. Do not resave the CSV in spreadsheet software before checking it.

The portfolio bundles no raw dataset or personal source documents. Saved model artifacts support inference without downloading data; reproducing notebook training requires the exact CSV. If the source endpoint requires authentication, use Kaggle's normal sign-in/download flow; never paste account credentials into project files. A checksum mismatch requires source review, not synthetic replacement or ad-hoc correction.
