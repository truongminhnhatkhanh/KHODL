-- ============================================================================
-- TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN VÀ TRUYỀN THÔNG VIỆT - HÀN (VKU)
-- KHOA KHOA HỌC MÁY TÍNH - MÔN: KHO DỮ LIỆU (DATA WAREHOUSE)
-- ĐỀ TÀI: DESIGN AND IMPLEMENTATION OF A CLINICAL DATA WAREHOUSE (CDW)
-- SCRIPT: 03_etl_pipeline.sql - CÁC STORED PROCEDURES THỰC HIỆN ETL TỰ ĐỘNG
-- ============================================================================

USE cdw_hospital_db;

DELIMITER $$

-- ============================================================================
-- THỦ TỤC 1: sp_etl_dim_date
-- Tự động sinh dữ liệu lịch đa chiều trong khoảng thời gian xác định (2024 - 2027)
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_etl_dim_date$$
CREATE PROCEDURE sp_etl_dim_date(IN p_start_date DATE, IN p_end_date DATE)
BEGIN
    DECLARE v_cur_date DATE;
    DECLARE v_date_key INT;
    DECLARE v_day_name VARCHAR(15);
    DECLARE v_day_num INT;
    DECLARE v_month_num INT;
    DECLARE v_month_name VARCHAR(15);
    DECLARE v_quarter INT;
    DECLARE v_year INT;
    DECLARE v_is_weekend TINYINT;
    DECLARE v_is_holiday TINYINT;

    SET v_cur_date = p_start_date;

    WHILE v_cur_date <= p_end_date DO
        SET v_date_key = YEAR(v_cur_date) * 10000 + MONTH(v_cur_date) * 100 + DAY(v_cur_date);
        SET v_day_name = DAYNAME(v_cur_date);
        SET v_day_num = DAY(v_cur_date);
        SET v_month_num = MONTH(v_cur_date);
        SET v_month_name = MONTHNAME(v_cur_date);
        SET v_quarter = QUARTER(v_cur_date);
        SET v_year = YEAR(v_cur_date);
        
        -- Xác định ngày cuối tuần (Thứ 7 = 7, Chủ Nhật = 1)
        IF DAYOFWEEK(v_cur_date) IN (1, 7) THEN
            SET v_is_weekend = 1;
        ELSE
            SET v_is_weekend = 0;
        END IF;

        -- Xác định các ngày nghỉ lễ trọng đại tại Việt Nam (Tết Dương Lịch, Quốc Khánh,...)
        IF (v_month_num = 1 AND v_day_num = 1) OR
           (v_month_num = 4 AND v_day_num = 30) OR
           (v_month_num = 5 AND v_day_num = 1) OR
           (v_month_num = 9 AND v_day_num = 2) THEN
            SET v_is_holiday = 1;
        ELSE
            SET v_is_holiday = 0;
        END IF;

        INSERT INTO dim_date (
            date_key, full_date, day_of_week, day_number_in_month,
            month_number, month_name, quarter, year, is_weekend, is_holiday, shift_period
        )
        VALUES (
            v_date_key, v_cur_date, v_day_name, v_day_num,
            v_month_num, v_month_name, v_quarter, v_year, v_is_weekend, v_is_holiday, 'Standard Day'
        )
        ON DUPLICATE KEY UPDATE full_date = v_cur_date;

        SET v_cur_date = DATE_ADD(v_cur_date, INTERVAL 1 DAY);
    END WHILE;
    
    -- Thêm bản ghi đặc biệt cho ngày chưa xác định (Unknown Date)
    INSERT INTO dim_date (
        date_key, full_date, day_of_week, day_number_in_month,
        month_number, month_name, quarter, year, is_weekend, is_holiday, shift_period
    )
    VALUES (99991231, '9999-12-31', 'Unknown', 0, 0, 'Unknown', 0, 9999, 0, 0, 'Unknown')
    ON DUPLICATE KEY UPDATE full_date = '9999-12-31';

    SELECT CONCAT('[SUCCESS] Sinh thành công dữ liệu dim_date từ ', p_start_date, ' đến ', p_end_date) AS log_message;
