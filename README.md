# FIT4110_lab04_docker_packaging - Camera Stream Service

**Học phần:** FIT4110 – Dịch vụ kết nối và Công nghệ nền tảng  
**Buổi 4:** Đóng gói service với Docker & tư duy công nghệ nền tảng  
**Nhóm thực hiện:** Team Camera (Camera Stream Service)
**Repo gốc:** `FIT4110_lab03_postman_mock_testing`

---

## 1. Ý tưởng nối tiếp từ Lab 03 sang Lab 04

Ở Lab 04, chúng ta chuyển đổi từ Mock Server (Prism) sang **Service thật chạy trong Docker container**.

Dịch vụ **Camera Stream** quản lý các luồng camera và cung cấp endpoint phân tích frame với payload:

```json
{
  "cameraId": "CAM-01",
  "frameUrl": "https://campus.local/frame-001.jpg",
  "timestamp": "2026-05-10T08:00:00Z",
  "requestId": "REQ-001",
  "analysisType": "PERSON_DETECTION"
}
```

Kết quả trả về bao gồm `detectionId`, `confidence` và `boundingBox`.

---

## 2. Mục tiêu đã hoàn thành

- [x] Viết `Dockerfile` tối ưu (multi-stage build).
- [x] Sử dụng `.dockerignore` để loại bỏ `node_modules`, `.venv`.
- [x] Tách cấu hình qua `.env.example`.
- [x] Chạy app bằng user **non-root** (appuser) để bảo mật.
- [x] Cấu hình `HEALTHCHECK` gọi `GET /health` tự động mỗi 30s.
- [x] Build và chạy thành công trên Docker container.
- [x] Đồng bộ hóa logic với OpenAPI Contract của Lab 03.

---

## 3. Cấu trúc repo

```text
FIT4110_lab04_docker_packaging/
├── Dockerfile               # File đóng gói container
├── .dockerignore            # Loại bỏ file thừa khi build
├── .env.example             # Biến môi trường mẫu
├── Makefile                 # Lệnh tắt build/run/test
├── src/
│   └── iot_app/             # Source code Camera Stream (FastAPI)
│       └── main.py
├── contracts/
│   └── camera-stream.openapi.yaml # API Contract của nhóm
├── postman/                 # Bộ test từ Lab 03
├── reports/                 # Kết quả test Newman
└── RUN_LOCAL.md             # Hướng dẫn chạy nhanh
```

---

## 4. Hướng dẫn nhanh (Quick Start)

**Build Image:**
```bash
make build
```

**Chạy Container:**
```bash
make run
```

**Kiểm tra Health:**
```bash
curl http://localhost:8000/health
```
*Kết quả:* `{"status":"ok","service":"camera-stream-service","time":"..."}`

---

## 5. Artefact nộp bài (Submission)

Các file quan trọng đã sẵn sàng:
1. `Dockerfile` & `.dockerignore`
2. `.env.example`
3. `contracts/camera-stream.openapi.yaml`
4. `src/iot_app/main.py` (Logic Camera Stream)
5. `RUN_LOCAL.md` (Hướng dẫn chi tiết)
6. `reports/` (Chứa kết quả test sau khi chạy `make test-docker`)

---

## 6. Ghi chú về bảo mật
- Service chạy trên port `8000`.
- Mọi request (trừ `/health`) yêu cầu `Authorization: Bearer local-dev-token`.
- User trong container: `appuser` (UID 100).
