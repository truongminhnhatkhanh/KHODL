"""
===============================================================================
TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN VÀ TRUYỀN THÔNG VIỆT - HÀN (VKU)
KHOA KHOA HỌC MÁY TÍNH - MÔN: KHO DỮ LIỆU (DATA WAREHOUSE)
SCRIPT: generate_bulk_data.py - SINH DỮ LIỆU LÂM SÀNG SỐ LƯỢNG LỚN (BULK SEEDING)
Mục đích: Tự động tạo 10.000 - 50.000 bản ghi giao dịch lâm sàng thực tế,
          phục vụ kiểm thử tải và đo chuẩn hiệu năng (Performance Benchmarking).
===============================================================================
"""

import random
import os
import sys
from datetime import datetime, timedelta

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

NUM_RECORDS = 5000  # Có thể tăng lên 50,000 tùy nhu cầu kiểm thử

DIAGNOSES = [
    ("I10", "Tăng huyết áp vô căn (nguyên phát)", "Tim Mạch", 1, "Moderate"),
    ("I20", "Cơn đau thắt ngực ổn định", "Tim Mạch", 1, "Severe"),
    ("I50", "Suy tim sung huyết mạn tính", "Tim Mạch", 1, "Critical"),
    ("J45", "Hen phế quản thể dị ứng (Asthma)", "Hô Hấp", 1, "Moderate"),
    ("J18", "Viêm phổi mắc phải cộng đồng", "Hô Hấp", 0, "Severe"),
    ("J44", "Bệnh phổi tắc nghẽn mạn tính (COPD)", "Hô Hấp", 1, "Severe"),
    ("E11", "Đái tháo đường type 2 không phụ thuộc Insulin", "Nội Tiết", 1, "Moderate"),
    ("N18", "Bệnh thận mạn giai đoạn cuối (ESRD)", "Thận Niệu", 1, "Critical"),
    ("N20", "Sỏi thận và sỏi niệu quản", "Thận Niệu", 0, "Mild"),
    ("K29", "Viêm loét dạ dày - tá tràng do HP", "Tiêu Hóa", 1, "Mild"),
    ("K70", "Bệnh gan do rượu mạn tính", "Tiêu Hóa", 1, "Moderate"),
    ("S06", "Chấn thương sọ não kín sau tai nạn", "Ngoại Khoa", 0, "Critical"),
    ("M54", "Thoát vị đĩa đệm cột sống thắt lưng", "Cơ Xương Khớp", 1, "Moderate"),
    ("F32", "Rối loạn trầm cảm mức độ vừa", "Tâm Thần", 1, "Moderate"),
    ("Z00", "Khám kiểm tra sức khỏe tổng quát", "Kiểm Tra Tổng Quát", 0, "Mild")
]

FACILITIES = [
    ("FAC_OUTPAT", "Khoa Khám Bệnh Ngoại Trú", "Khoa Khám Bệnh", "Lâm Sàng", 10),
    ("FAC_EMERG", "Khoa Cấp Cứu Tổng Hợp", "Cấp Cứu", "Lâm Sàng", 40),
    ("FAC_CARDIO", "Khoa Tim Mạch Can Thiệp", "Nội Trú", "Lâm Sàng", 80),
    ("FAC_RESPIR", "Khoa Nội Hô Hấp", "Nội Trú", "Lâm Sàng", 70),
    ("FAC_NEPHRO", "Khoa Thận - Lọc Máu", "Nội Trú", "Lâm Sàng", 50),
    ("FAC_SURG", "Khoa Ngoại Phẫu Thuật Gây Mê", "Ngoại Phẫu Thuật", "Lâm Sàng", 60),
    ("FAC_ICU", "Khoa Hồi Sức Tích Cực (ICU)", "ICU", "Lâm Sàng", 30)
]

DOCTORS = [
    ("DOC_001", "BS.CKII Nguyễn Văn Tuấn", "Tim Mạch", "BS.CKII", "FAC_CARDIO"),
    ("DOC_002", "ThS.BS Trần Thị Mai", "Cấp Cứu", "ThS.BS", "FAC_EMERG"),
    ("DOC_003", "PGS.TS Lê Hoàng Nam", "Thận Tiết Niệu", "PGS.TS", "FAC_NEPHRO"),
    ("DOC_004", "BS.CKI Đặng Thu Hà", "Nội Tiết", "BS.CKI", "FAC_OUTPAT"),
    ("DOC_005", "ThS.BS Phạm Quốc Hùng", "Hô Hấp", "ThS.BS", "FAC_RESPIR"),
    ("DOC_006", "BS.CKII Vũ Đình Long", "Ngoại Thần Kinh", "BS.CKII", "FAC_SURG"),
    ("DOC_007", "ThS.BS Đỗ Minh Trí", "Hồi Sức Cấp Cứu", "ThS.BS", "FAC_ICU"),
    ("DOC_008", "BS.CKI Hồ Văn Tiến", "Tiêu Hóa", "BS.CKI", "FAC_OUTPAT"),
    ("DOC_009", "ThS.BS Bùi Bích Phương", "Tâm Lý Lâm Sàng", "ThS.BS", "FAC_OUTPAT"),
    ("DOC_010", "BS Nguyễn Văn Hải", "Đa Khoa Ngoại Trú", "BS", "FAC_OUTPAT")
]

