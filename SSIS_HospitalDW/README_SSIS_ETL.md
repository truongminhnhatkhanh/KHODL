# 🔄 SSIS_HospitalDW: QUY TRÌNH ETL (EXTRACT - TRANSFORM - LOAD)
> **HỌC PHẦN: KHO DỮ LIỆU (DATA WAREHOUSE) – VKU**  
> **TƯƠNG ỨNG: PHÂN HỆ SSIS (SQL SERVER INTEGRATION SERVICES / ETL PIPELINE)**

---

## 1. MỤC TIÊU CỦA PHÂN HỆ ETL (SSIS)
Phân hệ này chịu trách nhiệm trích xuất dữ liệu thô từ hệ thống tác nghiệp/tệp dữ liệu nguồn (`dataset/healthcare_dataset.csv`), đưa vào vùng đệm trung gian (`stg_hospital_transactions`), thực hiện các thao tác làm sạch, chuẩn hóa, bảo mật y tế và nạp vào mô hình hình sao (Star Schema).

---

## 2. LUỒNG ĐIỀU KHIỂN TỔNG THỂ (CONTROL FLOW)

```text
[Bắt đầu]
   │
   ▼
[Task 1: Generate Dim_Date] ─────────► Tự động sinh lịch 1.462 ngày (2024-2027), cờ cuối tuần, ngày lễ VN
   │
   ▼
[Task 2: Ingest Staging Data] ───────► Nạp dữ liệu giao dịch thô vào bảng đệm (Staging)
   │
   ▼
[Task 3: Dimension ETL Sub-flow] ────► Nạp đồng thời các Dimension:
   │                                   • Dim_Doctor (Bác sĩ, Chuyên khoa)
   │                                   • Dim_Facility (Khoa phòng, Giường kế hoạch)
   │                                   • Dim_Diagnosis (Ánh xạ chuẩn mã ICD-10)
   │                                   • Dim_Service (Nhóm dịch vụ kỹ thuật y tế)
   ▼
[Task 4: Patient SCD Type 2] ────────► Khử định danh SHA-256 có Salt + Theo dõi lịch sử bảo hiểm SCD Type 2
   │
   ▼
[Task 5: Fact Table ETL Data Flow] ──► Lookup các khóa Surrogate Key, làm sạch ngoại lai, nạp Fact_Patient_Visits
   │
   ▼
[Hoàn tất ETL]
```

---

## 3. CÁC THAO TÁC BIẾN ĐỔI CHÍNH (DATA FLOW TRANSFORMATIONS)

1. **Khử định danh bảo mật (Data Masking / Hashing via SHA-256):**
   * Tuân thủ tiêu chuẩn bảo mật y tế HIPAA & Thông tư 46/2018/TT-BYT.
   * `Patient_Hash_ID` = `SHA2(CONCAT(raw_patient_id, '_', 'VKU_CDW_2026_SECRET_KEY'), 256)`.
2. **Quản lý biến động dữ liệu lịch sử (Slowly Changing Dimension - SCD Type 2):**
   * Khi thông tin diện bảo hiểm thay đổi: Bản ghi cũ được chốt `end_date = CURRENT_DATE - 1`, `is_current = 0`; Bản ghi mới được tạo với `is_current = 1` và `start_date = CURRENT_DATE`.
3. **Làm sạch giá trị ngoại lai (Data Cleansing & Imputation):**
   * Chỉ số đường huyết (Glucose): Lọc bỏ các giá trị âm hoặc lớn bất thường ($> 1.000$), thay bằng trung vị lâm sàng ($110.0\text{ mg/dL}$).
   * Thời gian nằm viện ($LoS$): Tính toán $\text{DATEDIFF}(discharged, vdate)$, tối thiểu 1 ngày cho bệnh nhân nội trú.
4. **Ánh xạ khóa thay thế (Surrogate Key Lookup):**
   * Phép `INNER JOIN` giữa bảng Staging với các bảng Dimension hiện hành (`is_current = 1`) để lấy các khóa số nguyên (`patient_key`, `doctor_key`, `facility_key`, `diagnosis_key`, `service_key`, `visit_date_key`).

---

## 4. CÁCH THỰC THI
Chạy script tự động hóa tại thư mục này:
```bash
python run_etl_pipeline.py
```
Hoặc thực thi Stored Procedure master trong MySQL:
```sql
USE cdw_hospital_db;
CALL sp_run_full_cdw_etl();
```
