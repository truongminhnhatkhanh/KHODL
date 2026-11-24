"""
Lab 2-3: ETL Pipeline – Extract, Transform, Load
Phiên bản V2 — Sửa 6 lỗi đánh giá:
  ★ FIX #1: Wait Time theo chuyên khoa (không còn random đều 10–65)
  ★ FIX #2: LOS theo loại điều trị (không còn random đều 2–21)
  ★ FIX #3: Thêm Dim_Service (Outpatient / Inpatient / Surgery / Emergency)
  ★ FIX #4: Tỷ lệ BHYT phân hóa theo nhà bảo hiểm
"""
import hashlib
import os
import sys
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_server_url, get_oltp_url, get_dw_url

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQL_PATH = os.path.join(BASE_DIR, "sql", "02_create_dw.sql")

# ==================================================================
# Cấu hình phân phối theo chuyên khoa & loại điều trị
# ==================================================================

# ★ FIX #1: Wait Time (phút) theo chuyên khoa
WAIT_TIME_RANGES = {
    "Oncology":         (25, 60),
    "Cardiology":       (20, 50),
    "Orthopedics":      (15, 45),
    "Pulmonology":      (15, 45),
    "Endocrinology":    (10, 35),
    "General Medicine": (5,  30),
    "Pediatrics":       (10, 25),
    "Dermatology":      (5,  20),
}

# Thời gian khám (phút) theo chuyên khoa
CONSULT_RANGES = {
    "Oncology":         (20, 45),
    "Cardiology":       (15, 40),
    "Orthopedics":      (15, 35),
    "Pulmonology":      (15, 35),
    "Endocrinology":    (10, 30),
    "General Medicine": (10, 25),
    "Pediatrics":       (15, 30),
    "Dermatology":      (10, 20),
}

# ★ FIX #2: LOS (ngày) theo loại điều trị
LOS_RANGES = {
    "Chemotherapy":           (5, 21),
    "Cardiovascular Therapy": (3, 14),
    "Pulmonary Care":         (2, 10),
    "Orthopedic Therapy":     (3, 15),
    "Endocrine Therapy":      (1,  5),
    "Pediatric Care":         (1,  5),
    "Nutritional Counseling": (0,  0),
    "Dermatologic Treatment": (0,  0),
    "MRI":                    (0,  0),
    "ECG":                    (0,  0),
    "X-Ray":                  (0,  0),
    "Physiotherapy":          (0,  0),
    "General Clinical":       (0,  0),
}

# ★ FIX #3: Service Type xác suất theo treatment
# Mỗi entry: list[(service_type, cumulative_threshold)]
SERVICE_TYPE_MAP = {
    "Chemotherapy":           [("Inpatient",  1.0)],
    "Cardiovascular Therapy": [("Inpatient",  0.65), ("Emergency", 1.0)],
    "Orthopedic Therapy":     [("Surgery",    0.55), ("Inpatient", 1.0)],
    "Pulmonary Care":         [("Inpatient",  0.60), ("Emergency", 1.0)],
    "Endocrine Therapy":      [("Outpatient", 0.75), ("Inpatient", 1.0)],
    "Pediatric Care":         [("Outpatient", 0.65), ("Inpatient", 0.85), ("Emergency", 1.0)],
    "Nutritional Counseling": [("Outpatient", 1.0)],
    "Dermatologic Treatment": [("Outpatient", 1.0)],
    "MRI":                    [("Outpatient", 1.0)],
    "ECG":                    [("Outpatient", 1.0)],
    "X-Ray":                  [("Outpatient", 1.0)],
    "Physiotherapy":          [("Outpatient", 1.0)],
    "General Clinical":       [("Outpatient", 1.0)],
}

# ★ FIX #4: Tỷ lệ bảo hiểm chi trả theo nhà cung cấp
INSURANCE_RATES = {
    "Medicare":           0.80,
    "Cigna":              0.65,
    "UnitedHealthcare":   0.70,
    "Blue Cross":         0.70,
    "Aetna":              0.65,
}


# ==================================================================
# Hàm tiện ích
# ==================================================================

def run_sql_script(engine, filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        statements = [s.strip() for s in f.read().split(";") if s.strip()]
    with engine.begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))


