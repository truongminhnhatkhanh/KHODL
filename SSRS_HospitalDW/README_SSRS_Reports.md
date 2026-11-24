# 📊 SSRS_HospitalDW: HỆ THỐNG BÁO CÁO TRỰC QUAN HÓA (REPORTING SERVICES & BI)
> **HỌC PHẦN: KHO DỮ LIỆU (DATA WAREHOUSE) – VKU**  
> **TƯƠNG ỨNG: PHÂN HỆ SSRS (SQL SERVER REPORTING SERVICES / POWER BI DASHBOARDS)**

---

## 1. MỤC TIÊU CỦA PHÂN HỆ BÁO CÁO (SSRS / POWER BI)
Phân hệ này xây dựng các mẫu biểu mẫu báo cáo quản trị, bảng tổng hợp đa chiều (Matrix/Tablix), biểu đồ trực quan (Charts/Heatmaps) và thẻ chỉ số KPI giúp Ban Giám đốc và các Trưởng khoa phòng theo dõi, ra quyết định phân bổ nguồn lực y tế kịp thời.

---

## 2. BỐ CỤC 3 TRANG BÁO CÁO TRỌNG TÂM

### Trang 1: Tổng quan điều hành Bệnh viện (Executive Dashboard)
* **Thẻ chỉ số (KPI Cards):**
  * Tổng số lượt khám bệnh (`Total Visits`): 14.800+ lượt
  * Tổng viện phí (`Total Revenue`): Doanh thu toàn viện
  * Thời gian chờ trung bình (`Avg Waiting Time`): ~33.8 phút
  * Tỷ lệ chi trả BHYT (`Insurance Coverage %`): Cơ cấu bảo hiểm chi trả
* **Biểu đồ Cột/Đường (Combo Chart):** Số lượt khám và doanh thu qua các tháng theo chiều thời gian `Dim_Date[Year_Month]`.
* **Biểu đồ Tròn (Donut Chart):** Cơ cấu bệnh tật theo 10 chương bệnh quốc tế ICD-10 (`Dim_Diagnosis[Disease_Category]`).

### Trang 2: Vận hành Lâm sàng & Nguồn lực Khoa phòng (Clinical Ops & LoS)
* **Biểu đồ nhiệt (Matrix Heatmap):** Ma trận thời gian chờ khám ngoại trú theo Thứ trong tuần (`Day_Of_Week`) và Khung ca trực (`Shift_Period`).
* **Biểu đồ Thanh ngang:** Thời gian nằm viện trung bình (**LoS**) phân hóa theo từng Khoa điều trị (`Dim_Facility`).
* **Đồng hồ đo (Gauge Chart):** Tỷ lệ lấp đầy giường bệnh nội trú (**Bed Occupancy Rate %**), cảnh báo quá tải cho các khoa Hồi sức cấp cứu (ICU) và Tim mạch.

### Trang 3: Quản trị Tài chính & Chu trình Viện phí (Financial Cycle)
* **Biểu đồ Phân tích Trạng thái Hóa đơn:** Tỷ lệ Thực thu tiền mặt (`Paid`), Hồ sơ chờ thanh toán (`Pending`) và Hóa đơn từ chối/thất bại (`Failed`).
* **Bảng chi tiết đa chiều:** Doanh thu, mức đồng chi trả của người bệnh và mức bảo hiểm chi trả phân bổ theo từng Chuyên khoa y tế.

---

## 3. DANH MỤC CÔNG THỨC DAX CHUYÊN SÂU
Toàn bộ 18 công thức đo lường DAX được lưu trữ tại tệp: `dax_measures.dax`.
Một số công thức tiêu biểu:
```dax
Total Visits = COUNTROWS('fact_patient_visits')

Total Revenue = SUM('fact_patient_visits'[total_cost])

Avg Waiting Time (Min) = AVERAGE('fact_patient_visits'[waiting_time_minutes])

Avg Length of Stay (Days) = 
CALCULATE(
    AVERAGE('fact_patient_visits'[length_of_stay_days]),
    'fact_patient_visits'[length_of_stay_days] > 0
)

Insurance Coverage % = DIVIDE(SUM('fact_patient_visits'[insurance_covered_amount]), [Total Revenue], 0)
```