END$$

-- ============================================================================
-- THỦ TỤC 2: sp_etl_dim_patient_scd2
-- Thực hiện băm ẩn danh SHA-256 danh tính và quản lý lịch sử SCD Type 2
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_etl_dim_patient_scd2$$
CREATE PROCEDURE sp_etl_dim_patient_scd2()
BEGIN
    DECLARE v_salt VARCHAR(50);
    SET v_salt = 'VKU_CLINICAL_SALT_TOKEN_2026';

    -- 1. Cập nhật đóng bản ghi cũ (SCD Type 2 Expiry) nếu có sự thay đổi bảo hiểm hoặc BMI
    UPDATE dim_patient p
    INNER JOIN stg_hospital_transactions s 
        ON p.patient_hash_id = SHA2(CONCAT(s.raw_patient_id, '_', v_salt), 256)
        AND p.is_current = 1
    SET p.end_date = DATE_SUB(DATE(s.vdate), INTERVAL 1 DAY),
        p.is_current = 0
    WHERE p.insurance_tier <> s.insurance_tier;

    -- 2. Thêm bản ghi mới cho bệnh nhân mới hoặc phiên bản mới (SCD 2 Insert)
    INSERT INTO dim_patient (
        patient_hash_id, gender, age_group, bmi_category, insurance_tier, start_date, end_date, is_current
    )
    SELECT DISTINCT
        SHA2(CONCAT(s.raw_patient_id, '_', v_salt), 256) AS patient_hash_id,
        COALESCE(s.patient_gender, 'U') AS gender,
        CASE 
            WHEN s.patient_age < 18 THEN '<18'
            WHEN s.patient_age BETWEEN 18 AND 35 THEN '18-35'
            WHEN s.patient_age BETWEEN 36 AND 50 THEN '36-50'
            WHEN s.patient_age BETWEEN 51 AND 65 THEN '51-65'
            ELSE '>65'
        END AS age_group,
        CASE 
            WHEN s.patient_bmi IS NULL OR s.patient_bmi <= 0 THEN 'Unknown'
            WHEN s.patient_bmi < 18.5 THEN 'Underweight'
            WHEN s.patient_bmi < 25.0 THEN 'Normal'
            WHEN s.patient_bmi < 30.0 THEN 'Overweight'
            ELSE 'Obese'
        END AS bmi_category,
        COALESCE(s.insurance_tier, 'BHYT Tiêu chuẩn') AS insurance_tier,
        DATE(s.vdate) AS start_date,
        '9999-12-31' AS end_date,
        1 AS is_current
    FROM stg_hospital_transactions s
    LEFT JOIN dim_patient p 
        ON p.patient_hash_id = SHA2(CONCAT(s.raw_patient_id, '_', v_salt), 256)
        AND p.is_current = 1
    WHERE p.patient_key IS NULL;

    SELECT '[SUCCESS] Đã đồng bộ thành công dim_patient (SCD Type 2 & SHA-256).' AS log_message;
END$$

-- ============================================================================
-- THỦ TỤC 3: sp_etl_dim_doctor & sp_etl_dim_facility & sp_etl_dim_diagnosis
-- Đồng bộ các bảng danh mục phân loại
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_etl_dim_doctor$$
CREATE PROCEDURE sp_etl_dim_doctor()
BEGIN
    INSERT INTO dim_doctor (doctor_code, doctor_name, specialty, academic_title, department_id)
    SELECT DISTINCT
        s.doctor_code,
        s.doctor_name,
        s.doctor_specialty,
        COALESCE(s.doctor_title, 'BS'),
        s.facid
    FROM stg_hospital_transactions s
    WHERE s.doctor_code IS NOT NULL
    ON DUPLICATE KEY UPDATE
        doctor_name = VALUES(doctor_name),
        specialty = VALUES(specialty),
        academic_title = VALUES(academic_title);
        
    SELECT '[SUCCESS] Đã nạp danh mục dim_doctor.' AS log_message;
