-- ====================================================================
-- File: 03_olap_and_benchmark.sql
-- MÔ TẢ: Truy vấn OLAP, Benchmark, SCD-2, RANK() OVER, Dim_Service
-- Phiên bản V2 — Thêm phân tích theo Loại dịch vụ
-- ====================================================================

-- ===================== PHẦN 1: OLTP BENCHMARK =====================
USE hospital_oltp;

-- 1. Truy vấn tham chiếu chéo OLTP
SELECT a.appointment_id,
       CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
       CONCAT(d.first_name, ' ', d.last_name) AS doctor_name,
       d.specialization,
       a.status
FROM appointments a
JOIN patients p ON a.patient_id = p.patient_id
JOIN doctors d ON a.doctor_id = d.doctor_id
LIMIT 20;

-- 2. Benchmark OLTP: JOIN 4 bảng + GROUP BY
EXPLAIN ANALYZE
SELECT DATE_FORMAT(a.appointment_date, '%Y-%m') AS year_month_val,
       d.specialization,
       COUNT(a.appointment_id) AS total_visits,
       SUM(b.amount) AS total_revenue
FROM appointments a
JOIN doctors d ON a.doctor_id = d.doctor_id
JOIN treatments t ON a.appointment_id = t.appointment_id
JOIN billing b ON t.treatment_id = b.treatment_id
GROUP BY year_month_val, d.specialization;


-- ===================== PHẦN 2: DW - STAGING & SCD-2 =====================
USE hospital_dw;

-- 3. Kiểm tra Staging
SELECT Source_System, COUNT(*) AS total_rows
FROM Staging_Doctors
GROUP BY Source_System;

-- 4. Kiểm tra trùng Doctor_ID
SELECT Doctor_ID, COUNT(*) AS duplicate_count
FROM Staging_Doctors
GROUP BY Doctor_ID
HAVING COUNT(*) > 1;

-- 5. Xác minh SCD Type 2
SELECT Doctor_Key, Doctor_ID, Doctor_Name, Specialty, Hospital_Branch,
       Effective_Date, End_Date, Is_Current
FROM Dim_Doctor
WHERE Doctor_ID IN ('D001', 'D999')
ORDER BY Doctor_ID, Doctor_Key;


-- ===================== PHẦN 3: DW - BENCHMARK STAR SCHEMA =====================

-- 6. Benchmark DW: Star Schema query
EXPLAIN ANALYZE
SELECT d.Year_Month,
       dept.Department_Name,
       COUNT(f.Visit_Key) AS total_visits,
       SUM(f.Total_Cost) AS total_revenue
FROM Fact_Patient_Visits f
JOIN Dim_Date d ON f.Date_Key = d.Date_Key
JOIN Dim_Department dept ON f.Department_Key = dept.Department_Key
GROUP BY d.Year_Month, dept.Department_Name;


-- ===================== PHẦN 4: ROLLUP ĐA CẤP =====================

-- 7. ROLLUP tổng hợp đa cấp (Năm → Quý → Khoa)
SELECT d.Year,
       d.Quarter,
       dept.Department_Name,
       COUNT(f.Visit_Key) AS Total_Visits,
       ROUND(AVG(f.Waiting_Time_Minutes), 1) AS Avg_Wait_Min,
       SUM(f.Total_Cost) AS Total_Revenue
FROM Fact_Patient_Visits f
JOIN Dim_Date d ON f.Date_Key = d.Date_Key
JOIN Dim_Department dept ON f.Department_Key = dept.Department_Key
GROUP BY d.Year, d.Quarter, dept.Department_Name WITH ROLLUP;


-- ===================== PHẦN 5: WINDOW FUNCTION =====================

-- 8. RANK() OVER — Xếp hạng doanh thu & lượt khám theo quý
SELECT
    d.Year,
    d.Quarter,
    dept.Department_Name,
    COUNT(f.Visit_Key) AS Total_Visits,
    ROUND(AVG(f.Waiting_Time_Minutes), 1) AS Avg_Wait_Mins,
    ROUND(SUM(f.Total_Cost), 2) AS Total_Revenue,
    RANK() OVER (
        PARTITION BY d.Year, d.Quarter
        ORDER BY SUM(f.Total_Cost) DESC
    ) AS Revenue_Rank_In_Quarter,
    DENSE_RANK() OVER (
        ORDER BY COUNT(f.Visit_Key) DESC
    ) AS Overall_Visit_Rank
FROM Fact_Patient_Visits f
JOIN Dim_Date d ON f.Date_Key = d.Date_Key
JOIN Dim_Department dept ON f.Department_Key = dept.Department_Key
GROUP BY d.Year, d.Quarter, dept.Department_Name
ORDER BY d.Year, d.Quarter, Revenue_Rank_In_Quarter;


-- ===================== PHẦN 6: ★ PHÂN TÍCH DIM_SERVICE =====================

-- 9. Phân bổ Lượt khám & Doanh thu theo Loại dịch vụ × Khoa
SELECT
    svc.Service_Type,
    dept.Department_Name,
    COUNT(f.Visit_Key) AS Total_Visits,
    ROUND(AVG(f.Length_Of_Stay_Days), 1) AS Avg_LOS,
    ROUND(AVG(f.Waiting_Time_Minutes), 1) AS Avg_Wait_Min,
    ROUND(SUM(f.Total_Cost), 2) AS Total_Revenue,
    ROUND(SUM(f.Insurance_Covered_Amount), 2) AS Total_Insurance,
    ROUND(SUM(f.Patient_Paid_Amount), 2) AS Total_OOP
FROM Fact_Patient_Visits f
JOIN Dim_Service svc ON f.Service_Key = svc.Service_Key
JOIN Dim_Department dept ON f.Department_Key = dept.Department_Key
GROUP BY svc.Service_Type, dept.Department_Name
ORDER BY svc.Service_Type, Total_Revenue DESC;

-- 10. Top 5 khoa doanh thu cao nhất MỖI loại dịch vụ
SELECT *
FROM (
    SELECT
        svc.Service_Type,
        dept.Department_Name,
        COUNT(f.Visit_Key) AS Total_Visits,
        ROUND(SUM(f.Total_Cost), 2) AS Total_Revenue,
        RANK() OVER (
            PARTITION BY svc.Service_Type
            ORDER BY SUM(f.Total_Cost) DESC
        ) AS Revenue_Rank
    FROM Fact_Patient_Visits f
    JOIN Dim_Service svc ON f.Service_Key = svc.Service_Key
    JOIN Dim_Department dept ON f.Department_Key = dept.Department_Key
    GROUP BY svc.Service_Type, dept.Department_Name
) ranked
WHERE Revenue_Rank <= 5
ORDER BY Service_Type, Revenue_Rank;

-- 11. Tỷ lệ Outpatient / Inpatient / Surgery / Emergency theo tháng
SELECT
    d.Year_Month,
    svc.Service_Type,
    COUNT(f.Visit_Key) AS Visits,
    ROUND(COUNT(f.Visit_Key) * 100.0 / SUM(COUNT(f.Visit_Key)) OVER (PARTITION BY d.Year_Month), 1) AS Pct_Of_Month
FROM Fact_Patient_Visits f
JOIN Dim_Date d ON f.Date_Key = d.Date_Key
JOIN Dim_Service svc ON f.Service_Key = svc.Service_Key
GROUP BY d.Year_Month, svc.Service_Type
ORDER BY d.Year_Month, svc.Service_Type;
