# Upload StrokeLens lên GitHub / GitHub upload guide

## Tiếng Việt

Chưa tạo repository hoặc publish trong lần soạn lại này. Tạo repository trống `strokelens-analysis`, rồi giữ đúng cấu trúc thư mục khi upload.

**Ở root:** `README.md`, `README.en.md`, `.gitignore`, `.dockerignore`, `requirements.txt`, `requirements-lock.txt`, `requirements-notebook.txt`, `requirements-browser.txt`, `pytest.ini`, `Dockerfile`.

**Các thư mục:** `notebooks/`, `backend/`, `frontend/` (code/config/lock, bỏ `dist/` và `node_modules/`), `artifacts/`, `scripts/`, `tests/`, `.github/` và `docs/`.

**Dữ liệu:** chỉ `data/README.md` và `data/raw/.gitkeep`; không có CSV trong bản bàn giao. Nếu sau này tải CSV, không upload nó qua trình duyệt; `.gitignore` không bảo vệ thao tác upload thủ công.

Không upload `.venv`, `outputs`, `.ipynb_checkpoints`, `__pycache__`, PDF bài nộp, thông tin sinh viên hoặc token. `outputs` có model/HTML/ảnh phát sinh khi kiểm tra; notebook công khai đã lưu bảng/ảnh cần xem.

Nếu upload bằng web: tạo/mở từng thư mục trước rồi upload nội dung của đúng thư mục đó. Phân biệt `README.md` ở root với `data/README.md`, giữ `notebooks/StrokeLens_Analysis_EN_VI.ipynb` đúng đường dẫn. Sau cùng kiểm tra link/ảnh ở README.

Nguồn audit và delivery gốc trong docs ghi lại lần làm trước; trạng thái mới nhất nằm ở `docs/VALIDATION.md`. Không upload toàn bộ thư mục Machine Learning cũ.

## English

Create an empty repository and preserve the folder structure above. Include source, trusted artifacts, notebooks, documentation and lock files. Exclude raw data, generated outputs, dependencies, credentials and personal source documents. Browser upload does not honor `.gitignore`; upload only the reviewed files. The repository has not been published by this packaging task.
