# Hướng dẫn deploy ứng dụng Python lên Render

## 1. Đảm bảo code đã push lên GitHub
- Nếu chưa có repo, tạo mới trên GitHub và push toàn bộ code lên đó.

## 2. Đăng ký và đăng nhập Render
- Truy cập https://render.com
- Đăng ký tài khoản hoặc đăng nhập bằng GitHub.

## 3. Tạo Web Service mới
- Chọn "New Web Service"
- Kết nối với repo GitHub của bạn
- Chọn branch (thường là main)

## 4. Cấu hình service
- Environment: Python 3.x
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port 8000` (hoặc file chạy phù hợp)
- Nếu deploy Flask: `python front-end-app.py`
- Chọn Free Plan

## 5. Thiết lập biến môi trường (nếu cần)
- Thêm các biến như MONGODB_URL, SECRET_KEY,...

## 6. Deploy
- Render sẽ tự động build và deploy app của bạn.
- Sau khi hoàn tất, bạn sẽ nhận được link public để truy cập app.

---
Nếu cần deploy cả backend và frontend, hãy tạo 2 Web Service riêng biệt (1 cho FastAPI, 1 cho Flask).

## 7. Troubleshooting
- Kiểm tra log khi build/deploy lỗi
- Đảm bảo requirements.txt đầy đủ
- Kiểm tra file start đúng tên

---
Nếu cần hướng dẫn chi tiết từng bước, hãy gửi link repo GitHub của bạn!
