# 💾 SSMS_HospitalDW: THIẾT KẾ CƠ SỞ DỮ LIỆU & LƯỢC ĐỒ QUAN HỆ
> **HỌC PHẦN: KHO DỮ LIỆU (DATA WAREHOUSE) – VKU**  
> **TƯƠNG ỨNG: PHÂN HỆ SSMS (SQL SERVER MANAGEMENT STUDIO / DATABASE ENGINE)**

---

## 1. MỤC TIÊU CỦA PHÂN HỆ CSDL (SSMS)
Phân hệ này đảm nhận việc định nghĩa cấu trúc bảng DDL, ràng buộc khóa chính/khóa ngoại, chỉ mục hiệu năng (Indexes) cho Kho dữ liệu lâm sàng `cdw_hospital_db` theo mô hình hình sao (Star Schema), kèm theo bộ câu truy vấn phân tích nghiệp vụ.

---

## 2. CẤU TRÚC TỆP TIN TRONG THƯ MỤC
* **`01_Create_Database_And_Star_Schema.sql`:** Kịch bản DDL tạo Database `cdw_hospital_db`, bảng đệm `stg_hospital_transactions`, bảng sự kiện `fact_patient_visits` và 6 bảng chiều `dim_patient`, `dim_doctor`, `dim_facility`, `dim_diagnosis`, `dim_service`, `dim_date`.
* **`02_Seed_Data.sql`:** Dữ liệu mẫu 5.010 bản ghi lâm sàng nạp vào bảng Staging.
* **`03_OLAP_Analytical_Queries.sql`:** Bộ 12 câu truy vấn phân tích nghiệp vụ, hàm cửa sổ `LAG()`, phân tích lũy kế `WITH ROLLUP` và kiểm chứng `EXPLAIN ANALYZE`.
* **`Star_Schema_Diagram.dbml`:** Bản thiết kế quan hệ lược đồ hình sao trực quan (mở tại [dbdiagram.io](https://dbdiagram.io)).

---

## 3. CÁCH CHẠY TRÊN HỆ QUẢN TRỊ CSDL
Mở công cụ quản trị (SSMS hoặc MySQL Workbench), mở file `01_Create_Database_And_Star_Schema.sql` và bấm nút Execute để tạo cấu trúc bảng sạch trước khi chạy phân hệ ETL (SSIS).
