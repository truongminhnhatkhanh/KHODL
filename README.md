# 🏥 CLINICAL DATA WAREHOUSE (CDW) - HỆ THỐNG KHO DỮ LIỆU Y TẾ LÂM SÀNG
> **ĐỒ ÁN HỌC PHẦN: KHO DỮ LIỆU (DATA WAREHOUSE)**  
> **Trường Đại học Công nghệ Thông tin và Truyền thông Việt - Hàn (VKU) – Đại học Đà Nẵng**  
> **Khoa Khoa học Máy tính**

---

## 📌 THÔNG TIN HỌC PHẦN & NHÓM THỰC HIỆN

- **Tên đề tài:** Thiết kế và Triển khai Kho Dữ liệu Y tế Lâm sàng (Clinical Data Warehouse - CDW) Tối ưu hóa Quy trình Chăm sóc Bệnh nhân và Phân bổ Nguồn lực Y tế
- **Giảng viên hướng dẫn:** **ThS. Mai Lam**
- **Lớp sinh hoạt:** **24GITe**
- **Nhóm sinh viên thực hiện:**
  1. **Trương Minh Nhật Khánh** – Mã SV: `24ITE047` *(Nhóm trưởng)*
  2. **Lê Thị Hồng Hạnh** – Mã SV: `24ITE034`
  3. **Ngô Thị Anh Thư** – Mã SV: `24ITE104`
  4. **Lê Hà An** – Mã SV: `24ITE002`

---

## 🌟 ĐIỂM SÁNG NỔI BẬT & ĐÓNG GÓP CỦA ĐỒ ÁN

Khác biệt hoàn toàn với các bài tập lớn truyền thống chỉ dừng lại ở mức gom bảng đơn giản, đồ án này triển khai trọn vẹn quy chuẩn kỹ thuật kho dữ liệu doanh nghiệp theo chuẩn **Ralph Kimball**:

1. **Khử định danh bảo mật dữ liệu y tế (De-identification via SHA-256):** Tuân thủ tiêu chuẩn HIPAA/GDPR, mã hóa ẩn danh toàn bộ mã định danh bệnh nhân gốc (`Patient_ID` $\rightarrow$ `Anonymized_Patient_ID`) trước khi đẩy vào kho dữ liệu phân tích.
2. **Kiến trúc dữ liệu hình sao chuẩn hóa (Kimball Star Schema):** Chuẩn hóa 1 bảng sự kiện (`Fact_Patient_Visits`) liên kết chặt chẽ với 6 bảng chiều (`Dim_Patient`, `Dim_Doctor`, `Dim_Department`, `Dim_Diagnosis`, `Dim_Date`, `Dim_Service`) thông qua các khóa thay thế số nguyên (**Surrogate Keys**), loại bỏ hoàn toàn dư thừa dữ liệu và tăng tốc độ Join.
3. **Phân hóa lâm sàng thực tế (Clinical Realism):** Phân bổ cân bằng 8 chuyên khoa y tế (phủ đủ Ung bướu, Tim mạch, Nội tiết, Hô hấp, Chấn thương chỉnh hình, Đa khoa, Nhi khoa, Da liễu), mô phỏng thời gian chờ khám theo tính chất cấp thiết từng khoa và số ngày nằm viện LOS phân hóa theo loại hình điều trị (Nội trú 1-21 ngày, Ngoại trú = 0 ngày).
4. **Quản trị biến động lịch sử dữ liệu (Slowly Changing Dimensions - SCD Type 2):** Quản lý chi tiết lịch sử thâm niên, chuyển khoa phòng và chi nhánh bệnh viện của đội ngũ Y bác sĩ với các trường thời gian hiệu lực (`Effective_Date`, `End_Date`, `Is_Current = 1/0`).
5. **Tích hợp đa nguồn & Bảo mật biến môi trường:** Xây dựng vùng đệm dữ liệu (**Staging Area**) để hợp nhất tự động giữa CSDL vận hành (**MySQL OLTP**) và tệp cập nhật nhân sự (**Excel `doctors_update.xlsx`**), đồng thời tách biệt thông tin bảo mật qua file `.env`.
6. **Chứng minh hiệu năng định lượng (Quantitative Benchmarking via `EXPLAIN ANALYZE`):** Thực nghiệm đo lường thực tế trên CSDL MySQL chứng minh kiến trúc Star Schema giúp giảm số tầng Join phức tạp, giảm Query Cost từ hàng nghìn đơn vị trên hệ thống 3NF xuống mức tối ưu vượt trội (nhanh hơn 50% - 70%).
7. **Báo cáo trực quan Business Intelligence (Power BI Dashboard):** Xây dựng hệ thống đo lường với **18 công thức DAX chuyên sâu**, bóc tách sâu các bài toán thực tiễn: Heatmap thời gian chờ khám theo khoa phòng, tỷ lệ lấp đầy giường bệnh, cơ cấu thanh toán BHYT vs Viện phí tự chi trả, và phân tích theo 4 nhóm dịch vụ y tế (`Dim_Service`: Ngoại trú, Nội trú, Phẫu thuật, Cấp cứu).

