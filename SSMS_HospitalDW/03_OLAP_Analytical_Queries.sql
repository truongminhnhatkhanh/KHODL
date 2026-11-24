-- ============================================================================
-- TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN VÀ TRUYỀN THÔNG VIỆT - HÀN (VKU)
-- KHOA KHOA HỌC MÁY TÍNH - MÔN: KHO DỮ LIỆU (DATA WAREHOUSE)
-- ĐỀ TÀI: DESIGN AND IMPLEMENTATION OF A CLINICAL DATA WAREHOUSE (CDW)
-- SCRIPT: 04_olap_analytical_queries.sql - TRUY VẤN PHÂN TÍCH ĐA CHIỀU (OLAP)
-- ============================================================================

USE cdw_hospital_db;

-- ============================================================================
-- TRUY VẤN 1 (ROLL-UP / DRILL-DOWN THEO THỜI GIAN)
-- Phân tích xu hướng số lượt khám, thời gian chờ trung bình và doanh thu theo Năm, Quý, Tháng
-- ============================================================================
SELECT 
    d.year,
    d.quarter,
    d.month_number,
    d.month_name,
    COUNT(f.visit_key) AS total_visits,
    ROUND(AVG(f.waiting_time_minutes), 1) AS avg_waiting_time,
    ROUND(AVG(f.consultation_duration), 1) AS avg_consult_duration,
    ROUND(SUM(f.total_cost), 0) AS total_revenue_vnd,
    ROUND(SUM(f.insurance_covered_amount), 0) AS insurance_reimbursed_vnd
FROM fact_patient_visits f
JOIN dim_date d ON f.visit_date_key = d.date_key
GROUP BY d.year, d.quarter, d.month_number, d.month_name
ORDER BY d.year DESC, d.quarter, d.month_number;


-- ============================================================================
-- TRUY VẤN 2 (SLICE & DICE: BỆNH LÝ & KHOA PHÒNG)
-- Thống kê số ca bệnh và độ dài nằm viện (LoS) phân chia theo Khoa và Nhóm bệnh ICD-10
-- ============================================================================
SELECT 
    fac.facility_name,
    diag.disease_category,
    COUNT(f.visit_key) AS case_count,
    ROUND(AVG(f.length_of_stay_days), 2) AS avg_length_of_stay,
    MIN(f.length_of_stay_days) AS min_los,
    MAX(f.length_of_stay_days) AS max_los,
    ROUND(AVG(f.lab_glucose), 1) AS avg_blood_glucose,
    ROUND(AVG(f.lab_creatinine), 2) AS avg_creatinine
FROM fact_patient_visits f
JOIN dim_facility fac ON f.facility_key = fac.facility_key
JOIN dim_diagnosis diag ON f.diagnosis_key = diag.diagnosis_key
GROUP BY fac.facility_name, diag.disease_category
HAVING COUNT(f.visit_key) > 5
ORDER BY fac.facility_name, case_count DESC;


-- ============================================================================
-- TRUY VẤN 3 (MA TRẬN HEATMAP: THỜI GIAN CHỜ KHÁM NGOẠI TRÚ)
-- Tìm kiếm các điểm nghẽn (Bottlenecks) theo Ngày trong tuần và Khung ca trực
-- ============================================================================
SELECT 
    d.day_of_week,
    d.is_weekend,
    COUNT(f.visit_key) AS total_patients,
    ROUND(AVG(f.waiting_time_minutes), 1) AS avg_waiting_minutes,
    SUM(CASE WHEN f.waiting_time_minutes > 60 THEN 1 ELSE 0 END) AS severe_delay_cases,
    ROUND(SUM(CASE WHEN f.waiting_time_minutes > 60 THEN 1 ELSE 0 END) * 100.0 / COUNT(f.visit_key), 2) AS pct_delayed_over_1hr
FROM fact_patient_visits f
JOIN dim_date d ON f.visit_date_key = d.date_key
JOIN dim_facility fac ON f.facility_key = fac.facility_key
WHERE fac.facility_type = 'Khoa Khám Bệnh'
GROUP BY d.day_of_week, d.is_weekend
ORDER BY d.is_weekend, avg_waiting_minutes DESC;


-- ============================================================================
-- TRUY VẤN 4 (PHÂN TÍCH TƯƠNG QUAN BỆNH NỀN VÀ THỜI GIAN NẰM VIỆN LoS)
-- Đánh giá bệnh lý mãn tính ảnh hưởng thế nào đến việc chiếm dụng giường bệnh
-- ============================================================================
SELECT 
    diag.disease_name,
    diag.chronic_indicator,
    diag.severity_level,
    COUNT(f.visit_key) AS patient_volume,
    ROUND(AVG(f.length_of_stay_days), 2) AS avg_los_days,
    ROUND(AVG(f.lab_creatinine), 2) AS avg_creatinine_level,
    ROUND(AVG(f.total_cost), 0) AS avg_treatment_cost
