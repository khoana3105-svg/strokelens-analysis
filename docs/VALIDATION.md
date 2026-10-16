# Kiểm tra bản portfolio / Portfolio validation

Ngày / Date: **16/10/2026**, Asia/Saigon. Thư mục độc lập `StrokeLens`, cạnh `Rever-apartment-analysisHCM`. Không publish, không cài dependency mới, không copy CSV nguồn hoặc tài liệu cá nhân vào bản bàn giao.

| Thành phần / Component | Kết quả / Result | Bằng chứng và giới hạn / Evidence and limits |
|---|---|---|
| Notebook song ngữ | PASS | 47 cell, 23 code cell chạy bằng nbclient/Jupyter kernel thật; 10 hình, không output lỗi |
| Dataset | PASS | Đọc CSV nguồn sẵn có qua biến môi trường phục vụ QA; checksum khớp; raw không nằm trong thư mục bàn giao |
| Tái lập kết quả | PASS | AP .1715347, ROC-AUC .8533745, recall .82, precision .1469534; confusion [[734,238],[9,41]]; cùng thí nghiệm/split, không phải holdout mới |
| Notebook structure | PASS | nbformat validate; outputs mới lưu riêng tại outputs/ |
| Kiểm tra hình | PASS | Đã xem contact sheet 10 hình: phân phối, thiếu BMI, nhóm tuổi, tương quan, PR, calibration, importance, confusion, local explanation |
| API/model tests | PASS | 29 passed, 1 skipped; test nguồn raw bỏ qua có chủ đích vì dữ liệu không được đóng gói |
| Translation parity | PASS | 131 key EN/VI, nội dung không rỗng |
| Frontend format | PASS | Prettier check; dùng code nguồn hiện có không thay đổi |
| TypeScript / Vite build | PASS | Source frontend byte-identical giữa bản gốc và bản sao; build bằng dependency sẵn có, copy build mới vào frontend/dist của bản sao để kiểm tra |
| Browser smoke | PASS | App từ bản sao, localhost:8016, FastAPI thật + pipeline thật; hai profile, EN/VI, input lỗi, null BMI, EDA, threshold, local terms; không page exception; 390px không tràn ngang |
| Screenshot | PASS | Cập nhật docs bằng screenshot desktop EN và mobile VI chụp từ lần kiểm tra này; đã xem ảnh |
| Fresh dependency install | NOT RUN | Không cài package; môi trường app dùng venv gốc, notebook dùng môi trường notebook có sẵn |
| Kaggle download | NOT RUN | Không tải lại; script và hướng dẫn nguồn được giữ, notebook kiểm tra CSV nguồn sẵn có |
| Docker / remote CI / hosting | NOT RUN | Có cấu hình từ dự án gốc; chưa build Docker, chưa chạy GitHub Actions và chưa publish |

## Lưu ý môi trường / Environment notes

- Vite build ban đầu bị sandbox chặn ghi file tạm. Đã chạy lại với quyền thực thi được duyệt, không thay đổi package hoặc global settings.
- Starlette cảnh báo deprecation của httpx TestClient; test vẫn pass. Không tự nâng dependency.
- Kernel ghi cảnh báo hạn chế permission thư mục IPython và transport local. Notebook hoàn tất; không xem các cảnh báo là kiểm tra bảo mật hoặc chứng nhận môi trường production.
- Phiên bản notebook thực tế được ghi trong `notebook_environment.json`; Python app trong `requirements-lock.txt`. Không khẳng định hai môi trường giống hệt hoặc cài mới đã kiểm thử.
- `docs/DELIVERY.md`, `docs/REQUIREMENTS.md` và các audit gốc là lịch sử của lần triển khai trước; dùng bảng này cho trạng thái bản đóng gói hiện tại.

## Commands used / Lệnh kiểm tra

```text
python scripts/verify_portfolio_notebook.py
python -m pytest tests -q -p no:cacheprovider
npm.cmd run check:i18n
npm.cmd run check:format
npm.cmd run build
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8016
python scripts/browser_smoke.py --url http://127.0.0.1:8016
```

Các lệnh thực tế dùng interpreter/môi trường sẵn có và thư mục làm việc tương ứng; không mặc định là Python hệ thống. QA dùng `STROKELENS_DATA_PATH` trỏ tới bản nguồn được phép đọc; người dùng tái lập bình thường tải CSV về `data/raw/` theo hướng dẫn.