END$$

DROP PROCEDURE IF EXISTS sp_etl_dim_facility$$
CREATE PROCEDURE sp_etl_dim_facility()
BEGIN
    INSERT INTO dim_facility (facility_code, facility_name, facility_type, clinic_room, division, planned_beds)
    SELECT DISTINCT
        s.facid,
        s.facility_name,
        COALESCE(s.facility_type, 'Khoa Khám Bệnh'),
        COALESCE(s.clinic_room, 'Phòng Tổng Hợp'),
        COALESCE(s.division, 'Lâm Sàng'),
        CASE 
            WHEN s.facility_type = 'ICU' THEN 30
            WHEN s.facility_type = 'Nội Trú' THEN 100
            WHEN s.facility_type = 'Cấp Cứu' THEN 40
            ELSE 10
        END AS planned_beds
    FROM stg_hospital_transactions s
    WHERE s.facid IS NOT NULL
    ON DUPLICATE KEY UPDATE
        facility_name = VALUES(facility_name),
        facility_type = VALUES(facility_type),
        division = VALUES(division);

    SELECT '[SUCCESS] Đã nạp danh mục dim_facility.' AS log_message;
END$$

DROP PROCEDURE IF EXISTS sp_etl_dim_diagnosis$$
CREATE PROCEDURE sp_etl_dim_diagnosis()
BEGIN
    INSERT INTO dim_diagnosis (icd10_code, disease_name, disease_category, chronic_indicator, severity_level)
    SELECT DISTINCT
        s.icd10_code,
        s.disease_name,
        COALESCE(s.disease_category, 'Nội Khoa'),
        COALESCE(s.is_chronic, 0),
        CASE 
            WHEN s.dialysisrenalendstage = 1 OR s.pneum = 1 THEN 'Severe'
            WHEN s.asthma = 1 OR s.depress = 1 THEN 'Moderate'
            ELSE 'Mild'
        END AS severity_level
    FROM stg_hospital_transactions s
    WHERE s.icd10_code IS NOT NULL
    ON DUPLICATE KEY UPDATE
        disease_name = VALUES(disease_name),
        disease_category = VALUES(disease_category),
        chronic_indicator = VALUES(chronic_indicator);

    SELECT '[SUCCESS] Đã nạp danh mục dim_diagnosis.' AS log_message;
END$$

DROP PROCEDURE IF EXISTS sp_etl_dim_service$$
CREATE PROCEDURE sp_etl_dim_service()
BEGIN
    INSERT INTO dim_service (service_code, service_name, service_group, standard_price)
    SELECT DISTINCT
        s.service_code,
        s.service_name,
        COALESCE(s.service_group, 'Khám Bệnh'),
        COALESCE(s.total_cost, 150000.00)
    FROM stg_hospital_transactions s
    WHERE s.service_code IS NOT NULL
    ON DUPLICATE KEY UPDATE
        service_name = VALUES(service_name),
        service_group = VALUES(service_group);

    SELECT '[SUCCESS] Đã nạp danh mục dim_service.' AS log_message;
END$$

