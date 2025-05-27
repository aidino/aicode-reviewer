# 🚀 Quick Start Guide

## Khởi Chạy Ứng Dụng

### Phương Pháp 1: Sử dụng Script Tự Động (Khuyến Nghị)

```bash
# Kích hoạt virtual environment
source venv/bin/activate

# Chạy script khởi động cả frontend và backend
./start_servers.sh
```

Script sẽ tự động:
- ✅ Khởi chạy Backend FastAPI tại `http://localhost:8000`
- ✅ Khởi chạy Frontend React tại `http://localhost:5173`
- ✅ Kiểm tra health của cả hai servers
- ✅ Hiển thị links hữu ích

### Phương Pháp 2: Chạy Thủ Công

#### 1️⃣ Khởi Chạy Backend

```bash
# Từ thư mục gốc dự án
source venv/bin/activate
python -m uvicorn src.webapp.backend.api.main:app --host 127.0.0.1 --port 8000 --reload
```

#### 2️⃣ Khởi Chạy Frontend

```bash
# Mở terminal mới và chuyển đến thư mục frontend
cd src/webapp/frontend
npm run dev
```

## 📋 Endpoints Quan Trọng

| Service | URL | Mô Tả |
|---------|-----|-------|
| **Frontend** | http://localhost:5173 | Giao diện chính của ứng dụng |
| **Backend API** | http://localhost:8000 | REST API backend |
| **API Documentation** | http://localhost:8000/docs | Swagger UI docs |
| **API Health** | http://localhost:8000/health | Health check endpoint |

## 🔍 Test API Endpoints

```bash
# Test tất cả endpoints
python test_api_endpoints.py

# Test một endpoint cụ thể
curl http://localhost:8000/api/scans/
curl http://localhost:8000/api/scans/demo_scan_1/report
```

## 📱 Sử Dụng Ứng Dụng

1. **Truy cập**: Mở browser và vào `http://localhost:5173`
2. **Xem Scans**: Trang chủ hiển thị danh sách scans có sẵn
3. **Xem Report**: Click vào một scan để xem chi tiết report
4. **Dashboard**: Click "Dashboard" để xem analytics tổng quan

## 🛠️ Troubleshooting

### Lỗi "Error loading scans"
- ✅ **Đã sửa**: Cập nhật API endpoints trong frontend để sử dụng `/api` prefix
- ✅ **Đã sửa**: Sửa imports trong backend để sử dụng relative imports
- ✅ **Đã sửa**: Cập nhật Vite proxy configuration

### Backend không khởi động
```bash
# Kiểm tra imports
python -c "from src.webapp.backend.api.main import app; print('OK')"

# Chạy từ thư mục gốc với module path đầy đủ
python -m uvicorn src.webapp.backend.api.main:app --reload
```

### Frontend không kết nối được backend
```bash
# Kiểm tra proxy hoạt động
curl http://localhost:5173/api/scans/

# Kiểm tra backend trực tiếp
curl http://localhost:8000/api/scans/
```

## 🎯 Chức Năng Hiện Có

- ✅ **Scan List**: Hiển thị danh sách scans với mock data
- ✅ **Report View**: Xem chi tiết findings, LLM insights, diagrams
- ✅ **Dashboard**: Analytics và metrics tổng quan
- ✅ **Feedback System**: Cho phép user feedback trên findings
- ✅ **Multi-language Support**: Python, Java, Kotlin, JavaScript
- ✅ **Flat Design**: Modern UI với clean aesthetic

## 🔄 Development Workflow

```bash
# Khởi động servers
./start_servers.sh

# Làm việc với code...
# Backend tự động reload khi code thay đổi
# Frontend tự động hot reload

# Stop servers: Ctrl+C trong terminal chạy script
```

Happy coding! 🎉 