FROM fact_patient_visits f
JOIN dim_diagnosis diag ON f.diagnosis_key = diag.diagnosis_key
WHERE f.length_of_stay_days > 1 -- Chỉ xét bệnh nhân điều trị nội trú
GROUP BY diag.disease_name, diag.chronic_indicator, diag.severity_level
ORDER BY avg_los_days DESC;


-- ============================================================================
-- TRUY VẤN 5 (TỶ LỆ LẤP ĐẦY GIƯỜNG BỆNH THEO KHOA - BED OCCUPANCY RATE)
-- Đánh giá công suất sử dụng giường thực tế so với giường kế hoạch
-- ============================================================================
SELECT 
    fac.facility_name,
    fac.facility_type,
    fac.planned_beds,
    COUNT(f.visit_key) AS total_admissions,
    SUM(f.length_of_stay_days) AS total_inpatient_bed_days,
    ROUND(SUM(f.length_of_stay_days) / (fac.planned_beds * 365.0) * 100, 2) AS estimated_annual_bed_occupancy_pct
FROM fact_patient_visits f
JOIN dim_facility fac ON f.facility_key = fac.facility_key
WHERE fac.planned_beds > 0 AND f.length_of_stay_days > 0
GROUP BY fac.facility_name, fac.facility_type, fac.planned_beds
ORDER BY estimated_annual_bed_occupancy_pct DESC;


-- ============================================================================
-- TRUY VẤN 6 (CƠ CẤU TÀI CHÍNH: BHYT CHI TRẢ VS BỆNH NHÂN ĐỒNG CHI TRẢ)
-- Phân tích tỷ trọng chi phí bảo hiểm theo nhóm chẩn đoán
-- ============================================================================
SELECT 
    diag.disease_category,
    COUNT(f.visit_key) AS treatment_count,
    ROUND(SUM(f.total_cost), 0) AS total_cost_vnd,
    ROUND(SUM(f.insurance_covered_amount), 0) AS insurance_covered_vnd,
    ROUND(SUM(f.patient_paid_amount), 0) AS patient_copay_vnd,
    ROUND(SUM(f.insurance_covered_amount) * 100.0 / NULLIF(SUM(f.total_cost), 0), 2) AS insurance_coverage_pct,
    ROUND(SUM(f.patient_paid_amount) * 100.0 / NULLIF(SUM(f.total_cost), 0), 2) AS patient_copay_pct
FROM fact_patient_visits f
JOIN dim_diagnosis diag ON f.diagnosis_key = diag.diagnosis_key
GROUP BY diag.disease_category
ORDER BY total_cost_vnd DESC;


-- ============================================================================
-- TRUY VẤN 7 (HIỆU SUẤT ĐIỀU TRỊ CỦA BÁC SĨ THEO CHUYÊN KHOA)
-- Phân tích số ca phụ trách, thời gian khám và chi phí điều trị trung bình
-- ============================================================================
SELECT 
    doc.doctor_name,
    doc.specialty,
    doc.academic_title,
    COUNT(f.visit_key) AS total_consultations,
    ROUND(AVG(f.consultation_duration), 1) AS avg_consult_minutes,
    ROUND(AVG(f.waiting_time_minutes), 1) AS avg_patient_wait_time,
    ROUND(AVG(f.total_cost), 0) AS avg_patient_billing
FROM fact_patient_visits f
JOIN dim_doctor doc ON f.doctor_key = doc.doctor_key
GROUP BY doc.doctor_name, doc.specialty, doc.academic_title
ORDER BY total_consultations DESC;


-- ============================================================================
-- TRUY VẤN 8 (PHÂN TÍCH TÁI KHÁM & NGUY CƠ ĐỌC LẠI BỆNH ÁN)
-- Thống kê số lượng bệnh nhân tái khám nhiều lần (rcount >= 2) theo nhóm tuổi và BMI
-- ============================================================================
SELECT 
    p.age_group,
    p.bmi_category,
    COUNT(f.visit_key) AS total_visits,
    SUM(CASE WHEN f.prior_visits_count >= 2 THEN 1 ELSE 0 END) AS frequent_revisit_cases,
    ROUND(SUM(CASE WHEN f.prior_visits_count >= 2 THEN 1 ELSE 0 END) * 100.0 / COUNT(f.visit_key), 2) AS revisit_rate_pct,
    ROUND(AVG(f.length_of_stay_days), 2) AS avg_stay_days
