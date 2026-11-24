import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_server_url, get_oltp_url

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQL_PATH = os.path.join(BASE_DIR, "sql", "01_create_oltp.sql")
DATA_DIR = os.path.join(BASE_DIR, "data")

CSV_TABLES = [
    ("patients.csv", "patients"),
    ("doctors.csv", "doctors"),
    ("appointments.csv", "appointments"),
    ("treatments.csv", "treatments"),
    ("billing.csv", "billing"),
]

def run_sql_script(engine, filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        statements = [s.strip() for s in f.read().split(";") if s.strip()]
    with engine.begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))

def main():
    print("=" * 65)
    print("🏥 BƯỚC 1: KHỞI TẠO VÀ NẠP DỮ LIỆU CSDL VẬN HÀNH (HOSPITAL_OLTP)")
    print("=" * 65)
    merged_path = os.path.join(os.path.dirname(BASE_DIR), "dataset", "healthcare_dataset.csv")

    server_engine = create_engine(get_server_url())
    print("▶ Đang tạo database hospital_oltp và 5 bảng 3NF...")
    run_sql_script(server_engine, SQL_PATH)

    oltp_engine = create_engine(get_oltp_url())

    if os.path.exists(merged_path):
        print(f"📥 Đọc dữ liệu trực tiếp từ: {merged_path}")
        m_df = pd.read_csv(merged_path)

        patients = m_df[['patient_id', 'patient_first_name', 'patient_last_name', 'gender', 'date_of_birth',
                         'patient_phone', 'patient_address', 'registration_date', 'insurance_provider',
                         'insurance_number', 'patient_email']].drop_duplicates(subset=['patient_id']).rename(
            columns={'patient_first_name': 'first_name', 'patient_last_name': 'last_name',
                     'patient_phone': 'contact_number', 'patient_address': 'address', 'patient_email': 'email'})

        doctors = m_df[['doctor_id', 'doctor_first_name', 'doctor_last_name', 'specialization',
                        'doctor_phone', 'years_experience', 'hospital_branch', 'doctor_email']].drop_duplicates(subset=['doctor_id']).rename(
            columns={'doctor_first_name': 'first_name', 'doctor_last_name': 'last_name',
                     'doctor_phone': 'phone_number', 'doctor_email': 'email'})

        appointments = m_df[['appointment_id', 'patient_id', 'doctor_id', 'appointment_date',
                             'appointment_time', 'reason_for_visit', 'appointment_status']].rename(
            columns={'appointment_status': 'status'})

        treatments = m_df[['treatment_id', 'appointment_id', 'treatment_type',
                           'treatment_description', 'treatment_cost', 'treatment_date']].rename(
            columns={'treatment_description': 'description', 'treatment_cost': 'cost'})

        billing = m_df[['bill_id', 'patient_id', 'treatment_id', 'bill_date',
                        'billing_amount', 'payment_method', 'payment_status']].rename(
            columns={'billing_amount': 'amount'})

        # Chuẩn hóa định dạng ngày về YYYY-MM-DD tương thích MySQL DATE
        patients['date_of_birth'] = pd.to_datetime(patients['date_of_birth'], format='mixed').dt.strftime('%Y-%m-%d')
        patients['registration_date'] = pd.to_datetime(patients['registration_date'], format='mixed').dt.strftime('%Y-%m-%d')
        appointments['appointment_date'] = pd.to_datetime(appointments['appointment_date'], format='mixed').dt.strftime('%Y-%m-%d')
        treatments['treatment_date'] = pd.to_datetime(treatments['treatment_date'], format='mixed').dt.strftime('%Y-%m-%d')
        billing['bill_date'] = pd.to_datetime(billing['bill_date'], format='mixed').dt.strftime('%Y-%m-%d')

        tables = [
            ("patients", patients),
            ("doctors", doctors),
            ("appointments", appointments),
            ("treatments", treatments),
            ("billing", billing),
        ]
        for table_name, df in tables:
            df.columns = [c.strip().lower() for c in df.columns]
            df.to_sql(table_name, oltp_engine, if_exists="append", index=False)
            csv_out = os.path.join(DATA_DIR, f"{table_name}.csv")
            df.to_csv(csv_out, index=False)
            print(f"  [OK] Đã nạp {len(df):>5d} dòng vào hospital_oltp.{table_name:<15s} & cập nhật data/{table_name}.csv")

    else:
        missing = [csv for csv, _ in CSV_TABLES if not os.path.exists(os.path.join(DATA_DIR, csv))]
        if missing:
            raise FileNotFoundError(f"Missing CSV files: {', '.join(missing)}")

        for csv_file, table_name in CSV_TABLES:
            df = pd.read_csv(os.path.join(DATA_DIR, csv_file))
            df.columns = [c.strip().lower() for c in df.columns]
            df.to_sql(table_name, oltp_engine, if_exists="append", index=False)
            print(f"  [OK] Đã nạp {len(df):>5d} dòng vào hospital_oltp.{table_name}")

    print("\n" + "=" * 65)
    print("🎉 HOÀN THÀNH BƯỚC 1! CSDL hospital_oltp đã sẵn sàng 100%.")
    print("👉 Bước tiếp theo: hãy chạy `python scripts/02_etl_lab3_initial.py`")
    print("=" * 65)

if __name__ == "__main__":
    main()