def anonymize_id(val):
    return hashlib.sha256(str(val).encode("utf-8")).hexdigest()[:16]


def get_age_group(dob):
    age = (pd.Timestamp.today() - pd.to_datetime(dob)).days // 365
    if age < 18:   return "0-17"
    if age < 35:   return "18-34"
    if age < 60:   return "35-59"
    return "60+"


def get_shift(hour_val):
    if 6 <= hour_val < 12:   return "Morning"
    if 12 <= hour_val < 18:  return "Afternoon"
    return "Night"


def assign_service_type(treatment_type, rng):
    """Gán loại dịch vụ dựa trên treatment_type với xác suất có trọng số."""
    probs = SERVICE_TYPE_MAP.get(treatment_type, [("Outpatient", 1.0)])
    r = rng.random()
    for stype, threshold in probs:
        if r < threshold:
            return stype
    return "Outpatient"


# ==================================================================
# MAIN
# ==================================================================

def main():
    if sys.stdout.encoding != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 65)
    print("🌟 BƯỚC 2: ETL STAR SCHEMA, KHỬ ĐỊNH DANH SHA-256 & NẠP HOSPITAL_DW")
    print("=" * 65)

    rng = np.random.default_rng(42)

    # --- 0. Kết nối & tạo DW schema ---
    server_engine = create_engine(get_server_url())
    print("▶ Đang tạo database hospital_dw và cấu trúc Star Schema (1 Fact + 6 Dim)...")
    run_sql_script(server_engine, SQL_PATH)
    print("✅ Đã tạo cấu trúc CSDL hospital_dw thành công.")

    oltp_engine = create_engine(get_oltp_url())
    dw_engine   = create_engine(get_dw_url())

    # === EXTRACT ===
    patients     = pd.read_sql("SELECT * FROM patients", oltp_engine)
    doctors      = pd.read_sql("SELECT * FROM doctors", oltp_engine)
    appointments = pd.read_sql("SELECT * FROM appointments", oltp_engine)
    treatments   = pd.read_sql("SELECT * FROM treatments", oltp_engine)
    billing      = pd.read_sql("SELECT * FROM billing", oltp_engine)
    print(f"📥 Extract: {len(patients)} patients, {len(doctors)} doctors, {len(appointments)} appts, {len(treatments)} treats, {len(billing)} bills")

    # === TRANSFORM & LOAD: DIMENSIONS ===

    # --- Dim_Patient ---
    patients["Anonymized_Patient_ID"] = patients["patient_id"].apply(anonymize_id)
    patients["Age_Group"] = patients["date_of_birth"].apply(get_age_group)
    patients["Insurance_Tier"] = patients["insurance_provider"].fillna("Self-Pay")

    dim_patient = patients[["Anonymized_Patient_ID", "Age_Group", "gender", "address", "Insurance_Tier"]] \
        .drop_duplicates(subset=["Anonymized_Patient_ID"])
    dim_patient.columns = ["Anonymized_Patient_ID", "Age_Group", "Gender", "Location", "Insurance_Tier"]
    dim_patient.to_sql("Dim_Patient", dw_engine, if_exists="append", index=False)
    print(f"  Dim_Patient:    {len(dim_patient)} rows")

    # --- Dim_Doctor ---
    doctors["Doctor_Name"] = doctors["first_name"] + " " + doctors["last_name"]
    dim_doctor = doctors[["doctor_id", "Doctor_Name", "specialization", "hospital_branch", "years_experience"]] \
        .drop_duplicates(subset=["doctor_id"])
    dim_doctor.columns = ["Doctor_ID", "Doctor_Name", "Specialty", "Hospital_Branch", "Years_Experience"]
    dim_doctor["Effective_Date"] = pd.to_datetime("2023-01-01").date()
    dim_doctor["End_Date"] = pd.to_datetime("9999-12-31").date()
    dim_doctor["Is_Current"] = 1
    dim_doctor.to_sql("Dim_Doctor", dw_engine, if_exists="append", index=False)
    print(f"  Dim_Doctor:     {len(dim_doctor)} rows")

    # --- Dim_Department ---
    depts = doctors[["specialization"]].drop_duplicates().reset_index(drop=True)
    depts["Department_Name"] = depts["specialization"]
    depts["Clinic_Room"] = ["Room-" + str(101 + i) for i in range(len(depts))]
    depts["Division"] = depts["specialization"].apply(
        lambda x: "Paraclinical" if any(k in str(x).lower() for k in ["radio", "lab", "patho", "diag"]) else "Clinical"
    )
    dim_department = depts[["Department_Name", "Clinic_Room", "Division"]]
    dim_department.to_sql("Dim_Department", dw_engine, if_exists="append", index=False)
    print(f"  Dim_Department: {len(dim_department)} rows")

    # --- Dim_Diagnosis ---
    icd10_map = {
        "Chemotherapy":           ("C80.1", "Oncology & Tumor",          1),
        "Cardiovascular Therapy": ("I10.0", "Cardiovascular Disease",    1),
        "Endocrine Therapy":      ("E11.9", "Endocrinology & Diabetes",  1),
        "Pulmonary Care":         ("J45.9", "Respiratory & Asthma",      1),
        "Orthopedic Therapy":     ("M19.9", "Orthopedics & Joint",       1),
        "Nutritional Counseling": ("E66.9", "Metabolic & Obesity",       1),
        "Pediatric Care":         ("Z00.1", "Pediatrics & Child Health", 0),
        "Dermatologic Treatment": ("L30.9", "Dermatology & Skin Disease",0),
        "MRI":                    ("R90.8", "Diagnostic Imaging",        0),
        "ECG":                    ("I49.9", "Cardiology",                1),
        "Physiotherapy":          ("M54.5", "Musculoskeletal",           1),
        "X-Ray":                  ("S99.9", "Radiology",                 0),
        "General Clinical":       ("Z00.0", "General Medicine",          0),
    }
    diag_df = treatments[["treatment_type"]].drop_duplicates().copy()
    diag_df["ICD10_Code"]        = diag_df["treatment_type"].map(lambda x: icd10_map.get(x, ("Z00.0", "General Clinical", 0))[0])
    diag_df["Disease_Category"]  = diag_df["treatment_type"].map(lambda x: icd10_map.get(x, ("Z00.0", "General Clinical", 0))[1])
    diag_df["Chronic_Indicator"] = diag_df["treatment_type"].map(lambda x: icd10_map.get(x, ("Z00.0", "General Clinical", 0))[2])
    diag_df.columns = ["Treatment_Type", "ICD10_Code", "Disease_Category", "Chronic_Indicator"]
    dim_diagnosis = diag_df[["ICD10_Code", "Treatment_Type", "Disease_Category", "Chronic_Indicator"]]
    dim_diagnosis.to_sql("Dim_Diagnosis", dw_engine, if_exists="append", index=False)
    print(f"  Dim_Diagnosis:  {len(dim_diagnosis)} rows")

    # --- ★ FIX #3: Dim_Service (MỚI) ---
    dim_service = pd.DataFrame([
        {"Service_Code": "SVC01", "Service_Name": "Outpatient Consultation", "Service_Type": "Outpatient"},
        {"Service_Code": "SVC02", "Service_Name": "Inpatient Treatment",     "Service_Type": "Inpatient"},
        {"Service_Code": "SVC03", "Service_Name": "Surgical Procedure",      "Service_Type": "Surgery"},
        {"Service_Code": "SVC04", "Service_Name": "Emergency Treatment",     "Service_Type": "Emergency"},
    ])
    dim_service.to_sql("Dim_Service", dw_engine, if_exists="append", index=False)
    print(f"  Dim_Service:    {len(dim_service)} rows ★")

    # --- Dim_Date ---
    appointments["appointment_date"] = pd.to_datetime(appointments["appointment_date"])
    appointments["hour"] = pd.to_timedelta(appointments["appointment_time"].astype(str)).dt.components["hours"]
    appointments["Shift"] = appointments["hour"].apply(get_shift)
    appointments["Date_Key"] = (
        appointments["appointment_date"].dt.strftime("%Y%m%d").astype(int) * 10
        + appointments["Shift"].map({"Morning": 1, "Afternoon": 2, "Night": 3})
    )

    dim_date = appointments[["Date_Key", "appointment_date", "Shift"]].drop_duplicates(subset=["Date_Key"]).copy()
    dim_date["Full_Date"]   = dim_date["appointment_date"].dt.date
    dim_date["Day_Of_Week"] = dim_date["appointment_date"].dt.day_name()
    dim_date["Month"]       = dim_date["appointment_date"].dt.month
    dim_date["Quarter"]     = dim_date["appointment_date"].dt.quarter
    dim_date["Year"]        = dim_date["appointment_date"].dt.year
    dim_date["Year_Month"]  = dim_date["appointment_date"].dt.strftime("%Y-%m")
    dim_date["Is_Weekend"]  = dim_date["appointment_date"].dt.dayofweek.isin([5, 6]).astype(int)
    dim_date = dim_date[["Date_Key", "Full_Date", "Day_Of_Week", "Month", "Quarter", "Year", "Year_Month", "Shift", "Is_Weekend"]]
    dim_date.to_sql("Dim_Date", dw_engine, if_exists="append", index=False)
    print(f"  Dim_Date:       {len(dim_date)} rows")

    # === BUILD FACT TABLE ===
    db_pat  = pd.read_sql("SELECT Patient_Key, Anonymized_Patient_ID FROM Dim_Patient", dw_engine)
    db_doc  = pd.read_sql("SELECT Doctor_Key, Doctor_ID, Specialty FROM Dim_Doctor WHERE Is_Current = 1", dw_engine)
    db_dept = pd.read_sql("SELECT Department_Key, Department_Name FROM Dim_Department", dw_engine)
    db_diag = pd.read_sql("SELECT Diagnosis_Key, Treatment_Type FROM Dim_Diagnosis", dw_engine)
    db_svc  = pd.read_sql("SELECT Service_Key, Service_Type FROM Dim_Service", dw_engine)

    fact = appointments.merge(treatments, on="appointment_id", how="inner")
    fact = fact.merge(billing, on=["patient_id", "treatment_id"], how="left")
    # Merge patients để lấy insurance_provider cho FIX #4
    fact = fact.merge(patients[["patient_id", "insurance_provider"]], on="patient_id", how="left")

    fact["Anonymized_Patient_ID"] = fact["patient_id"].apply(anonymize_id)
    fact = fact.merge(db_pat,  on="Anonymized_Patient_ID", how="inner")
    fact = fact.merge(db_doc,  left_on="doctor_id",       right_on="Doctor_ID",       how="inner")
    fact = fact.merge(db_dept, left_on="Specialty",        right_on="Department_Name", how="inner")
    fact = fact.merge(db_diag, left_on="treatment_type",   right_on="Treatment_Type",  how="inner")

    # ★ FIX #3: Assign Service_Type → Service_Key
    fact["Service_Type"] = [assign_service_type(tt, rng) for tt in fact["treatment_type"]]
    fact = fact.merge(db_svc, on="Service_Type", how="inner")

    # ★ FIX #1: Wait Time theo chuyên khoa
    fact["Waiting_Time_Minutes"] = 0
    for spec, (lo, hi) in WAIT_TIME_RANGES.items():
        mask = fact["Specialty"] == spec
        n = mask.sum()
        if n > 0:
            fact.loc[mask, "Waiting_Time_Minutes"] = rng.integers(lo, hi + 1, size=n)
    unmatched = fact["Waiting_Time_Minutes"] == 0
    if unmatched.any():
        fact.loc[unmatched, "Waiting_Time_Minutes"] = rng.integers(10, 40, size=unmatched.sum())

    # Consultation Duration theo chuyên khoa
    fact["Consultation_Duration"] = 0
    for spec, (lo, hi) in CONSULT_RANGES.items():
        mask = fact["Specialty"] == spec
        n = mask.sum()
        if n > 0:
            fact.loc[mask, "Consultation_Duration"] = rng.integers(lo, hi + 1, size=n)
    unmatched = fact["Consultation_Duration"] == 0
    if unmatched.any():
        fact.loc[unmatched, "Consultation_Duration"] = rng.integers(10, 30, size=unmatched.sum())

    # ★ FIX #2: LOS theo loại điều trị
    fact["Length_Of_Stay_Days"] = 0
    for tt, (lo, hi) in LOS_RANGES.items():
        if lo == 0 and hi == 0:
            continue
        mask = fact["treatment_type"] == tt
        n = mask.sum()
        if n > 0:
            fact.loc[mask, "Length_Of_Stay_Days"] = rng.integers(lo, hi + 1, size=n)
    # Outpatient → LOS phải = 0
    fact.loc[fact["Service_Type"] == "Outpatient", "Length_Of_Stay_Days"] = 0

    # Total Cost
    fact["Total_Cost"] = fact["amount"].fillna(fact["cost"]).fillna(0)

    # ★ FIX #4: Insurance coverage phân hóa theo nhà bảo hiểm
    fact["coverage_rate"] = fact["insurance_provider"].map(INSURANCE_RATES).fillna(0.0)
    is_insurance = fact["payment_method"].fillna("").str.lower().eq("insurance")
    fact["Insurance_Covered_Amount"] = np.where(
        is_insurance,
        (fact["Total_Cost"] * fact["coverage_rate"]).round(2),
        0.0
    )
    fact["Patient_Paid_Amount"] = (fact["Total_Cost"] - fact["Insurance_Covered_Amount"]).round(2)

    # === LOAD FACT ===
    fact_final = fact[[
        "appointment_id", "Patient_Key", "Doctor_Key", "Department_Key",
        "Date_Key", "Diagnosis_Key", "Service_Key",
        "Waiting_Time_Minutes", "Consultation_Duration",
        "Length_Of_Stay_Days", "Total_Cost", "Insurance_Covered_Amount", "Patient_Paid_Amount"
    ]].drop_duplicates(subset=["appointment_id"])
    fact_final.columns = [
        "Appointment_ID", "Patient_Key", "Doctor_Key", "Department_Key",
        "Date_Key", "Diagnosis_Key", "Service_Key",
        "Waiting_Time_Minutes", "Consultation_Duration",
        "Length_Of_Stay_Days", "Total_Cost", "Insurance_Covered_Amount", "Patient_Paid_Amount"
    ]
    fact_final.to_sql("Fact_Patient_Visits", dw_engine, if_exists="append", index=False)

    # === THỐNG KÊ KẾT QUẢ ===
    print(f"\n✅ Lab 3 ETL V2 completed: {len(fact_final)} rows → Fact_Patient_Visits")

    dept_stats = fact_final.merge(
        pd.read_sql("SELECT Department_Key, Department_Name FROM Dim_Department", dw_engine),
        on="Department_Key"
    )
    print("\n📊 Phân bổ theo Khoa:")
    summary = dept_stats.groupby("Department_Name").agg(
        Visits=("Department_Key", "count"),
        Revenue=("Total_Cost", "sum"),
        Avg_Wait=("Waiting_Time_Minutes", "mean"),
        Avg_LOS=("Length_Of_Stay_Days", "mean"),
    ).sort_values("Visits", ascending=False)
    for dept, row in summary.iterrows():
        pct = row["Visits"] / len(fact_final) * 100
        print(f"  {dept:<22s}  {int(row['Visits']):>5d} ({pct:>5.1f}%)  Revenue: ${row['Revenue']:>12,.2f}  AvgWait: {row['Avg_Wait']:.0f}min  AvgLOS: {row['Avg_LOS']:.1f}d")

    svc_stats = fact_final.merge(
        pd.read_sql("SELECT Service_Key, Service_Type FROM Dim_Service", dw_engine),
        on="Service_Key"
    )
    print("\n📊 Phân bổ theo Loại dịch vụ:")
    svc_summary = svc_stats.groupby("Service_Type").agg(
        Visits=("Service_Key", "count"),
        Revenue=("Total_Cost", "sum"),
    ).sort_values("Visits", ascending=False)
    for svc, row in svc_summary.iterrows():
        pct = row["Visits"] / len(fact_final) * 100
        print(f"  {svc:<12s}  {int(row['Visits']):>5d} ({pct:>5.1f}%)  Revenue: ${row['Revenue']:>12,.2f}")

    print("\n" + "=" * 65)
    print("🎉 HOÀN THÀNH BƯỚC 2! Kho dữ liệu hospital_dw đã được nạp Fact & 6 Dim.")
    print("👉 Bước tiếp theo: hãy chạy `python scripts/03_etl_lab4_advanced.py`")
    print("=" * 65)

if __name__ == "__main__":
    main()
