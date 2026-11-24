-- ============================================================================
-- TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN VÀ TRUYỀN THÔNG VIỆT - HÀN (VKU)
-- KHOA KHOA HỌC MÁY TÍNH - MÔN: KHO DỮ LIỆU (DATA WAREHOUSE)
-- ĐỀ TÀI: DESIGN AND IMPLEMENTATION OF A CLINICAL DATA WAREHOUSE (CDW)
--         FOR OPTIMIZING PATIENT CARE PROCESSES AND HEALTHCARE RESOURCE ALLOCATION
-- NHÓM SINH VIÊN: Trương Minh Nhật Khánh, Lê Thị Hồng Hạnh, Ngô Thị Anh Thư, Lê Hà An
-- GVHD: ThS. Mai Lam
-- SCRIPT: 01_schema_ddl.sql - KHỞI TẠO CƠ SỞ DỮ LIỆU & LƯỢC ĐỒ HÌNH SAO (STAR SCHEMA)
-- ============================================================================

CREATE DATABASE IF NOT EXISTS cdw_hospital_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE cdw_hospital_db;

-- Xóa các bảng cũ nếu đã tồn tại để thiết lập lại môi trường sạch
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS fact_patient_visits;
DROP TABLE IF EXISTS dim_patient;
DROP TABLE IF EXISTS dim_doctor;
DROP TABLE IF EXISTS dim_facility;
DROP TABLE IF EXISTS dim_diagnosis;
DROP TABLE IF EXISTS dim_service;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS stg_hospital_transactions;
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================================
-- 1. BẢNG ĐỆM TRUNG GIAN (STAGING AREA TABLE)
-- Chứa dữ liệu giao dịch thô trích xuất từ các hệ thống HIS, LIS, Viện phí
-- ============================================================================
CREATE TABLE stg_hospital_transactions (
    stg_id INT AUTO_INCREMENT PRIMARY KEY,
    raw_patient_id VARCHAR(50) NOT NULL,
    patient_gender CHAR(1),
    patient_age INT,
    patient_bmi DECIMAL(5,2),
    insurance_tier VARCHAR(50),
    doctor_code VARCHAR(20),
    doctor_name VARCHAR(100),
    doctor_specialty VARCHAR(100),
    doctor_title VARCHAR(50),
    facid VARCHAR(20),
    facility_name VARCHAR(150),
    facility_type VARCHAR(50),
    clinic_room VARCHAR(50),
    division VARCHAR(50),
    vdate DATETIME,
    discharged DATETIME,
    waiting_time_minutes INT,
    consultation_duration INT,
    rcount INT,
    icd10_code VARCHAR(20),
    disease_name VARCHAR(255),
    disease_category VARCHAR(100),
    is_chronic TINYINT DEFAULT 0,
    asthma TINYINT DEFAULT 0,
    irondef TINYINT DEFAULT 0,
    pneum TINYINT DEFAULT 0,
    substancedependence TINYINT DEFAULT 0,
    psychologicaldisordermajor TINYINT DEFAULT 0,
    depress TINYINT DEFAULT 0,
    malnutrition TINYINT DEFAULT 0,
    dialysisrenalendstage TINYINT DEFAULT 0,
    hematocrit DECIMAL(6,2),
    neutrophils DECIMAL(6,2),
    sodium DECIMAL(6,2),
    glucose DECIMAL(6,2),
    bloodureanitro DECIMAL(6,2),
    creatinine DECIMAL(6,2),
    pulse INT,
    respiration INT,
    service_code VARCHAR(20),
    service_name VARCHAR(150),
    service_group VARCHAR(100),
    total_cost DECIMAL(15,2),
    insurance_covered DECIMAL(15,2),
    patient_paid DECIMAL(15,2),
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================================
-- 2. CÁC BẢNG CHIỀU (DIMENSION TABLES)
-- ============================================================================

-- 2.1. Dim_Date: Chiều thời gian đa cấp (Năm, Quý, Tháng, Ngày, Ca trực, Cuối tuần)
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY, -- Định dạng: YYYYMMDD
    full_date DATE NOT NULL UNIQUE,
    day_of_week VARCHAR(15) NOT NULL,
    day_number_in_month INT NOT NULL,
    month_number INT NOT NULL,
    month_name VARCHAR(15) NOT NULL,
    quarter INT NOT NULL,
    year INT NOT NULL,
    is_weekend TINYINT NOT NULL DEFAULT 0, -- 1: Cuối tuần (T7, CN), 0: Ngày thường
    is_holiday TINYINT NOT NULL DEFAULT 0,
    shift_period VARCHAR(20) DEFAULT 'Day Shift' -- 'Morning Shift', 'Afternoon Shift', 'Night Shift'
) ENGINE=InnoDB;

