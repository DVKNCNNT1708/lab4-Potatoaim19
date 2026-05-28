# RUN_LOCAL.md – Hướng dẫn chạy AI Vision Service (Lab 04)

Tài liệu này hướng dẫn cách đóng gói và chạy AI Vision service trong môi trường Docker.

---

## 1. Chuẩn bị
- Đảm bảo đã cài đặt **Docker Desktop**.
- Cài đặt dependencies (để chạy linter/test local):
```bash
npm install
```

---

## 2. Build Docker image
Sử dụng Makefile để build image:
```bash
make build
```
Hoặc dùng lệnh Docker:
```bash
docker build -t fit4110/ai-vision:lab04 .
```

---

## 3. Chạy Container
Khởi chạy service kèm theo file cấu hình môi trường:
```bash
make run
```
Service sẽ lắng nghe tại cổng `8000`.

---

## 4. Kiểm tra hoạt động
Kiểm tra Healthcheck endpoint:
```bash
curl http://localhost:8000/health
```
**Kết quả mong đợi:**
```json
{
  "status": "ok",
  "service": "ai-vision-service",
  "time": "2026-05-10T..."
}
```

---

## 5. Chạy Automation Test (Newman)
Sau khi container đã chạy, mở một terminal mới và chạy bộ test Postman:
```bash
make test-docker
```
Kết quả báo cáo (HTML/XML) sẽ được lưu trong thư mục `reports/`.

---

## 6. Dừng Service
```bash
make stop
```
