# KJC Testing API Event

Dự án Testing API đơn giản với FastAPI, Flask và MongoDB, kèm theo giao diện web để quản lý users tham gia event.

## 🚀 Cài đặt và Chạy

### 1. Cài đặt Dependencies

```bash
pip install -r requirements.txt
```

### 2. Cấu hình MongoDB

Tạo file `.env` và thêm connection string MongoDB:

```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=user_crud_db
```

### 3. Chạy API Backend

```bash
python main.py
```

API sẽ chạy tại: http://localhost:5000

- **Docs**: http://localhost:5000/docs
- **Healthcheck**: http://localhost:5000/health
- **Test MongoDB**: http://localhost:5000/test-db

### 4. Chạy Frontend Web Interface

```bash
python front-end-app.py
```

Frontend sẽ chạy tại: http://localhost:5000

## 📚 API Endpoints

### Users CRUD

| Method | URL | Mô tả |
|--------|-----|-------|
| `GET` | `/users` | Lấy danh sách tất cả users |
| `POST` | `/users` | Tạo user mới |
| `GET` | `/users/{username}` | Lấy thông tin user theo username |
| `PUT` | `/users/{username}` | Cập nhật user theo username |
| `DELETE` | `/users/{username}` | Xóa user theo username |

### Ví dụ User Object

```json
{
  "username": "xaclo89",
  "password": "$2b$10$gMmnRmp0hrNGY.Q6lBCdguLaBvlzoUEUMh7yLOcAX3ZYQo7VsmlYG",
  "phone": "0961737854",
  "type": "user",
  "status": "active",
  "avatarUrl": "",
  "point": 0,
  "totalPoint": 0,
  "levelId": "689467ff8dc2b0f9b7796e93",
  "externalVerifyHistoryIds": [],
  "isVerifired": false,
  "createdAt": "2025-10-12T14:02:55.555Z",
  "updatedAt": "2025-10-12T14:02:55.555Z"
}
```

## 🎯 Sử dụng Frontend

Frontend cung cấp 4 tab chính:

2. **➕ Create User**: Tạo user mới
4. **🗑️ Delete User**: Xóa user

## 🔧 Cấu trúc Dự án

```
kjc-python-bot-testing-api/
├── main.py                          # FastAPI application chính
├── botnet_routes.py                 # Botnet routes (no user CRUD)
├── front-end-app.py                # Flask frontend interface
├── templates/
│   └── crud_interface.html          # HTML template cho frontend
├── requirements.txt                 # Dependencies
├── .env                            # Cấu hình database
├── .gitignore                      # Git ignore file
└── README.md                       # Hướng dẫn này
```

## 🛠️ Tính năng

### Backend (FastAPI)
- ✅ CRUD đầy đủ cho Users
- ✅ MongoDB integration
- ✅ Dynamic schema (không cần model cứng)
- ✅ Auto-convert ObjectId to string
- ✅ Health check endpoints
- ✅ API documentation (Swagger/OpenAPI)

### Frontend (Flask + HTML/JS)
- ✅ Giao diện web đơn giản
- ✅ Tab-based navigation
- ✅ Form validation
- ✅ Real-time API calls
- ✅ Error handling và success messages
- ✅ Responsive design

## 🐛 Troubleshooting

### API không chạy được
- Kiểm tra MongoDB đã chạy chưa
- Kiểm tra file `.env` có đúng connection string không

### Frontend không kết nối được API
- Đảm bảo API backend đã chạy tại http://localhost:5000
- Kiểm tra CORS nếu có lỗi cross-origin

### Dependencies lỗi
- Sử dụng Python 3.10+ (được test với Python 3.14)
- Cài đặt lại: `pip install -r requirements.txt --force-reinstall`

## 🎉 Demo

1. Chạy server: `python main.py`
2. Truy cập http://localhost:5000
3. Thử các chức năng CRUD với users!

## 📝 Notes

- Project sử dụng dynamic schema, có thể thêm bất kỳ field nào cho user
- Tất cả dữ liệu được lưu trong MongoDB
- Frontend là single-page app sử dụng vanilla JavaScript
- API hỗ trợ tất cả HTTP methods cần thiết cho CRUD