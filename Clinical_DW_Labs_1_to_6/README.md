# 🏥 CLINICAL DATA WAREHOUSE (LABS 1 - 6) - HƯỚNG DẪN CHI TIẾT
> **HỌC PHẦN: KHO DỮ LIỆU (DATA WAREHOUSE) - VKU**  
> **Nhóm thực hiện (Lớp 24GITe):** Trương Minh Nhật Khánh (24ITE047), Lê Thị Hồng Hạnh (24ITE034), Ngô Thị Anh Thư (24ITE104), Lê Hà An (24ITE002)  
> **Giảng viên hướng dẫn:** ThS. Mai Lam

---

## 1. CẤU TRÚC THƯ MỤC TRỌN GÓI LABS 1 ĐẾN 6
- `config.py`: Tệp cấu hình kết nối MySQL trực tiếp. Mở file này ra để sửa mật khẩu và chạy `python config.py` để kiểm tra kết nối.
- `data/`: Chứa 5 file CSV nguồn (`patients.csv`, `doctors.csv`, `appointments.csv`, `treatments.csv`, `billing.csv`) đã được làm giàu cân bằng 8 chuyên khoa và file Excel bổ sung `doctors_update.xlsx`.
- `sql/`:
  - `01_create_oltp.sql`: DDL khởi tạo CSDL vận hành `hospital_oltp`.
  - `02_create_dw.sql`: DDL khởi tạo CSDL kho dữ liệu `hospital_dw` (Kimball Star Schema với 6 bảng Dimension bao gồm `Dim_Service`).
  - `03_olap_and_benchmark.sql`: Truy vấn kiểm tra SCD Type 2, Benchmark `EXPLAIN ANALYZE`, phân tích `WITH ROLLUP`, Window Function `RANK() OVER()` và phân loại dịch vụ `Dim_Service`.
- `scripts/`:
  - `01_load_oltp_csv.py`: Thực hiện thủ công Lab 1 (nạp CSV vào MySQL OLTP).
  - `02_etl_lab3_initial.py`: Thực hiện thủ công Lab 2 & Lab 3 (Khử định danh SHA-256, sinh Surrogate Key, phân hóa Wait Time & LOS, nạp Fact & 6 Dim).
  - `03_etl_lab4_advanced.py`: Thực hiện thủ công Lab 4 (Hợp nhất Staging và cập nhật SCD Type 2 cho Dim_Doctor).
