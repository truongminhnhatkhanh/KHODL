"""
===============================================================================
PHẦN 2: SSIS (SQL SERVER INTEGRATION SERVICES / ETL PIPELINE)
MÔ TẢ: Script tự động hóa toàn bộ quá trình ETL nạp dữ liệu từ Staging sang
       các bảng Dimension và Fact trong Kho Dữ Liệu Lâm Sàng (cdw_hospital_db).
===============================================================================
"""
import subprocess
import sys

MYSQL_PATH = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
MYSQL_USER = "root"
MYSQL_PASSWORD = "nhatkhanh"
DB_NAME = "cdw_hospital_db"

def execute_sql(sql_command, step_name):
    print(f"▶ [ETL STEP] {step_name}...")
    cmd = [MYSQL_PATH, f"-u{MYSQL_USER}", f"-p{MYSQL_PASSWORD}", DB_NAME, "-e", sql_command]
    res = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
    if res.returncode != 0:
        print(f"❌ Lỗi: {res.stderr}")
        return False
    return True

def main():
    print("=" * 65)
    print("🔄 BẮT ĐẦU TIẾN TRÌNH ETL (EXTRACT - TRANSFORM - LOAD)")
    print("=" * 65)

    # 1. Sinh lịch thời gian Dim Date
    if not execute_sql("CALL sp_etl_dim_date('2024-01-01', '2027-12-31');", "1. Sinh chiều thời gian Dim_Date (2024-2027)"):
        sys.exit(1)

    # 2. Xử lý SCD Type 2 cho bệnh nhân (Mã hóa SHA-256)
    if not execute_sql("CALL sp_etl_dim_patient_scd2();", "2. Khử định danh SHA-256 & Xử lý SCD Type 2 (Dim_Patient)"):
        sys.exit(1)

    # 3. Nạp các Dimension danh mục
    if not execute_sql("CALL sp_etl_dim_doctor();", "3. Nạp danh mục Bác sĩ (Dim_Doctor)"):
        sys.exit(1)
    if not execute_sql("CALL sp_etl_dim_facility();", "4. Nạp danh mục Khoa phòng (Dim_Facility)"):
        sys.exit(1)
    if not execute_sql("CALL sp_etl_dim_diagnosis();", "5. Chuẩn hóa mã bệnh ICD-10 (Dim_Diagnosis)"):
        sys.exit(1)
    if not execute_sql("CALL sp_etl_dim_service();", "6. Nạp danh mục Dịch vụ y tế (Dim_Service)"):
        sys.exit(1)

    # 4. Nạp Fact Table
    if not execute_sql("CALL sp_etl_fact_patient_visits();", "7. Ánh xạ Surrogate Key & Nạp bảng sự kiện (Fact_Patient_Visits)"):
        sys.exit(1)

    print("=" * 65)
    print("✅ TIẾN TRÌNH ETL HOÀN TẤT THÀNH CÔNG 100%!")
    print("=" * 65)

if __name__ == "__main__":
    main()
