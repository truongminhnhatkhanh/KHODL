# 📊 HƯỚNG DẪN MỞ BÁO CÁO SSRS TRONG MICROSOFT VISUAL STUDIO 2026

Thư mục này chứa trọn bộ **Report Server Project (`Hospital_CDW_Reports`)** theo chuẩn **SQL Server Reporting Services (SSRS)** kết nối trực tiếp tới Kho dữ liệu **`hospital_dw`** trên MySQL 8.0 qua **ODBC**.

---

## 1. Cấu trúc thư mục `ssrs_reports/`
- `Hospital_CDW_Reports.sln`: Solution mở trực tiếp trong Visual Studio.
- `Hospital_CDW_Reports.rptproj`: Project Report Server chứa Data Source, Shared Datasets và 3 báo cáo `.rdl`.
- `DS_Hospital_DW.rds`: Shared Data Source dùng `Extension = ODBC`, trỏ tới System DSN `Hospital_DW`.
- `DS_WaitTime.rsd`, `DS_ClinicalOps.rsd`, `DS_Finance.rsd`: 3 Shared Datasets truy vấn Star Schema (`hospital_dw`).
- `Rpt_WaitTime_Heatmap.rdl`: Báo cáo 1 — Bản đồ nhiệt thời gian chờ khám (Matrix).
- `Rpt_ClinicalOps_LOS.rdl`: Báo cáo 2 — Vận hành lâm sàng, ngày nằm viện (LOS) & cơ cấu dịch vụ (Chart + Tablix).
- `Rpt_Revenue_Insurance.rdl`: Báo cáo 3 — Tài chính viện phí & bảo hiểm y tế theo ICD-10 (Stacked Bar Chart + Tablix).
- `previews/`: Chứa 3 ảnh biểu đồ màu (nguyên gốc) xuất trực tiếp từ dữ liệu `hospital_dw` dùng minh họa trong báo cáo.

---

## 2. Yêu cầu cài đặt để bấm `Preview` trong Visual Studio 2026
1. **Cài extension trong Visual Studio 2026:**
   - Mở **Visual Studio Community 2026** → `Extensions` → `Manage Extensions...`.
   - Tìm **`Microsoft Reporting Services Projects 2022+`** → chọn **Install** → đóng Visual Studio để tiến trình VSIX Installer cài xong.
2. **Cài MySQL Connector/ODBC & tạo System DSN tên `Hospital_DW`:**
   - Tải và cài đặt **MySQL Connector/ODBC** (Windows 64-bit) từ [dev.mysql.com/downloads/connector/odbc](https://dev.mysql.com/downloads/connector/odbc/).
   - Mở **ODBC Data Sources (64-bit)** trên Windows → tab **System DSN** → **Add...** → chọn **MySQL ODBC Unicode Driver**.
   - Nhập:
     - **Data Source Name:** `Hospital_DW`
     - **TCP/IP Server:** `localhost` | **Port:** `3306`
     - **User:** `root` | **Password:** *(mật khẩu trong `config.py`)*
     - **Database:** `hospital_dw`
   - Bấm **Test** → **OK**.
3. **Mở Project & Xem báo cáo:**
   - Mở `Hospital_CDW_Reports.sln` bằng Visual Studio 2026.
   - Mở từng tệp `.rdl` trong **Solution Explorer** → chuyển sang tab **Preview** để xem dữ liệu thực tế và chụp ảnh màn hình nếu cần.