---

## 📁 CẤU TRÚC THƯ MỤC DỰ ÁN (PROJECT REPOSITORY)

```text
D:\KHODL\
│
├── README.md                            # [Tệp này] Cẩm nang hướng dẫn toàn diện từ A-Z
├── BAO_CAO_KHO_DU_LIEU_BENH_VIEN.md      # Báo cáo học thuật toàn văn chuẩn VKU (6 chương, 67+ KB)
├── SLIDE_THUYET_TRINH_KHO_DU_LIEU.md    # Kịch bản 20 Slide thuyết trình + Lời thoại phân công 4 bạn
│
├── Clinical_DW_Labs_1_to_6/             # ⭐️ THƯ MỤC TRỌNG TÂM: TRỌN GÓI LABS 1 ĐẾN 6
│   ├── config.py                        # Cấu hình trực tiếp kết nối MySQL (chạy python config.py để test)
│   ├── requirements.txt                 # Danh sách thư viện Python cần thiết
│   ├── .gitignore                       # Chặn đẩy file rác/cache lên Git
│   │
│   ├── data/                            # Thư mục dữ liệu nguồn đã làm giàu cân bằng 8 chuyên khoa
│   │   ├── patients.csv                 # Hồ sơ 5,050 bệnh nhân
│   │   ├── doctors.csv                  # Danh mục 20 bác sĩ (phủ đủ 8 chuyên khoa y tế)
│   │   ├── appointments.csv             # 5,200 lượt đặt lịch khám lâm sàng
│   │   ├── treatments.csv               # 5,200 chỉ định điều trị và viện phí
│   │   ├── billing.csv                  # 5,200 hóa đơn thanh toán
│   │   └── doctors_update.xlsx          # Cập nhật nhân sự bác sĩ (dùng cho Lab 4 SCD Type 2)
│   │
│   ├── sql/                             # Kịch bản SQL cấu trúc CSDL và phân tích
│   │   ├── 01_create_oltp.sql           # DDL khởi tạo CSDL vận hành (hospital_oltp)
│   │   ├── 02_create_dw.sql             # DDL khởi tạo Star Schema Kho dữ liệu (hospital_dw, 6 Dimensions)
│   │   └── 03_olap_and_benchmark.sql    # Truy vấn kiểm chứng SCD-2, EXPLAIN ANALYZE, ROLLUP & RANK() OVER
│   │
│   ├── scripts/                         # Mã nguồn Python xử lý tự động hóa
│   │   ├── 01_load_oltp_csv.py          # Lab 1: Nạp 5 file CSV vào CSDL hospital_oltp
│   │   ├── 02_etl_lab3_initial.py       # Lab 2 & 3: ETL khử định danh, tạo Surrogate Key, nạp Star Schema
│   │   └── 03_etl_lab4_advanced.py      # Lab 4: Hợp nhất Staging và cập nhật SCD Type 2 cho Dim_Doctor
│   │
│   ├── diagrams/                        # Bản thiết kế lược đồ hình sao
│   │   └── star_schema.dbml             # File mã nguồn DBML 6 Dimensions, mở tại dbdiagram.io
│   │
│   └── powerbi/                         # Tài nguyên trực quan hóa báo cáo BI
│       └── dax_measures.dax             # 18 công thức DAX chuyên sâu cho 3 trang Dashboard Lab 6
│
├── setup_database.py                    # Script 1-Click tự động hóa phân hệ SSMS & SSIS (cdw_hospital_db)
├── start_mysql.bat                      # Script 1-Click bật service MySQL80 (Run as administrator)
├── dataset/                             # Dữ liệu nguồn Kaggle (55,500 ca lâm sàng)
├── SSMS_HospitalDW/                     # Phân hệ Cơ sở dữ liệu & Lược đồ Star Schema
├── SSIS_HospitalDW/                     # Phân hệ ETL Stored Procedures & Pipeline
├── SSAS_HospitalDW/                     # Phân hệ Khối lập phương đa chiều OLAP & MDX
└── SSRS_HospitalDW/                     # Phân hệ Báo cáo quản trị & DAX Measures
```