-- 2.2. Dim_Patient: Chiều bệnh nhân (Quản lý lịch sử SCD Type 2 & Ẩn danh hóa SHA-256)
CREATE TABLE dim_patient (
    patient_key INT AUTO_INCREMENT PRIMARY KEY,
    patient_hash_id CHAR(64) NOT NULL, -- SHA-256 đã khử định danh danh tính
    gender CHAR(1) NOT NULL,            -- 'M' hoặc 'F'
    age_group VARCHAR(20) NOT NULL,     -- '<18', '18-35', '36-50', '51-65', '>65'
    bmi_category VARCHAR(30) NOT NULL,  -- 'Underweight', 'Normal', 'Overweight', 'Obese'
    insurance_tier VARCHAR(50) NOT NULL,-- 'BHYT Hộ nghèo', 'BHYT Tiêu chuẩn', 'Khám Dịch vụ'
    start_date DATE NOT NULL,
    end_date DATE NOT NULL DEFAULT '9999-12-31',
    is_current TINYINT NOT NULL DEFAULT 1, -- 1: Bản ghi hiện hành, 0: Bản ghi lịch sử
    INDEX idx_patient_hash (patient_hash_id),
    INDEX idx_patient_active (patient_hash_id, is_current)
) ENGINE=InnoDB;