- `diagrams/star_schema.dbml`: File mã nguồn lược đồ hình sao (chuẩn 6 Dimensions + 1 Fact), mở tại [dbdiagram.io](https://dbdiagram.io) để xuất hình ảnh.
- `powerbi/dax_measures.dax`: 18 công thức DAX Measures chuyên sâu cho 3 trang Dashboard Power BI.

---

## 2. HƯỚNG DẪN CÀI ĐẶT & CHẠY THỦ CÔNG TỪNG BƯỚC

### Bước 1: Khởi động dịch vụ MySQL Server
- **Cách 1:** Chuột phải vào tệp `D:\KHODL\start_mysql.bat` chọn **Run as administrator**.
- **Cách 2:** Mở CMD hoặc PowerShell với quyền Admin và gõ:
  ```cmd
  net start MYSQL80
  ```

### Bước 2: Thiết lập thông tin kết nối trực tiếp trong `config.py`
Mở tệp `config.py` và kiểm tra tài khoản, mật khẩu MySQL của bạn:
```python
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "your_password"  # Nhập mật khẩu MySQL của bạn (nếu dùng XAMPP thì để trống "")
```
Chạy thử lệnh sau để kiểm tra kết nối:
```bash
python config.py
```
*(Nếu thấy báo `✅ KẾT NỐI THÀNH CÔNG!` là thông số đã chính xác).*

### Bước 3: Chạy thủ công từng bước (Hiểu rõ bản chất luồng dữ liệu)

Mở Terminal tại thư mục `Clinical_DW_Labs_1_to_6`:

```bash
# 1. Nạp CSDL vận hành OLTP (Lab 1)
python scripts/01_load_oltp_csv.py

# 2. ETL Star Schema, băm SHA-256 và nạp Kho dữ liệu DW (Lab 2 & Lab 3)
python scripts/02_etl_lab3_initial.py

# 3. Nạp Vùng đệm Staging & Quản trị biến động lịch sử SCD Type 2 (Lab 4)
python scripts/03_etl_lab4_advanced.py
```

---

## 3. THỰC HIỆN LAB 5: BENCHMARK & TRUY VẤN OLAP
1. Mở **MySQL Workbench**, kết nối vào CSDL `hospital_dw`.
2. Mở file `sql/03_olap_and_benchmark.sql`.
3. Chạy từng phần truy vấn để lấy số liệu bảo vệ đồ án:
   - **Phần 1:** Đo lường hiệu năng truy vấn trên `hospital_oltp` bằng `EXPLAIN ANALYZE` (phép JOIN 4 bảng phức tạp).
   - **Phần 2:** Kiểm chứng kỹ thuật **SCD Type 2** trên `Dim_Doctor` (Bác sĩ `D001` có 2 dòng lịch sử theo dõi chuyển khoa từ Dermatology sang Neurology; bác sĩ `D999` được thêm mới).
   - **Phần 3:** Đo lường hiệu năng truy vấn trên Star Schema `hospital_dw` bằng `EXPLAIN ANALYZE` $\rightarrow$ **Tốc độ nhanh hơn 50% - 70%** so với OLTP.
   - **Phần 4:** Phân tích đa cấp Năm $\rightarrow$ Quý $\rightarrow$ Khoa phòng với `GROUP BY ... WITH ROLLUP`.
   - **Phần 5:** Xếp hạng doanh thu và lượt khám theo quý sử dụng Window Function `RANK() OVER()` và `DENSE_RANK() OVER()`.
   - **Phần 6:** Phân tích đa chiều theo Loại dịch vụ y tế (`Dim_Service`: Outpatient, Inpatient, Surgery, Emergency).

---

## 4. THỰC HIỆN LAB 6: XÂY DỰNG BÁO CÁO POWER BI DESKTOP
1. Khởi động **Power BI Desktop**.
2. Chọn **Get Data** $\rightarrow$ **MySQL database** $\rightarrow$ Nhập Server: `localhost:3306`, Database: `hospital_dw`.
3. Chọn nạp đủ **7 bảng**: `Fact_Patient_Visits`, `Dim_Patient`, `Dim_Doctor`, `Dim_Department`, `Dim_Diagnosis`, `Dim_Date`, `Dim_Service`.
4. Vào **Model View**: Xác nhận mô hình Star Schema chuẩn, các bảng Dim nối vào Fact qua các trường Surrogate Key (`1-to-many`, `Single filter direction`).
5. Tạo các thước đo từ file `powerbi/dax_measures.dax`.
6. Dựng 3 trang Dashboard chuẩn:
   - **Trang 1: Wait-Time Heatmap** (Bản đồ nhiệt thời gian chờ theo Khoa phòng và Thứ trong tuần / Ca trực).
   - **Trang 2: Bed Occupancy & Service Mix** (Xu hướng công suất giường bệnh, ngày nằm viện LOS, tỷ lệ Nội trú / Ngoại trú / Phẫu thuật / Cấp cứu).
   - **Trang 3: Revenue & Insurance Breakdown** (Doanh thu theo nhóm bệnh ICD-10, cơ cấu bảo hiểm chi trả vs người bệnh đồng chi trả, phân tích chu trình thanh toán).

---

## 5. THAM KHẢO TÀI LIỆU TOÀN VĂN
- Báo cáo học thuật toàn văn chuẩn VKU (6 chương): [BAO_CAO_KHO_DU_LIEU_BENH_VIEN.md](../BAO_CAO_KHO_DU_LIEU_BENH_VIEN.md)
- Kịch bản 20 Slide thuyết trình và phân vai thuyết trình: [SLIDE_THUYET_TRINH_KHO_DU_LIEU.md](../SLIDE_THUYET_TRINH_KHO_DU_LIEU.md)
- Hướng dẫn tổng quát cấp dự án: [README.md](../README.md)