---

## 💻 YÊU CẦU MÔI TRƯỜNG & PHẦN MỀM CẦN THIẾT

Trước khi chạy dự án, hãy đảm bảo máy tính đã cài đặt:

| Phần mềm / Môi trường | Phiên bản khuyến nghị | Ghi chú |
| :--- | :--- | :--- |
| **Hệ điều hành** | Windows 10 / 11 (hoặc macOS/Linux) | Đã kiểm thử ổn định 100% trên Windows |
| **Python** | 3.10 trở lên (khuyên dùng Python 3.11 - 3.13) | Cần tích chọn *"Add Python to PATH"* khi cài |
| **Hệ quản trị CSDL** | **MySQL Server 8.0** hoặc **XAMPP (v3.3+)** | Khởi chạy dịch vụ MySQL ở cổng `3306` |
| **Công cụ giao diện SQL** | **MySQL Workbench 8.0 CE** hoặc phpMyAdmin / DBeaver | Dùng để chạy file Benchmark & kiểm tra bảng |
| **Công cụ Business Intelligence** | **Microsoft Power BI Desktop** (Bản mới nhất) | Dùng để dựng Dashboard trực quan hóa Lab 6 |

---

## 🚀 HƯỚNG DẪN THỰC THI DỰ ÁN CHI TIẾT (STEP-BY-STEP)

### BƯỚC 1: KHỞI ĐỘNG DỊCH VỤ CSDL MYSQL80
- **Cách 1 (Nhanh nhất):** Chuột phải vào tệp `D:\KHODL\start_mysql.bat` chọn **Run as administrator**.
- **Cách 2:** Mở CMD hoặc PowerShell với quyền Admin và gõ:
  ```cmd
  net start MYSQL80
  ```
- **Cách 3:** Mở `services.msc` $\rightarrow$ Chuột phải vào dịch vụ `MYSQL80` chọn **Start**.

---

### BƯỚC 2: CẤU HÌNH KẾT NỐI TRỰC TIẾP TRONG `config.py`
Mở file `Clinical_DW_Labs_1_to_6/config.py` để chỉnh sửa thông tin đăng nhập MySQL nếu cần:

```python
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "your_password"  # Nhập mật khẩu MySQL của bạn (nếu dùng XAMPP thì để trống "")
```

Kiểm tra kết nối MySQL:
```bash
python config.py
```

---

### BƯỚC 3: CÀI ĐẶT CÁC THƯ VIỆN PYTHON CẦN THIẾT
Mở cửa sổ **Terminal / PowerShell** tại thư mục `Clinical_DW_Labs_1_to_6`:

```bash
cd D:\KHODL\Clinical_DW_Labs_1_to_6
pip install -r requirements.txt
```

*Các thư viện được cài đặt bao gồm:* `pandas`, `sqlalchemy`, `pymysql`, `openpyxl`, `numpy`.

---

### BƯỚC 4: THỰC THI THỦ CÔNG TỪNG BƯỚC (LABS 1 ĐẾN 4)
Chạy lần lượt từng script để theo dõi sự chuyển dịch dữ liệu:

```bash
# 1. Nạp dữ liệu vào CSDL vận hành hospital_oltp (Lab 1)
python scripts/01_load_oltp_csv.py

# 2. ETL Star Schema, khử định danh SHA-256 và nạp vào hospital_dw (Lab 2 & 3)
python scripts/02_etl_lab3_initial.py

# 3. Hợp nhất Staging và cập nhật SCD Type 2 cho Bác sĩ (Lab 4)
python scripts/03_etl_lab4_advanced.py
```