-- 2.3. Dim_Doctor: Chiều bác sĩ thăm khám và điều trị
CREATE TABLE dim_doctor (
    doctor_key INT AUTO_INCREMENT PRIMARY KEY,
    doctor_code VARCHAR(20) NOT NULL UNIQUE,
    doctor_name VARCHAR(100) NOT NULL,
    specialty VARCHAR(100) NOT NULL,
    academic_title VARCHAR(50) NOT NULL, -- 'BS', 'BS.CKI', 'BS.CKII', 'ThS.BS', 'PGS.TS'
    department_id VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

-- 2.4. Dim_Facility: Chiều cơ sở khám chữa bệnh & Khoa phòng
CREATE TABLE dim_facility (
    facility_key INT AUTO_INCREMENT PRIMARY KEY,
    facility_code VARCHAR(20) NOT NULL UNIQUE,
    facility_name VARCHAR(150) NOT NULL,
    facility_type VARCHAR(50) NOT NULL, -- 'Khoa Khám Bệnh', 'Nội Trú', 'Cấp Cứu', 'ICU', 'Ngoại Phẫu Thuật'
    clinic_room VARCHAR(50),
    division VARCHAR(50) NOT NULL,      -- 'Lâm Sàng', 'Cận Lâm Sàng', 'Dược & Viện Phí'
    planned_beds INT DEFAULT 0          -- Số giường bệnh chỉ tiêu
) ENGINE=InnoDB;

-- 2.5. Dim_Diagnosis: Chiều phân loại bệnh tật theo ICD-10
CREATE TABLE dim_diagnosis (
    diagnosis_key INT AUTO_INCREMENT PRIMARY KEY,
    icd10_code VARCHAR(20) NOT NULL UNIQUE,
    disease_name VARCHAR(255) NOT NULL,
    disease_category VARCHAR(100) NOT NULL, -- 'Hô Hấp', 'Tim Mạch', 'Nội Tiết', 'Thận Niệu', 'Tiêu Hóa'
    chronic_indicator TINYINT NOT NULL DEFAULT 0, -- 1: Mãn tính, 0: Cấp tính
    severity_level VARCHAR(20) DEFAULT 'Moderate' -- 'Mild', 'Moderate', 'Severe', 'Critical'
) ENGINE=InnoDB;

-- 2.6. Dim_Service: Chiều danh mục dịch vụ y tế kỹ thuật
CREATE TABLE dim_service (
    service_key INT AUTO_INCREMENT PRIMARY KEY,
    service_code VARCHAR(20) NOT NULL UNIQUE,
    service_name VARCHAR(150) NOT NULL,
    service_group VARCHAR(100) NOT NULL, -- 'Khám Bệnh', 'Xét Nghiệm Máu', 'Chẩn Đoán Hình Ảnh', 'Thủ Thuật'
    standard_price DECIMAL(15,2) NOT NULL DEFAULT 0.00
) ENGINE=InnoDB;

-- ============================================================================
-- 3. BẢNG SỰ KIỆN TRỌNG TÂM (FACT TABLE: Fact_Patient_Visits)
-- Hạt mịn (Grain): Mỗi dòng đại diện cho 1 lượt khám hoặc 1 đợt điều trị nội trú
-- ============================================================================
CREATE TABLE fact_patient_visits (
    visit_key BIGINT AUTO_INCREMENT PRIMARY KEY,
    
    -- Khóa ngoại liên kết 6 chiều (Surrogate Keys)
    patient_key INT NOT NULL,
    doctor_key INT NOT NULL,
    facility_key INT NOT NULL,
    diagnosis_key INT NOT NULL,
    service_key INT NOT NULL,
    visit_date_key INT NOT NULL,
    discharged_date_key INT NOT NULL,
    
    -- Measures: Đo lường thời gian & Vận hành quy trình
    waiting_time_minutes INT NOT NULL DEFAULT 0,     -- Thời gian chờ khám (phút)
    consultation_duration INT NOT NULL DEFAULT 0,    -- Thời gian bác sĩ khám trực tiếp (phút)
    length_of_stay_days INT NOT NULL DEFAULT 1,      -- Số ngày nằm viện điều trị (LoS)
    prior_visits_count INT NOT NULL DEFAULT 0,       -- Số lần tái khám trước đó trong 180 ngày (rcount)
    
    -- Measures: Các chỉ số xét nghiệm & Dấu hiệu sinh tồn quan trọng
    lab_hematocrit DECIMAL(6,2),
    lab_neutrophils DECIMAL(6,2),
    lab_sodium DECIMAL(6,2),
    lab_glucose DECIMAL(6,2),
    lab_bloodureanitro DECIMAL(6,2),
    lab_creatinine DECIMAL(6,2),
    vital_pulse INT,
    vital_respiration INT,
    
    -- Measures: Cơ cấu tài chính viện phí & Bảo hiểm y tế (VNĐ)
    total_cost DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    insurance_covered_amount DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    patient_paid_amount DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    
    etl_load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ràng buộc toàn vẹn khóa ngoại (Foreign Key Constraints)
    CONSTRAINT fk_fact_patient FOREIGN KEY (patient_key) REFERENCES dim_patient(patient_key),
    CONSTRAINT fk_fact_doctor FOREIGN KEY (doctor_key) REFERENCES dim_doctor(doctor_key),
    CONSTRAINT fk_fact_facility FOREIGN KEY (facility_key) REFERENCES dim_facility(facility_key),
    CONSTRAINT fk_fact_diagnosis FOREIGN KEY (diagnosis_key) REFERENCES dim_diagnosis(diagnosis_key),
    CONSTRAINT fk_fact_service FOREIGN KEY (service_key) REFERENCES dim_service(service_key),
    CONSTRAINT fk_fact_vdate FOREIGN KEY (visit_date_key) REFERENCES dim_date(date_key),
    CONSTRAINT fk_fact_discharged FOREIGN KEY (discharged_date_key) REFERENCES dim_date(date_key)
) ENGINE=InnoDB;

-- ============================================================================
-- 4. TỐI ƯU HÓA CHỈ MỤC TRUY VẤN ĐA CHIỀU (OLAP INDEXING)
-- ============================================================================
CREATE INDEX idx_fact_vdate_perf ON fact_patient_visits(visit_date_key, facility_key);
CREATE INDEX idx_fact_diag_perf ON fact_patient_visits(diagnosis_key, length_of_stay_days);
CREATE INDEX idx_fact_patient_perf ON fact_patient_visits(patient_key);
CREATE INDEX idx_fact_doctor_perf ON fact_patient_visits(doctor_key);

-- ============================================================================
-- 5. LỚP VIEW TỔNG HỢP NGHIỆP VỤ (SEMANTIC & REPORTING VIEWS)
-- ============================================================================

-- View 1: Tổng hợp thời gian chờ và công suất khám theo ngày trong tuần
CREATE OR REPLACE VIEW vw_kpi_wait_time_summary AS
SELECT 
    d.day_of_week,
    d.shift_period,
    f.facility_name,
    COUNT(v.visit_key) AS total_visits,
    ROUND(AVG(v.waiting_time_minutes), 1) AS avg_waiting_minutes,
    ROUND(AVG(v.consultation_duration), 1) AS avg_consultation_minutes,
    MAX(v.waiting_time_minutes) AS max_waiting_minutes
FROM fact_patient_visits v
JOIN dim_date d ON v.visit_date_key = d.date_key
JOIN dim_facility f ON v.facility_key = f.facility_key
GROUP BY d.day_of_week, d.shift_period, f.facility_name;

-- View 2: Tổng hợp hiệu suất giường bệnh và thời gian lưu viện (LoS) theo nhóm bệnh
CREATE OR REPLACE VIEW vw_kpi_los_and_bed_occupancy AS
SELECT 
    diag.disease_category,
    diag.disease_name,
    diag.chronic_indicator,
    f.facility_name,
    COUNT(v.visit_key) AS total_admissions,
    ROUND(AVG(v.length_of_stay_days), 2) AS avg_length_of_stay_days,
    ROUND(AVG(v.lab_glucose), 1) AS avg_blood_glucose,
    ROUND(AVG(v.lab_creatinine), 2) AS avg_creatinine,
    ROUND(SUM(v.total_cost), 0) AS total_clinical_cost,
    ROUND(SUM(v.insurance_covered_amount), 0) AS total_insurance_covered,
    ROUND(SUM(v.patient_paid_amount), 0) AS total_patient_copay
FROM fact_patient_visits v
JOIN dim_diagnosis diag ON v.diagnosis_key = diag.diagnosis_key
JOIN dim_facility f ON v.facility_key = f.facility_key
GROUP BY diag.disease_category, diag.disease_name, diag.chronic_indicator, f.facility_name;