SERVICES = [
    ("SRV_EXAM_OUT", "Khám chuyên khoa ngoại trú", "Khám Bệnh", 150000.00),
    ("SRV_EMERG_CARE", "Xử trí cấp cứu ban đầu", "Khám Bệnh", 850000.00),
    ("SRV_INPAT_TREAT", "Điều trị nội trú chuyên sâu", "Nội Trú", 15000000.00),
    ("SRV_HEMODIALYSIS", "Lọc máu chạy thận nhân tạo", "Thủ Thuật", 22000000.00),
    ("SRV_SURG_MAJOR", "Phẫu thuật chuyên khoa loại 1", "Thủ Thuật", 35000000.00),
    ("SRV_ICU_CARE", "Hồi sức tích cực thở máy", "Nội Trú", 45000000.00),
    ("SRV_EXAM_VIP", "Gói tầm soát sức khỏe toàn diện VIP", "Khám Bệnh", 3500000.00)
]

INSURANCE_TIERS = ["BHYT Tiêu chuẩn", "BHYT Hộ nghèo", "Khám Dịch vụ"]

def generate_sql():
    start_time = datetime(2025, 1, 1)
    end_time = datetime(2026, 10, 1)
    delta_days = (end_time - start_time).days

    output_path = os.path.join(os.path.dirname(__file__), "02_Seed_Data.sql")
    print(f"[INFO] Đang sinh {NUM_RECORDS} bản ghi lâm sàng ngẫu nhiên...")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("-- ============================================================================\n")
        f.write("-- DỮ LIỆU LÂM SÀNG SINH TỰ ĐỘNG PHỤC VỤ BENCHMARK (BULK CLINICAL SEED DATA)\n")
        f.write("-- ============================================================================\n\n")
        f.write("USE cdw_hospital_db;\n\n")
        f.write("INSERT INTO stg_hospital_transactions (\n")
        f.write("    raw_patient_id, patient_gender, patient_age, patient_bmi, insurance_tier,\n")
        f.write("    doctor_code, doctor_name, doctor_specialty, doctor_title,\n")
        f.write("    facid, facility_name, facility_type, clinic_room, division,\n")
        f.write("    vdate, discharged, waiting_time_minutes, consultation_duration, rcount,\n")
        f.write("    icd10_code, disease_name, disease_category, is_chronic,\n")
        f.write("    asthma, irondef, pneum, substancedependence, psychologicaldisordermajor, depress, malnutrition, dialysisrenalendstage,\n")
        f.write("    hematocrit, neutrophils, sodium, glucose, bloodureanitro, creatinine, pulse, respiration,\n")
        f.write("    service_code, service_name, service_group, total_cost, insurance_covered, patient_paid\n")
        f.write(") VALUES\n")

        rows = []
        for i in range(1, NUM_RECORDS + 1):
            pat_id = f"PAT_{random.randint(1000, 3500):05d}"
            gender = random.choice(["M", "F"])
            age = random.choices([random.randint(1, 17), random.randint(18, 50), random.randint(51, 85)], weights=[0.1, 0.45, 0.45])[0]
            bmi = round(random.gauss(24.0, 4.0), 1)
            insurance = random.choices(INSURANCE_TIERS, weights=[0.70, 0.15, 0.15])[0]

            diag = random.choice(DIAGNOSES)
            icd10, disease_name, disease_cat, is_chronic, severity = diag

            doc = random.choice(DOCTORS)
            fac = next(f for f in FACILITIES if f[0] == doc[4])

            # Random visit date
            rand_day = random.randint(0, delta_days)
            rand_hour = random.randint(6, 21)
            rand_min = random.randint(0, 59)
            vdate = start_time + timedelta(days=rand_day, hours=rand_hour, minutes=rand_min)

            # Length of Stay based on facility
            if fac[2] == "Khoa Khám Bệnh":
                los_days = 0
                discharged = vdate + timedelta(hours=random.randint(2, 4))
                srv = SERVICES[0] if insurance != "Khám Dịch vụ" else SERVICES[6]
                waiting_time = random.randint(15, 95)
                consult_dur = random.randint(8, 25)
            elif fac[2] == "Cấp Cứu":
                los_days = random.randint(1, 3)
                discharged = vdate + timedelta(days=los_days)
                srv = SERVICES[1]
                waiting_time = random.randint(0, 15)
                consult_dur = random.randint(20, 50)
            elif fac[2] == "ICU":
                los_days = random.randint(5, 20)
                discharged = vdate + timedelta(days=los_days)
                srv = SERVICES[5]
                waiting_time = 0
                consult_dur = random.randint(30, 60)
            else:
                los_days = random.randint(3, 14)
                discharged = vdate + timedelta(days=los_days)
                srv = SERVICES[2] if fac[0] != "FAC_NEPHRO" else SERVICES[3]
                waiting_time = random.randint(10, 45)
                consult_dur = random.randint(15, 30)

            rcount = random.choices([0, 1, 2, 3, 4, 5], weights=[0.5, 0.25, 0.12, 0.08, 0.03, 0.02])[0]

            # Disease flags
            asthma = 1 if icd10 == "J45" or (age < 20 and random.random() < 0.15) else 0
            dialysis = 1 if icd10 == "N18" or (age > 60 and random.random() < 0.1) else 0
            pneum = 1 if icd10 in ["J18", "J44"] else 0
            irondef = 1 if random.random() < 0.12 else 0
            malnutrition = 1 if (bmi < 18.5 and random.random() < 0.3) else 0
            depress = 1 if icd10 == "F32" or random.random() < 0.08 else 0
            substance = 1 if random.random() < 0.04 else 0
            psych = 1 if depress or random.random() < 0.03 else 0

            # Lab tests
            hematocrit = round(random.gauss(38.0, 5.0), 1)
            neutrophils = round(random.gauss(62.0, 12.0), 1)
            sodium = round(random.gauss(138.0, 4.0), 1)
            glucose = round(random.gauss(115.0 if icd10 != "E11" else 190.0, 25.0), 1)
            bun = round(random.gauss(18.0 if dialysis == 0 else 45.0, 8.0), 1)
            creatinine = round(random.gauss(1.0 if dialysis == 0 else 4.8, 0.5), 2)
            pulse = random.randint(60, 115)
            respiration = random.randint(14, 28)

            # Finances
            base_cost = srv[3] * (1 + (los_days * 0.4 if los_days > 0 else 0))
            total_cost = round(base_cost * random.uniform(0.9, 1.25), 2)
            if insurance == "BHYT Hộ nghèo":
                ins_covered = total_cost
                pat_paid = 0.0
            elif insurance == "BHYT Tiêu chuẩn":
                ins_covered = round(total_cost * 0.80, 2)
                pat_paid = round(total_cost * 0.20, 2)
            else:
                ins_covered = 0.0
                pat_paid = total_cost

            vdate_str = vdate.strftime("%Y-%m-%d %H:%M:%S")
            discharged_str = discharged.strftime("%Y-%m-%d %H:%M:%S")

            row_str = (
                f"('{pat_id}', '{gender}', {age}, {bmi}, '{insurance}', "
                f"'{doc[0]}', '{doc[1]}', '{doc[2]}', '{doc[3]}', "
                f"'{fac[0]}', '{fac[1]}', '{fac[2]}', 'Phòng {random.randint(101, 505)}', '{fac[3]}', "
                f"'{vdate_str}', '{discharged_str}', {waiting_time}, {consult_dur}, {rcount}, "
                f"'{icd10}', '{disease_name}', '{disease_cat}', {is_chronic}, "
                f"{asthma}, {irondef}, {pneum}, {substance}, {psych}, {depress}, {malnutrition}, {dialysis}, "
                f"{hematocrit}, {neutrophils}, {sodium}, {glucose}, {bun}, {creatinine}, {pulse}, {respiration}, "
                f"'{srv[0]}', '{srv[1]}', '{srv[2]}', {total_cost}, {ins_covered}, {pat_paid})"
            )
            rows.append(row_str)

        f.write(",\n".join(rows))
        f.write(";\n\n")
        f.write("SELECT CONCAT('[SUCCESS] Đã nạp thành công ', COUNT(*), ' bản ghi vào stg_hospital_transactions!') FROM stg_hospital_transactions;\n")

    print(f"[SUCCESS] Đã xuất thành công tệp: {output_path} ({NUM_RECORDS} bản ghi).")

if __name__ == "__main__":
    generate_sql()