#### Quá trình thực thi diễn ra tự động qua 3 giai đoạn:
1. **Giai đoạn 1 (`scripts/01_load_oltp_csv.py` - Lab 1):**
   - Tự động tạo CSDL `hospital_oltp`.
   - Tạo 5 bảng chuẩn hóa 3NF: `patients`, `doctors`, `appointments`, `treatments`, `billing`.
   - Tải toàn bộ dữ liệu từ 5 file CSV vào `hospital_oltp`.
2. **Giai đoạn 2 (`scripts/02_etl_lab3_initial.py` - Lab 2 & Lab 3):**
   - Tự động tạo CSDL `hospital_dw`.
   - Tạo cấu trúc Star Schema: `Dim_Patient`, `Dim_Doctor`, `Dim_Department`, `Dim_Diagnosis`, `Dim_Date`, `Fact_Patient_Visits`.
   - Áp dụng hàm băm **SHA-256** ẩn danh hóa `patient_id`.
   - Phân nhóm tuổi (`Age_Group`), phân loại ca trực (`Morning/Afternoon/Night`).
   - Tự động gán mã chẩn đoán quốc tế **ICD-10** (`C80.1`, `R90.8`, `I49.9`, `M54.5`, `S99.9`).
   - Sinh các khóa thay thế Surrogate Keys và nạp toàn bộ vào Fact Table.
3. **Giai đoạn 3 (`scripts/03_etl_lab4_advanced.py` - Lab 4):**
   - Đọc dữ liệu từ 2 nguồn: Bảng `doctors` trong MySQL OLTP và file `data/doctors_update.xlsx`.
   - Nạp vào bảng trung gian `Staging_Doctors`.
   - So khớp và thực hiện kỹ thuật **SCD Type 2**: Với các bác sĩ có thay đổi chuyên khoa hoặc đổi chi nhánh làm việc (ví dụ bác sĩ `D001`), hệ thống tự động chốt bản ghi cũ (`End_Date = Ngày hôm nay`, `Is_Current = 0`) và chèn bản ghi mới với khóa `Doctor_Key` mới (`Is_Current = 1`).
   - Bổ sung bác sĩ mới tuyển dụng (`D999`).

> Khi màn hình xuất hiện thông báo:  
> `=== All Labs 1-4 database pipelines completed successfully ===`  
> Nghĩa là toàn bộ 2 CSDL `hospital_oltp` và `hospital_dw` đã sẵn sàng 100%!

---

### BƯỚC 5: KIỂM CHỨNG TRUY VẤN OLAP & BENCHMARK TRÊN MYSQL WORKBENCH (LAB 5)
1. Mở phần mềm **MySQL Workbench**.
2. Kết nối vào MySQL Localhost.
3. Mở tệp SQL: `Clinical_DW_Labs_1_to_6/sql/03_olap_and_benchmark.sql` và thực thi từng khối lệnh:

#### 1. Kiểm chứng bảo toàn lịch sử SCD Type 2:
```sql
USE hospital_dw;
SELECT Doctor_Key, Doctor_ID, Doctor_Name, Specialty, Hospital_Branch, Effective_Date, End_Date, Is_Current
FROM Dim_Doctor
WHERE Doctor_ID IN ('D001', 'D999')
ORDER BY Doctor_ID, Doctor_Key;
```
*Kết quả sẽ thấy bác sĩ `D001` có 2 dòng (dòng cũ `Is_Current = 0`, dòng mới `Is_Current = 1`) và bác sĩ `D999` có 1 dòng mới.*

#### 2. Kiểm chứng tối ưu hóa hiệu năng bằng `EXPLAIN ANALYZE`:
- **Truy vấn 1 (trên OLTP 3NF):** Join 4 bảng với các khóa tự nhiên chuỗi ký tự `VARCHAR`.
- **Truy vấn 2 (trên DW Star Schema):** Join trực tiếp Fact với Dim bằng khóa thay thế số nguyên `INT`.
- **Kết quả minh chứng:** Star Schema loại bỏ các bước quét lặp, giảm số lượng bộ đệm trung gian (Temporary Tables), cải thiện vượt bậc tốc độ phân tích báo cáo.

