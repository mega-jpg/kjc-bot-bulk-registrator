@echo off
echo =====================================
echo    CAI DAT DEPENDENCIES CHO PYTHON
echo =====================================
echo.

echo [1] Kiem tra Python va pip...
python --version
pip --version
echo.

echo [2] Chon loai server ban muon:
echo    1. FastAPI (Khuyến nghị)
echo    2. Flask (Truyền thống)
echo    3. Cài tất cả (Full)
echo    4. HTTP Server (Không cần cài gì)
echo.

set /p choice="Nhap lua chon (1/2/3/4): "

if "%choice%"=="1" (
    echo.
    echo [3] Cai dat FastAPI dependencies...
    pip install -r requirements-fastapi.txt
    echo.
    echo ✅ Hoan thanh! Chay server: python main.py
) else if "%choice%"=="2" (
    echo.
    echo [3] Cai dat Flask dependencies...
    pip install -r requirements-flask.txt
    echo.
    echo ✅ Hoan thanh! Chay server: python main_flask.py
) else if "%choice%"=="3" (
    echo.
    echo [3] Cai dat tat ca dependencies...
    pip install -r requirements-full.txt
    echo.
    echo ✅ Hoan thanh! Co the chay bat ky server nao!
) else if "%choice%"=="4" (
    echo.
    echo ✅ HTTP Server khong can cai gi them!
    echo Chay server: python main_http.py
) else (
    echo ❌ Lua chon khong hop le!
)

echo.
echo =====================================
echo         CAI DAT HOAN THANH!
echo =====================================
pause