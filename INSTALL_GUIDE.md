# 📦 HƯỚNG DẪN CÁI ĐẶT DEPENDENCIES

## 🔍 **Bước 1: Kiểm tra Python**
```bash
python --version
pip --version
```

## 🚀 **Bước 2: Cài đặt theo Framework**

### **FastAPI (Khuyến nghị cho API)**
```bash
# Cài cơ bản
pip install fastapi uvicorn

# Cài đầy đủ
pip install fastapi "uvicorn[standard]" pydantic requests python-multipart
```

### **Flask (Truyền thống)**
```bash
# Cài cơ bản  
pip install flask

# Cài đầy đủ
pip install flask flask-cors requests
```

### **HTTP Server tích hợp**
```bash
# Không cần cài gì - đã có sẵn trong Python!
```

## 📋 **Bước 3: Cài đặt từ file requirements**

### **Cách 1: Cài từ file có sẵn**
```bash
# FastAPI
pip install -r requirements-fastapi.txt

# Flask  
pip install -r requirements-flask.txt

# Tất cả
pip install -r requirements-full.txt
```

### **Cách 2: Cài thủ công từng package**
```bash
# Framework
pip install fastapi
pip install uvicorn[standard]

# HTTP Client
pip install requests
pip install httpx

# Database
pip install pymongo
pip install sqlalchemy

# Utilities
pip install python-dotenv
pip install loguru
```

## 🔧 **Bước 4: Kiểm tra cài đặt**
```bash
# Kiểm tra packages đã cài
pip list

# Kiểm tra FastAPI
python -c "import fastapi; print('FastAPI OK!')"

# Kiểm tra Flask
python -c "import flask; print('Flask OK!')"
```

## ⚡ **Bước 5: Chạy server**

### **FastAPI**
```bash
python main_fastapi.py
# Hoặc
uvicorn main_fastapi:app --reload
```

### **Flask**
```bash
python main_flask.py
```

### **HTTP Server**
```bash
python main_http.py
```

## 🐛 **Xử lý lỗi thường gặp**

### **Lỗi: ModuleNotFoundError**
```bash
# Cài đặt lại package
pip install package_name
```

### **Lỗi: Permission denied**
```bash
# Windows: Chạy PowerShell as Administrator
# Hoặc cài cho user hiện tại
pip install --user package_name
```

### **Lỗi: Version conflict**
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Force reinstall
pip install --force-reinstall package_name
```

### **Lỗi: Python 3.14 compatibility**
```bash
# Dùng phiên bản mới nhất
pip install --upgrade fastapi pydantic uvicorn
```

## 🎯 **Script tự động**

### **Windows (PowerShell/CMD)**
```bash
# Chạy script cài đặt
install_dependencies.bat
```

### **Hoặc step-by-step**
```bash
# 1. Tạo virtual environment (Optional)
python -m venv venv
venv\Scripts\activate

# 2. Upgrade pip
python -m pip install --upgrade pip

# 3. Cài dependencies
pip install -r requirements-fastapi.txt

# 4. Chạy server
python main_fastapi.py
```

## ✅ **Kiểm tra thành công**

Nếu thấy output như này là OK:
```
🚀 Starting FastAPI server...
📖 Docs: http://localhost:5000/docs
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Truy cập: http://localhost:5000 để test!