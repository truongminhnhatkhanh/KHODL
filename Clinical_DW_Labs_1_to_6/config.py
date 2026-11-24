"""
===============================================================================
CẤU HÌNH KẾT NỐI CSDL MYSQL (THIẾT LẬP THỦ CÔNG)
===============================================================================
Hướng dẫn:
- Bạn mở tệp này và chỉnh sửa các thông số kết nối MySQL bên dưới nếu cần.
- Chạy trực tiếp tệp này: `python config.py` để kiểm tra kết nối có thành công không!
"""

import sys
from sqlalchemy import create_engine, text

# --- THÔNG SỐ KẾT NỐI MYSQL CỦA BẠN (TỰ CHỈNH SỬA TẠI ĐÂY) ---
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "nhatkhanh"  # Nhập mật khẩu MySQL của bạn (nếu dùng XAMPP thì để trống "")

# --- TÊN 2 CƠ SỞ DỮ LIỆU ĐƯỢC TẠO TRONG DỰ ÁN ---
OLTP_DB = "hospital_oltp"  # CSDL giao dịch vận hành 3NF (Lab 1)
DW_DB = "hospital_dw"      # Kho dữ liệu phân tích Star Schema (Labs 2 - 6)


def get_server_url():
    """Chuỗi kết nối tới MySQL Server (dùng để tạo Database)."""
    return f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}"


def get_oltp_url():
    """Chuỗi kết nối tới CSDL vận hành hospital_oltp."""
    return f"{get_server_url()}/{OLTP_DB}"


def get_dw_url():
    """Chuỗi kết nối tới Kho dữ liệu hospital_dw."""
    return f"{get_server_url()}/{DW_DB}"


if __name__ == "__main__":
    print("=" * 60)
    print("🔍 ĐANG KIỂM TRA KẾT NỐI TỚI MYSQL SERVER...")
    print(f"👉 Host: {MYSQL_HOST}:{MYSQL_PORT} | User: {MYSQL_USER}")
    print("=" * 60)
    try:
        engine = create_engine(get_server_url())
        with engine.connect() as conn:
            res = conn.execute(text("SELECT VERSION()")).scalar()
            print(f"✅ KẾT NỐI THÀNH CÔNG! Phiên bản MySQL: {res}")
            print("\n👉 Cấu hình đã sẵn sàng. Bạn có thể bắt đầu chạy thủ công từng bước:")
            print("   Bước 1: python scripts/01_load_oltp_csv.py")
            print("   Bước 2: python scripts/02_etl_lab3_initial.py")
            print("   Bước 3: python scripts/03_etl_lab4_advanced.py")
    except Exception as e:
        print(f"❌ KẾT NỐI THẤT BẠI! Lỗi: {e}")
        print("💡 Gợi ý: Hãy mở lại file config.py và kiểm tra lại MYSQL_PASSWORD hoặc bật dịch vụ MySQL.")
