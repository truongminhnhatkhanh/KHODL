# 🧊 SSAS_HospitalDW: THIẾT KẾ KHỐI LẬP PHƯƠNG ĐA CHIỀU (OLAP CUBE)
> **HỌC PHẦN: KHO DỮ LIỆU (DATA WAREHOUSE) – VKU**  
> **TƯƠNG ỨNG: PHÂN HỆ SSAS (SQL SERVER ANALYSIS SERVICES / MULTIDIMENSIONAL OLAP CUBE)**

---

## 1. MỤC TIÊU CỦA PHÂN HỆ PHÂN TÍCH ĐA CHIỀU (SSAS)
Phân hệ này xây dựng Khối lập phương phân tích trực tuyến đa chiều (**OLAP Cube: `Hospital_Clinical_Cube`**), tổ chức các độ đo định lượng (**Measures**) theo các góc nhìn kinh doanh y tế (**Dimensions**) và thiết lập các cấp bậc phân cấp (**Hierarchies**) để phục vụ thao tác phân tích tức thì (Drill-down, Roll-up, Slice & Dice).

---

## 2. KIẾN TRÚC KHỐI LẬP PHƯƠNG (CUBE SPECIFICATION)

### A. Tên Cube: `Hospital_Clinical_Cube`
* **Nguồn dữ liệu (Data Source):** `cdw_hospital_db`
* **Khung nhìn nguồn dữ liệu (Data Source View - DSV):** Lược đồ hình sao Kimball Star Schema gồm 1 Fact trung tâm và 6 Dimensions.

### B. Danh mục các Độ đo (Measures) trong Fact:
1. `[Measures].[Total Visits]` = $\text{COUNT}(visit\_key)$ (Tổng số lượt khám).
2. `[Measures].[Total Revenue]` = $\text{SUM}(total\_cost)$ (Tổng viện phí).
3. `[Measures].[Insurance Covered]` = $\text{SUM}(insurance\_covered\_amount)$ (Bảo hiểm chi trả).
4. `[Measures].[Patient Copay]` = $\text{SUM}(patient\_paid\_amount)$ (Bệnh nhân tự trả).
5. `[Measures].[Avg Waiting Time]` = $\text{AVG}(waiting\_time\_minutes)$ (Thời gian chờ trung bình).
6. `[Measures].[Avg LoS]` = $\text{AVG}(length\_of\_stay\_days)$ (Số ngày nằm viện trung bình).
7. `[Measures].[Avg Glucose]` = $\text{AVG}(lab\_glucose)$ (Đường huyết trung bình).
8. `[Measures].[Avg Creatinine]` = $\text{AVG}(lab\_creatinine)$ (Chỉ số Creatinine chức năng thận).

---

## 3. CÁC CHIỀU DỮ LIỆU (DIMENSIONS) & PHÂN CẤP (HIERARCHIES)

| Chiều (Dimension) | Khóa chính (PK) | Các phân cấp (Hierarchies) | Thuộc tính (Attributes) |
| :--- | :--- | :--- | :--- |
| **Dim Date** | `date_key` | **Lịch thời gian:** `Year` $\rightarrow$ `Quarter` $\rightarrow$ `Month` $\rightarrow$ `Full Date` | `Day_Of_Week`, `Is_Weekend`, `Is_Holiday` |
| **Dim Facility** | `facility_key` | **Cơ cấu tổ chức:** `Division` $\rightarrow$ `Facility_Type` $\rightarrow$ `Facility_Name` | `Clinic_Room`, `Planned_Beds` |
| **Dim Diagnosis** | `diagnosis_key` | **Phân loại bệnh tật:** `Disease_Category` $\rightarrow$ `ICD10_Code` $\rightarrow$ `Disease_Name` | `Is_Chronic`, `Severity_Level` |
| **Dim Patient** | `patient_key` | **Nhân khẩu học:** `Gender` $\rightarrow$ `Age_Group` $\rightarrow$ `Patient_Hash_ID` | `BMI_Category`, `Insurance_Tier` |
| **Dim Doctor** | `doctor_key` | **Nhân sự y tế:** `Specialty` $\rightarrow$ `Academic_Title` $\rightarrow$ `Doctor_Name` | `Doctor_Code` |
| **Dim Service** | `service_key` | **Dịch vụ y tế:** `Service_Group` $\rightarrow$ `Service_Name` | `Service_Code`, `Standard_Price` |

---

## 4. CÁC CÂU TRUY VẤN PHÂN TÍCH ĐA CHIỀU BẰNG MDX (MULTIDIMENSIONAL EXPRESSIONS)

### Truy vấn 1: Doanh thu và lượt khám theo Quý và Khoa phòng
```mdx
SELECT 
    {[Measures].[Total Visits], [Measures].[Total Revenue]} ON COLUMNS,
    NON EMPTY CROSSJOIN([Dim Date].[Calendar].[Quarter].Members, [Dim Facility].[Facility Name].Members) ON ROWS
FROM [Hospital_Clinical_Cube];
```

### Truy vấn 2: Cắt lát thời gian chờ khám bệnh nhân ngoại trú theo Thứ trong tuần
```mdx
SELECT 
    {[Measures].[Total Visits], [Measures].[Avg Waiting Time]} ON COLUMNS,
    [Dim Date].[Day Of Week].Members ON ROWS
FROM [Hospital_Clinical_Cube]
WHERE ([Dim Facility].[Facility Type].[Khoa Khám Bệnh]);
```

### Truy vấn 3: Phân tích độ dài nằm viện LoS theo nhóm bệnh lý mãn tính
```mdx
SELECT 
    {[Measures].[Total Visits], [Measures].[Avg LoS], [Measures].[Avg Creatinine]} ON COLUMNS,
    [Dim Diagnosis].[Disease Category].Members ON ROWS
FROM [Hospital_Clinical_Cube]
WHERE ([Dim Diagnosis].[Is Chronic].[1]);
```