-- ============================================================================
-- THỦ TỤC 4: sp_etl_fact_patient_visits
-- Làm sạch, chuẩn hóa số ngày nằm viện, giải quyết Surrogate Key và nạp Fact Table
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_etl_fact_patient_visits$$
CREATE PROCEDURE sp_etl_fact_patient_visits()
BEGIN
    DECLARE v_salt VARCHAR(50);
    SET v_salt = 'VKU_CLINICAL_SALT_TOKEN_2026';

    INSERT INTO fact_patient_visits (
        patient_key,
        doctor_key,
        facility_key,
        diagnosis_key,
        service_key,
        visit_date_key,
        discharged_date_key,
        waiting_time_minutes,
        consultation_duration,
        length_of_stay_days,
        prior_visits_count,
        lab_hematocrit,
        lab_neutrophils,
        lab_sodium,
        lab_glucose,
        lab_bloodureanitro,
        lab_creatinine,
        vital_pulse,
        vital_respiration,
        total_cost,
        insurance_covered_amount,
        patient_paid_amount
    )
    SELECT 
        p.patient_key,
        doc.doctor_key,
        fac.facility_key,
        diag.diagnosis_key,
        srv.service_key,
        YEAR(s.vdate) * 10000 + MONTH(s.vdate) * 100 + DAY(s.vdate) AS visit_date_key,
        CASE 
            WHEN s.discharged IS NOT NULL THEN YEAR(s.discharged) * 10000 + MONTH(s.discharged) * 100 + DAY(s.discharged)
            ELSE 99991231
        END AS discharged_date_key,
        
        -- Measures: Làm sạch và xử lý giá trị mặc định
        COALESCE(s.waiting_time_minutes, 15) AS waiting_time_minutes,
        COALESCE(s.consultation_duration, 10) AS consultation_duration,
        
        -- Tính toán số ngày nằm viện (LoS: Tối thiểu 1 ngày nếu xuất viện cùng ngày)
        CASE 
            WHEN s.discharged IS NOT NULL AND DATEDIFF(s.discharged, s.vdate) > 0 
                THEN DATEDIFF(s.discharged, s.vdate)
            ELSE 1
        END AS length_of_stay_days,
        
        COALESCE(s.rcount, 0) AS prior_visits_count,
        
        -- Lab measures & Sinh hiệu
        s.hematocrit,
        s.neutrophils,
        s.sodium,
        CASE 
            WHEN s.glucose <= 0 OR s.glucose > 1000 THEN 110.0 -- Thay thế ngoại lai bằng trung vị
            ELSE s.glucose 
        END AS lab_glucose,
        s.bloodureanitro,
        s.creatinine,
        COALESCE(s.pulse, 75) AS vital_pulse,
        COALESCE(s.respiration, 18) AS vital_respiration,
        
        -- Measures viện phí
        COALESCE(s.total_cost, 0.00),
        COALESCE(s.insurance_covered, 0.00),
        COALESCE(s.patient_paid, 0.00)
    FROM stg_hospital_transactions s
    INNER JOIN dim_patient p 
        ON p.patient_hash_id = SHA2(CONCAT(s.raw_patient_id, '_', v_salt), 256)
        AND p.is_current = 1
    INNER JOIN dim_doctor doc 
        ON doc.doctor_code = s.doctor_code
    INNER JOIN dim_facility fac 
        ON fac.facility_code = s.facid
    INNER JOIN dim_diagnosis diag 
        ON diag.icd10_code = s.icd10_code
    INNER JOIN dim_service srv 
        ON srv.service_code = s.service_code;

    SELECT CONCAT('[SUCCESS] Đã nạp thành công dữ liệu vào Fact_Patient_Visits! Tổng số dòng: ', ROW_COUNT()) AS log_message;
END$$

-- ============================================================================
-- THỦ TỤC 5: sp_run_full_cdw_etl
-- Master Orchestration Stored Procedure điều phối toàn bộ quá trình ETL
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_run_full_cdw_etl$$
CREATE PROCEDURE sp_run_full_cdw_etl()
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT '[ERROR] Tiến trình ETL gặp lỗi nghiêm trọng! Đã thực hiện ROLLBACK toàn bộ.' AS log_message;
    END;

    START TRANSACTION;
        CALL sp_etl_dim_doctor();
        CALL sp_etl_dim_facility();
        CALL sp_etl_dim_diagnosis();
        CALL sp_etl_dim_service();
        CALL sp_etl_dim_patient_scd2();
        CALL sp_etl_fact_patient_visits();
    COMMIT;

    SELECT '[COMPLETED] Toàn bộ quy trình ETL Kho Dữ liệu Lâm sàng đã hoàn tất thành công!' AS final_status;
END$$

DELIMITER ;