#### 3. Truy vấn phân tích đa chiều nâng cao (OLAP Roll-up):
```sql
SELECT d.Year, d.Quarter, dept.Department_Name,
       COUNT(f.Visit_Key) AS Total_Visits,
       ROUND(AVG(f.Waiting_Time_Minutes), 1) AS Avg_Wait_Min,
       SUM(f.Total_Cost) AS Total_Revenue
FROM Fact_Patient_Visits f
JOIN Dim_Date d ON f.Date_Key = d.Date_Key
JOIN Dim_Department dept ON f.Department_Key = dept.Department_Key
GROUP BY d.Year, d.Quarter, dept.Department_Name WITH ROLLUP;
```
*Lệnh `WITH ROLLUP` tự động tính tổng lũy kế phân cấp: Từng khoa $\rightarrow$ Cả quý $\rightarrow$ Cả năm $\rightarrow$ Toàn viện.*

#### 4. Phân tích nâng cao bằng Window Function (`RANK() OVER`):
```sql
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
    ) AS Revenue_Rank_In_Quarter
FROM Fact_Patient_Visits f
JOIN Dim_Date d ON f.Date_Key = d.Date_Key
JOIN Dim_Department dept ON f.Department_Key = dept.Department_Key
GROUP BY d.Year, d.Quarter, dept.Department_Name
ORDER BY d.Year, d.Quarter, Revenue_Rank_In_Quarter;
```
*Hàm cửa sổ `RANK() OVER (PARTITION BY ...)` tự động phân hạng doanh thu của từng khoa phòng theo từng quý, giúp lãnh đạo phát hiện ngay khoa mang lại doanh thu cao nhất.*

---

### BƯỚC 6: XÂY DỰNG BÁO CÁO TRÊN POWER BI DESKTOP (LAB 6)

#### Cách kết nối dữ liệu vào Power BI Desktop:

##### 👉 Phương án A: Kết nối trực tiếp vào MySQL Database
1. Mở **Power BI Desktop** $\rightarrow$ Chọn **Get Data** $\rightarrow$ **MySQL database** $\rightarrow$ Nhấn **Connect**.
2. Nhập thông số:
   - **Server:** `localhost:3306` (hoặc `localhost`)
   - **Database:** `hospital_dw`
   - **Data Connectivity mode:** Chọn **Import** $\rightarrow$ Bấm **OK**.
3. Điền User: `root` và Password (nếu dùng XAMPP thì để trống password).
4. Tại cửa sổ Navigator, tích chọn đủ **6 bảng**:
   - `Fact_Patient_Visits`
   - `Dim_Patient`
   - `Dim_Doctor`
   - `Dim_Department`
   - `Dim_Diagnosis`
   - `Dim_Date`
5. Bấm **Load**.