FROM fact_patient_visits f
JOIN dim_patient p ON f.patient_key = p.patient_key
GROUP BY p.age_group, p.bmi_category
ORDER BY revisit_rate_pct DESC;


-- ============================================================================
-- TRUY VẤN 9 (TĂNG TRƯỞNG THEO THỜI GIAN VỚI WINDOW FUNCTION: LAG)
-- So sánh biến động số lượt khám và doanh thu so với tháng liền trước (MoM)
-- ============================================================================
WITH MonthlyAggregates AS (
    SELECT 
        d.year,
        d.month_number,
        d.month_name,
        COUNT(f.visit_key) AS current_visits,
        ROUND(SUM(f.total_cost), 0) AS current_revenue
    FROM fact_patient_visits f
    JOIN dim_date d ON f.visit_date_key = d.date_key
    GROUP BY d.year, d.month_number, d.month_name
)
SELECT 
    year,
    month_number,
    month_name,
    current_visits,
    LAG(current_visits, 1) OVER (ORDER BY year, month_number) AS prev_month_visits,
    current_visits - LAG(current_visits, 1) OVER (ORDER BY year, month_number) AS visit_growth,
    current_revenue,
    LAG(current_revenue, 1) OVER (ORDER BY year, month_number) AS prev_month_revenue,
    ROUND((current_revenue - LAG(current_revenue, 1) OVER (ORDER BY year, month_number)) * 100.0 / 
          NULLIF(LAG(current_revenue, 1) OVER (ORDER BY year, month_number), 0), 2) AS revenue_growth_pct
FROM MonthlyAggregates
ORDER BY year, month_number;


-- ============================================================================
-- TRUY VẤN 10 (PHÂN PHỐI CHỈ SỐ SINH HÓA THEO NHÓM TUỔI)
-- Phân tích Đường huyết (Glucose) và Chức năng lọc thận (Creatinine)
-- ============================================================================
SELECT 
    p.age_group,
    p.gender,
    COUNT(f.visit_key) AS sample_size,
    ROUND(AVG(f.lab_glucose), 2) AS avg_glucose_mg_dl,
    MIN(f.lab_glucose) AS min_glucose,
    MAX(f.lab_glucose) AS max_glucose,
    ROUND(AVG(f.lab_creatinine), 2) AS avg_creatinine_mg_dl,
    ROUND(AVG(f.vital_pulse), 1) AS avg_heart_rate
FROM fact_patient_visits f
JOIN dim_patient p ON f.patient_key = p.patient_key
WHERE f.lab_glucose IS NOT NULL AND f.lab_creatinine IS NOT NULL
GROUP BY p.age_group, p.gender
ORDER BY p.age_group, p.gender;


-- ============================================================================
-- TRUY VẤN 11 (TỔNG HỢP ĐA CHIỀU CÓ PHÂN CẤP VỚI WITH ROLLUP)
-- Tổng hợp số lượt khám và viện phí từ chi tiết Giới tính -> Nhóm tuổi -> Tổng chung
-- ============================================================================
SELECT 
    COALESCE(p.gender, '=== TẤT CẢ GIỚI TÍNH ===') AS gender,
    COALESCE(p.age_group, '--- TẤT CẢ NHÓM TUỔI ---') AS age_group,
    COUNT(f.visit_key) AS total_visits,
    ROUND(AVG(f.length_of_stay_days), 2) AS avg_los,
    ROUND(SUM(f.total_cost), 0) AS total_cost_vnd
FROM fact_patient_visits f
JOIN dim_patient p ON f.patient_key = p.patient_key
GROUP BY p.gender, p.age_group WITH ROLLUP;


-- ============================================================================
-- TRUY VẤN 12 (EXPLAIN QUERY PLAN BENCHMARK: KIỂM CHỨNG TỐI ƯU HÓA INDEX)
-- Kiểm tra kế hoạch thực thi câu truy vấn phân tích lọc theo ngày và khoa phòng
-- ============================================================================
EXPLAIN ANALYZE
SELECT 
    d.month_name,
    fac.facility_name,
    COUNT(f.visit_key) AS visits,
    SUM(f.total_cost) AS revenue
FROM fact_patient_visits f
JOIN dim_date d ON f.visit_date_key = d.date_key
JOIN dim_facility fac ON f.facility_key = fac.facility_key
WHERE d.year = 2026 AND fac.facility_type = 'Nội Trú'
GROUP BY d.month_name, fac.facility_name;
