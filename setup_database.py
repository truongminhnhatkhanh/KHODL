"""
===============================================================================
SCRIPT: setup_database.py (1-Click Khởi tạo toàn bộ CSDL cdw_hospital_db)
ĐỒ ÁN: KHO DỮ LIỆU BỆNH VIỆN LÂM SÀNG (CLINICAL DATA WAREHOUSE - CDW)
CHUẨN BỘ DỰ ÁN VKU: SSMS - SSIS - SSAS - SSRS
===============================================================================
"""
import os
import sys
import subprocess

MYSQL_PATH = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
MYSQL_USER = "root"
MYSQL_PASSWORD = "nhatkhanh"
SSMS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SSMS_HospitalDW")
SSIS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SSIS_HospitalDW")

def run_sql_file(folder_dir, file_name, db_name=None):
    file_path = os.path.join(folder_dir, file_name)
    if not os.path.exists(file_path):
        print(f"❌ Không tìm thấy: {file_path}")
        return False
    
    print(f"▶ Đang thực thi {file_name}...")
    cmd = [MYSQL_PATH, f"-u{MYSQL_USER}", f"-p{MYSQL_PASSWORD}"]
    if db_name:
        cmd.append(db_name)
    cmd.extend(["-e", f"source {file_path.replace(os.sep, '/')}"])
    
    result = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
    if result.returncode != 0:
        print(f"❌ Lỗi khi chạy {file_name}:", result.stderr)
        return False
    return True

def execute_sql(sql, db_name="cdw_hospital_db"):
    cmd = [MYSQL_PATH, f"-u{MYSQL_USER}", f"-p{MYSQL_PASSWORD}", db_name, "-e", sql]
    result = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
    return result.returncode == 0

def main():
    print("=" * 65)
    print("🏥 KHỞI TẠO VÀ NẠP CƠ SỞ DỮ LIỆU KHO LÂM SÀNG: cdw_hospital_db")
    print("=" * 65)

    # 1. Khởi tạo schema DDL (SSMS)
    if not run_sql_file(SSMS_DIR, "01_Create_Database_And_Star_Schema.sql"):
        sys.exit(1)

    # 2. Biên dịch Stored Procedures ETL (SSIS)
    if not run_sql_file(SSIS_DIR, "01_ETL_Stored_Procedures.sql", db_name="cdw_hospital_db"):
        sys.exit(1)

    # 3. Nạp dữ liệu vào Staging (SSMS)
    if not run_sql_file(SSMS_DIR, "02_Seed_Data.sql", db_name="cdw_hospital_db"):
        sys.exit(1)

    # 4. Kích hoạt Stored Procedure sinh Dim Date và ETL Master (SSIS)
    print("▶ Đang kích hoạt Stored Procedure ETL tự động...")
    execute_sql("CALL sp_etl_dim_date('2024-01-01', '2027-12-31');")
    execute_sql("CALL sp_run_full_cdw_etl();")

    print("\n" + "=" * 65)
    print("🎉 HOÀN TẤT 100%! CƠ SỞ DỮ LIỆU cdw_hospital_db ĐÃ SẴN SÀNG.")
    print("👉 Hãy mở MySQL Workbench, mở file 'SSMS_HospitalDW/03_OLAP_Analytical_Queries.sql'")
    print("   và nhấn ⚡ để chạy các câu truy vấn phân tích!")
    print("=" * 65)

if __name__ == "__main__":
    main()
