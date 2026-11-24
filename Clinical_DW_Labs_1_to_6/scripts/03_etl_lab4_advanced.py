import os
import sys
from datetime import date
import pandas as pd
from sqlalchemy import create_engine, text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_oltp_url, get_dw_url

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCEL_PATH = os.path.join(BASE_DIR, "data", "doctors_update.xlsx")

def main():
    print("=" * 65)
    print("🔄 BƯỚC 3: HỢP NHẤT STAGING & CẬP NHẬT BIẾN ĐỘNG SCD TYPE 2 (LAB 4)")
    print("=" * 65)
    oltp_engine = create_engine(get_oltp_url())
    dw_engine = create_engine(get_dw_url())

    df_sql = pd.read_sql(
        "SELECT doctor_id, CONCAT(first_name, ' ', last_name) AS Doctor_Name, specialization, hospital_branch, years_experience FROM doctors",
        oltp_engine
    )
    df_sql.columns = ["Doctor_ID", "Doctor_Name", "Specialty", "Hospital_Branch", "Years_Experience"]
    df_sql["Source_System"] = "MySQL_OLTP"

    df_excel = pd.read_excel(EXCEL_PATH, sheet_name="Sheet1")
    df_excel["Source_System"] = "HR_Excel_Update"

    df_staging = pd.concat([df_excel, df_sql], ignore_index=True)
    df_staging = df_staging.drop_duplicates(subset=["Doctor_ID"], keep="first")

    with dw_engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE Staging_Doctors"))
    df_staging.to_sql("Staging_Doctors", dw_engine, if_exists="append", index=False)

    current_dim = pd.read_sql("SELECT * FROM Dim_Doctor WHERE Is_Current = 1", dw_engine)
    merged = df_staging.merge(current_dim, on="Doctor_ID", how="left", suffixes=("_new", "_old"))

    today = date.today()
    inserted = 0
    updated_scd2 = 0

    with dw_engine.begin() as conn:
        for _, row in merged.iterrows():
            if pd.isna(row["Doctor_Key"]):
                conn.execute(text(
                    "INSERT INTO Dim_Doctor (Doctor_ID, Doctor_Name, Specialty, Hospital_Branch, Years_Experience, Effective_Date, End_Date, Is_Current) "
                    "VALUES (:id, :name, :spec, :branch, :exp, :eff, '9999-12-31', 1)"
                ), {
                    "id": row["Doctor_ID"],
                    "name": row["Doctor_Name_new"],
                    "spec": row["Specialty_new"],
                    "branch": row["Hospital_Branch_new"],
                    "exp": int(row["Years_Experience_new"]),
                    "eff": today
                })
                inserted += 1
            elif row["Specialty_new"] != row["Specialty_old"] or row["Hospital_Branch_new"] != row["Hospital_Branch_old"]:
                conn.execute(text(
                    "UPDATE Dim_Doctor SET End_Date = :end_dt, Is_Current = 0 WHERE Doctor_Key = :key"
                ), {"end_dt": today, "key": int(row["Doctor_Key"])})

                conn.execute(text(
                    "INSERT INTO Dim_Doctor (Doctor_ID, Doctor_Name, Specialty, Hospital_Branch, Years_Experience, Effective_Date, End_Date, Is_Current) "
                    "VALUES (:id, :name, :spec, :branch, :exp, :eff, '9999-12-31', 1)"
                ), {
                    "id": row["Doctor_ID"],
                    "name": row["Doctor_Name_new"],
                    "spec": row["Specialty_new"],
                    "branch": row["Hospital_Branch_new"],
                    "exp": int(row["Years_Experience_new"]),
                    "eff": today
                })
                updated_scd2 += 1

    print(f"  [OK] Đã nạp Staging: {len(df_staging)} bác sĩ | Thêm mới: {inserted} | Cập nhật SCD-2: {updated_scd2}")

    print("\n" + "=" * 65)
    print("🎉 HOÀN THÀNH BƯỚC 3! Toàn bộ 2 CSDL hospital_oltp và hospital_dw đã sẵn sàng.")
    print("👉 Bây giờ bạn có thể:")
    print("   1. Mở MySQL Workbench chạy file `sql/03_olap_and_benchmark.sql` (Lab 5).")
    print("   2. Mở Power BI Desktop kết nối `hospital_dw` để dựng Dashboard (Lab 6).")
    print("=" * 65)

if __name__ == "__main__":
    main()