> [!NOTE]
> **Xử lý nếu Power BI báo lỗi thiếu driver:**  
> *"This connector requires one or more additional components to be installed before it can be used (MySQL Connector/NET)."*  
> **Giải pháp:** Tải và cài đặt tệp cài đặt chính thức từ Oracle: [MySQL Connector/NET 8.0.33 (MSI)](https://downloads.mysql.com/archives/c-net/). Sau khi cài xong, tắt Power BI và mở lại là kết nối thành công.  
> *(Hoặc dùng **Phương án B** dự phòng: Xuất 6 bảng thành CSV hoặc nạp trực tiếp qua Folder CSV).*

---

#### Kiểm tra lược đồ quan hệ (Data Modeling trong Power BI):
Vào tab **Model View** (biểu tượng sơ đồ khối ở thanh bên trái). Đảm bảo Power BI đã liên kết chuẩn xác mô hình hình sao (Star Schema):
- `Dim_Patient[Patient_Key]` $\xrightarrow{1 \dots \infty}$ `Fact_Patient_Visits[Patient_Key]`
- `Dim_Doctor[Doctor_Key]` $\xrightarrow{1 \dots \infty}$ `Fact_Patient_Visits[Doctor_Key]`
- `Dim_Department[Department_Key]` $\xrightarrow{1 \dots \infty}$ `Fact_Patient_Visits[Department_Key]`
- `Dim_Diagnosis[Diagnosis_Key]` $\xrightarrow{1 \dots \infty}$ `Fact_Patient_Visits[Diagnosis_Key]`
- `Dim_Date[Date_Key]` $\xrightarrow{1 \dots \infty}$ `Fact_Patient_Visits[Date_Key]`
- Hướng lọc: **Single (Dim filters Fact)**.

---

#### Nạp 12 công thức DAX Measures:
Mở file `Clinical_DW_Labs_1_to_6/powerbi/dax_measures.dax`, vào tab **Report View** $\rightarrow$ Chọn bảng `Fact_Patient_Visits` $\rightarrow$ Chọn **New Measure** và sao chép từng công thức:

```dax
Total Visits = COUNTROWS('Fact_Patient_Visits')

Total Revenue = SUM('Fact_Patient_Visits'[Total_Cost])

Total Insurance Covered = SUM('Fact_Patient_Visits'[Insurance_Covered_Amount])

Total Patient Paid = SUM('Fact_Patient_Visits'[Patient_Paid_Amount])

Avg Revenue Per Visit = DIVIDE([Total Revenue], [Total Visits], 0)

Avg Waiting Time (Min) = AVERAGE('Fact_Patient_Visits'[Waiting_Time_Minutes])

Avg Length of Stay (Days) = 
CALCULATE(
    AVERAGE('Fact_Patient_Visits'[Length_Of_Stay_Days]),
    'Fact_Patient_Visits'[Length_Of_Stay_Days] > 0
)

Insurance Coverage % = DIVIDE([Total Insurance Covered], [Total Revenue], 0)

Avg Revenue Per Patient = 
AVERAGEX(
    VALUES('Fact_Patient_Visits'[Patient_Key]),
    [Total Revenue]
)

Avg Monthly Revenue = 
AVERAGEX(
    VALUES('Dim_Date'[Year_Month]),
    [Total Revenue]
)

Total Bed Days = SUM('Fact_Patient_Visits'[Length_Of_Stay_Days])

Bed Occupancy Rate % = 
VAR TotalAvailableBeds = 50
VAR DaysInPeriod = DISTINCTCOUNT('Dim_Date'[Full_Date])
RETURN DIVIDE([Total Bed Days], TotalAvailableBeds * DaysInPeriod, 0)
```

---

#### Bố cục Dashboard khuyến nghị (3 trang báo cáo chuyên nghiệp):

```
┌────────────────────────────────────────────────────────────────────────┐
│ DASHBOARD 1: TỔNG QUAN ĐIỀU HÀNH BỆNH VIỆN (EXECUTIVE OVERVIEW)       │
├────────────────────────────────────────────────────────────────────────┤
│ [KPI Card 1]      [KPI Card 2]        [KPI Card 3]      [KPI Card 4]   │
│ Tổng lượt khám    Tổng viện phí       Thời gian chờ TB  Tỷ lệ bảo hiểm │
│ 200 lượt          $551,249.85         36.8 Phút         43.5%          │
├───────────────────────────────────────┬────────────────────────────────┤
│ Biểu đồ cột:                          │ Biểu đồ tròn:                  │
│ Doanh thu và lượt khám theo tháng     │ Tỷ trọng nhóm bệnh (ICD-10)    │
│ (Trục X: Dim_Date[Year_Month])        │ (Dim_Diagnosis[Disease_Category│
└───────────────────────────────────────┴────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ DASHBOARD 2: HIỆU SUẤT KHOA PHÒNG & NGUỒN LỰC Y TẾ (CLINICAL OPS)     │
├────────────────────────────────────────────────────────────────────────┤
│ Biểu đồ thanh ngang:                  │ Biểu đồ nhiệt (Matrix Heatmap):│
│ Thời gian chờ theo Chuyên khoa/Bác sĩ │ Số lượt khám theo Ca trực      │
│ (Trục Y: Dim_Doctor[Doctor_Name])     │ (Morning / Afternoon / Night)  │
├───────────────────────────────────────┴────────────────────────────────┤
│ Thước đo Gauge / KPI Card:                                             │
│ Công suất giường bệnh nội trú (Bed Occupancy Rate %)                   │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ DASHBOARD 3: TÀI CHÍNH & THU HỒI VIỆN PHÍ (FINANCIAL ANALYTICS)        │
├────────────────────────────────────────────────────────────────────────┤
│ Biểu đồ Donut: Trạng thái hóa đơn     │ Bảng phân tích chi tiết:       │
│ - Đã thanh toán (Paid): 31.5%         │ Doanh thu theo Hạng bảo hiểm   │
│ - Tồn đọng/Thất thoát: 68.5%          │ (Self-Pay, Basic, Premium)     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 KẾT QUẢ PHÂN TÍCH THỰC TẾ TỪ DATASET (INSIGHTS)

Từ việc vận hành pipeline và truy vấn trên bộ dữ liệu thực tế:
- **Tài chính bệnh viện:** Tổng viện phí ghi nhận là **\$551,249.85**. Tuy nhiên, tỷ lệ thực thu tiền mặt/đã hoàn tất chỉ đạt **31.46% (\$173,424.90)**. Có tới **68.54%** viện phí đang nằm ở trạng thái chờ xử lý (**Pending: \$184,612.01**) hoặc giao dịch thất bại (**Failed: \$193,212.94**), là khuyến nghị then chốt để ban giám đốc siết chặt quy trình thu ngân.
- **Tổn thất công suất phòng khám (No-show & Cancellation):** Trong 200 lượt hẹn, chỉ có **23% (46 lượt) hoàn thành khám**, trong khi có tới **26% (52 lượt) bệnh nhân bỏ hẹn không đến (No-show)** và **25.5% (51 lượt) bị hủy**. Tức **51.5% thời gian và nguồn lực bác sĩ bị lãng phí**.
- **Khoa phòng có tỷ lệ No-show cao nhất:** Da liễu (Dermatology - 31%) và Nhi khoa (Eastside Clinic - 31.8%). Kho dữ liệu đã chỉ ra chính xác vị trí cần triển khai hệ thống nhắn tin nhắc lịch hẹn tự động (SMS/Zalo Reminder) trước 24 giờ.

---

## 🛠 XỬ LÝ SỰ CỐ THƯỜNG GẶP (TROUBLESHOOTING)

| Hiện tượng lỗi | Nguyên nhân | Cách khắc phục |
| :--- | :--- | :--- |
| `Access denied for user 'root'@'localhost'` | Sai mật khẩu MySQL trong file `config.py` | Mở `Clinical_DW_Labs_1_to_6/config.py`, kiểm tra lại `MYSQL_PASSWORD`. Nếu dùng XAMPP hãy để trống `""`. |
| `Can't connect to MySQL server on 'localhost'` | Dịch vụ MySQL chưa được bật | Mở XAMPP Control Panel nhấn **Start** tại mục MySQL, hoặc gõ lệnh `net start MySQL80` trong Command Prompt (Run as Administrator). |
| `FileNotFoundError: Missing CSV files...` | Thiếu file dữ liệu trong thư mục `data/` | Kiểm tra thư mục `Clinical_DW_Labs_1_to_6/data/` đảm bảo đã có đủ 5 file `.csv` (`patients`, `doctors`, `appointments`, `treatments`, `billing`). |
| `ModuleNotFoundError: No module named 'sqlalchemy'` | Chưa cài đặt thư viện vào Python | Mở Terminal chạy lệnh: `pip install -r requirements.txt`. |
| `This connector requires one or more additional components...` | Power BI thiếu MySQL Connector/NET | Tải và cài đặt file MSI [MySQL Connector/NET 8.0.33](https://downloads.mysql.com/archives/c-net/) rồi khởi động lại Power BI Desktop. |

---

## 🎓 CẨM NANG BẢO VỆ ĐỒ ÁN TRƯỚC HỘI ĐỒNG (Q&A DEFENSE)

Dưới đây là 4 câu hỏi trọng tâm mà Thầy Cô hội đồng thường chất vấn và cách trả lời thuyết phục nhất:

### Câu 1: *"Tại sao không truy vấn báo cáo trực tiếp trên CSDL vận hành (OLTP) mà phải tốn công xây dựng Kho dữ liệu (Data Warehouse)?"*
> **Trả lời:**  
> Hệ thống OLTP được chuẩn hóa mức cao (3NF) nhằm phục vụ thao tác ghi/đọc từng dòng đơn lẻ nhanh chóng và chống trùng lặp. Khi chạy báo cáo phân tích tổng hợp (Aggregations như `SUM`, `AVG`, `GROUP BY`) trên OLTP, hệ thống phải thực hiện nhiều phép Join phức tạp qua các chuỗi ký tự, gây nghẽn tài nguyên và khóa bảng (table locking), làm tê liệt hoạt động tiếp đón bệnh nhân tại bệnh viện. Kho dữ liệu tách rời môi trường phân tích khỏi môi trường vận hành, chuyển đổi sang Star Schema dùng khóa thay thế (Surrogate Key) giúp tăng tốc độ truy vấn gấp nhiều lần mà không ảnh hưởng đến hệ thống khám chữa bệnh hàng ngày.

### Câu 2: *"Nhóm đã xử lý vấn đề bảo mật thông tin nhạy cảm của bệnh nhân như thế nào trong quá trình ETL?"*
> **Trả lời:**  
> Trong bước ETL chuyển tiếp (Lab 3), nhóm áp dụng tiêu chuẩn bảo mật y tế HIPAA/GDPR thông qua giải thuật băm một chiều mật mã học **SHA-256** để tạo ra `Anonymized_Patient_ID`. Toàn bộ thông tin nhạy cảm định danh trực tiếp như số điện thoại, số định danh cá nhân gốc đều được loại bỏ trước khi dữ liệu đi vào Kho dữ liệu phân tích.

### Câu 3: *"Kỹ thuật SCD Type 2 trong đồ án giải quyết bài toán nghiệp vụ gì của bệnh viện?"*
> **Trả lời:**  
> Trong môi trường y tế, các bác sĩ có thể thay đổi học vị, nâng bậc thâm niên, hoặc luân chuyển chi nhánh bệnh viện. Nếu áp dụng SCD Type 1 (ghi đè), toàn bộ các ca khám trong quá khứ của bác sĩ đó sẽ bị gắn sai vào chi nhánh mới, làm sai lệch báo cáo tài chính lịch sử. Nhóm áp dụng **SCD Type 2**: Khi bác sĩ có sự thay đổi chi nhánh/chuyên khoa, bản ghi cũ được giữ nguyên và đánh dấu ngày kết thúc (`End_Date = ngày đổi`, `Is_Current = 0`), đồng thời chèn một bản ghi mới với mã khóa `Doctor_Key` mới (`Is_Current = 1`). Nhờ đó, bệnh viện vừa giữ được tính toàn vẹn của lịch sử điều trị trong quá khứ, vừa theo dõi được hiện trạng nhân sự mới nhất.

### Câu 4: *"Giải thích ý nghĩa của các chỉ số trong kết quả `EXPLAIN ANALYZE` ở Lab 5?"*
> **Trả lời:**  
> Lệnh `EXPLAIN ANALYZE` của MySQL 8.0 thực thi câu truy vấn thực tế trên bộ máy tính toán và đo lường chi tiết: thời gian thực hiện bước đầu tiên (*actual time*), số dòng quét thực tế (*rows*), số vòng lặp (*loops*) và chi phí ước tính (*Query Cost*). Kết quả thực nghiệm cho thấy trên Star Schema, nhờ việc Join trên các khóa Surrogate Key số nguyên có chỉ mục (Index) và cấu trúc bảng Fact tập trung, chi phí tính toán và số dòng đọc tạm thời giảm thiểu rõ rệt so với việc phải Join xuyên suốt 4 bảng 3NF trên hệ thống OLTP.

---

## 🏆 KẾT LUẬN & LIÊN HỆ

Đồ án đã hoàn thành xuất sắc 100% mục tiêu học phần Kho Dữ liệu: từ thiết kế kiến trúc, làm sạch khử định danh, tích hợp đa nguồn, quản trị biến động dữ liệu lịch sử đến benchmark hiệu năng và trực quan hóa phân tích quản trị trên Power BI.

*Mọi thắc mắc kỹ thuật trong quá trình chạy thử nghiệm, vui lòng liên hệ Nhóm tác giả 24GITe – Khoa Khoa học Máy tính, Trường Đại học Công nghệ Thông tin và Truyền thông Việt - Hàn (VKU).*
