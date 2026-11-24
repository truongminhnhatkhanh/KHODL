import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def create_document():
    doc = docx.Document()
    
    # Page Setup: Standard 1 inch margins
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
        # Header
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("Báo cáo Kho Dữ Liệu Lâm Sàng (Clinical Data Warehouse - CDW) | VKU")
        hrun.font.name = "Arial"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)
        
        # Footer
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run("Trang nội dung học thuật – Học phần Kho Dữ Liệu (Data Warehouse) – VKU")
        frun.font.name = "Arial"
        frun.font.size = Pt(8.5)
        frun.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)

    # Styles helper
    NAVY = RGBColor(0x0F, 0x17, 0x2A)      # #0F172A
    SKY_BLUE = RGBColor(0x02, 0x84, 0xC7)  # #0284C7
    SLATE = RGBColor(0x47, 0x55, 0x69)     # #475569
    DARK_TEXT = RGBColor(0x1E, 0x29, 0x3B) # #1E293B

    def set_cell_background(cell, fill_hex):
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
        cell._tc.get_or_add_tcPr().append(shd)

    def set_cell_margins(cell, top=120, bottom=120, left=160, right=160):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
        tcPr.append(tcMar)

    def set_table_borders(table, color="CBD5E1", sz="4"):
        tblPr = table._tbl.tblPr
        borders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'<w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:left w:val="none"/>'
            f'<w:right w:val="none"/>'
            f'<w:insideV w:val="none"/>'
            f'</w:tblBorders>'
        )
        tblPr.append(borders)

    def add_callout(text, title=None, border_color="0284C7", bg_color="F8FAFC"):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.5)
        set_cell_background(cell, bg_color)
        set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
        
        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'<w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>'
            f'<w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/>'
            f'</w:tcBorders>'
        )
        tcPr.append(borders)
        
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        if title:
            trun = p.add_run(title + "\n")
            trun.font.name = "Arial"
            trun.font.size = Pt(10.5)
            trun.font.bold = True
            trun.font.color.rgb = SKY_BLUE
        
        mrun = p.add_run(text)
        mrun.font.name = "Arial"
        mrun.font.size = Pt(10.0)
        mrun.font.italic = False
        mrun.font.color.rgb = DARK_TEXT
        
        # Add a tiny spacing paragraph after table
        sp = doc.add_paragraph()
        sp.paragraph_format.space_before = Pt(0)
        sp.paragraph_format.space_after = Pt(4)

    def add_code_block(code_text, lang_title=None):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.5)
        set_cell_background(cell, "0F172A") # Dark Navy background for code
        set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
        
        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'<w:left w:val="single" w:sz="18" w:space="0" w:color="38BDF8"/>'
            f'<w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/>'
            f'</w:tcBorders>'
        )
        tcPr.append(borders)
        
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.1
        if lang_title:
            trun = p.add_run(f"/* {lang_title} */\n")
            trun.font.name = "Consolas"
            trun.font.size = Pt(9.0)
            trun.font.bold = True
            trun.font.color.rgb = RGBColor(0x38, 0xBD, 0xF8) # Sky blue text
        
        crun = p.add_run(code_text)
        crun.font.name = "Consolas"
        crun.font.size = Pt(9.0)
        crun.font.color.rgb = RGBColor(0xF1, 0xF5, 0xF9) # Light text
        
        sp = doc.add_paragraph()
        sp.paragraph_format.space_before = Pt(0)
        sp.paragraph_format.space_after = Pt(4)

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(13.5)
        r.font.bold = True
        r.font.color.rgb = NAVY
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(11.5)
        r.font.bold = True
        r.font.color.rgb = SKY_BLUE
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(7)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(10.5)
        r.font.bold = True
        r.font.color.rgb = DARK_TEXT
        return p

    def add_p(text, bold_prefix=None):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = "Arial"
            r_pre.font.size = Pt(10.0)
            r_pre.font.bold = True
            r_pre.font.color.rgb = DARK_TEXT
        r = p.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(10.0)
        r.font.color.rgb = DARK_TEXT
        return p

    # ========================== COVER / HEADER BLOCK ==========================
    p_inst = doc.add_paragraph()
    p_inst.paragraph_format.space_before = Pt(0)
    p_inst.paragraph_format.space_after = Pt(2)
    r_inst = p_inst.add_run("TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN VÀ TRUYỀN THÔNG VIỆT - HÀN (VKU)\nKHOA KHOA HỌC MÁY TÍNH – HỌC PHẦN: KHO DỮ LIỆU (DATA WAREHOUSE)")
    r_inst.font.name = "Arial"
    r_inst.font.size = Pt(9.5)
    r_inst.font.bold = True
    r_inst.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(6)
    p_title.paragraph_format.space_after = Pt(4)
    r_title = p_title.add_run("BÁO CÁO TỔNG QUAN HỌC THUẬT TOÀN DIỆN:\nTHIẾT KẾ VÀ TRIỂN KHAI KHO DỮ LIỆU Y TẾ LÂM SÀNG (CDW)")
    r_title.font.name = "Arial"
    r_title.font.size = Pt(17.0)
    r_title.font.bold = True
    r_title.font.color.rgb = NAVY

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(8)
    r_sub = p_sub.add_run("Tối Ưu Hóa Quy Trình Điều Trị Bệnh Nhân, Phân Bổ Nguồn Lực Bệnh Viện & Đối Chiếu Toàn Diện Đề Cương Bài Giảng VKU")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(10.5)
    r_sub.font.italic = True
    r_sub.font.color.rgb = SLATE

    add_callout(
        "Tài liệu này tổng hợp toàn bộ cơ sở lý thuyết, kiến trúc kỹ thuật, quy trình thực nghiệm và kết quả đo chuẩn của đồ án Kho Dữ Liệu Y Tế Lâm Sàng (Clinical Data Warehouse - CDW). Báo cáo đối chiếu trực tiếp với 15 tài liệu giáo trình chính thức của VKU (Lecture 01-05, Lab 01-06) cùng các chuẩn mực quốc tế về Mô hình hóa Đa chiều (Ralph Kimball), Kiến trúc Doanh nghiệp (W.H. Inmon) và Tiêu chuẩn Bảo mật Y tế (HIPAA / Thông tư 46/2018/TT-BYT).",
        title="MỤC ĐÍCH & PHẠM VI BÁO CÁO HỌC THUẬT"
    )

    # ========================== PHẦN 1: OVERVIEW ĐỀ TÀI ==========================
    add_h1("PHẦN 1: OVERVIEW ĐỀ TÀI")
    
    add_h2("1.1. Tổng quan đề tài & Định nghĩa Kho Dữ Liệu (Trích dẫn: Lecture 01 & Chương 1.1)")
    add_p("Kho dữ liệu lâm sàng (Clinical Data Warehouse - CDW) là hệ thống cơ sở dữ liệu chuyên biệt phục vụ phân tích quản trị, được thiết kế để tích hợp toàn diện các nguồn dữ liệu y tế phân tán nhằm hỗ trợ lãnh đạo bệnh viện và đội ngũ y bác sĩ ra các quyết định điều trị và phân bổ nguồn lực dựa trên bằng chứng định lượng.")
    
    add_callout(
        '"A data warehouse is a subject-oriented, integrated, non-volatile, and time-variant collection of data in support of management\'s decision-making process."\n(Tạm dịch: Kho dữ liệu là tập hợp dữ liệu hướng chủ đề, tích hợp, bất biến và biến thiên theo thời gian nhằm hỗ trợ quy trình ra quyết định của nhà quản lý).',
        title="ĐỊNH NGHĨA KINH ĐIỂN VỀ KHO DỮ LIỆU (W.H. INMON, 1992, 2005 - LECTURE 01 SLIDE 5)"
    )

    add_p("Bốn đặc tính cốt lõi của Kho dữ liệu được hiện thực hóa trọn vẹn trong đồ án:")
    add_p("Dữ liệu được tổ chức xoay quanh các đối tượng nghiệp vụ cốt lõi: Bệnh nhân, Bác sĩ, Lượt khám, Chẩn đoán, Dịch vụ và Doanh thu viện phí thay vì phân theo nghiệp vụ nhập liệu tác vụ hàng ngày.", bold_prefix="1. Hướng chủ đề (Subject-oriented): ")
    add_p("Đồng bộ dữ liệu dị thể từ nhiều nguồn phân tán (HIS, LIS, EMR, Billing, Excel nhân sự), giải quyết triệt để xung đột về định dạng dữ liệu, đơn vị đo lường và mã hóa bệnh tật.", bold_prefix="2. Tích hợp (Integrated): ")
    add_p("Dữ liệu sau khi nạp vào mang tính chất lịch sử ổn định, chỉ thực hiện thao tác Đọc (Read) và Nạp gia tăng (Append/Load), không bao giờ bị ghi đè hoặc sửa đổi tùy tiện như CSDL tác nghiệp.", bold_prefix="3. Bất biến (Non-volatile): ")
    add_p("Mọi bản ghi khám chữa bệnh đều được gắn với chiều thời gian đa cấp (Năm, Quý, Tháng, Ngày, Ca trực), cho phép truy vết lịch sử bệnh án và phân tích xu hướng dịch tễ nhiều năm.", bold_prefix="4. Biến thiên theo thời gian (Time-variant): ")

    add_h2("1.2. Lý do chọn đề tài & Thách thức thực tiễn trong ngành Y tế (Trích dẫn: Chương 1.2)")
    add_p("Thực trạng hoạt động tại các bệnh viện hiện đại đặt ra 4 thách thức cấp bách (Pain Points) thúc đẩy việc bắt buộc phải xây dựng Kho dữ liệu:")
    add_p("Các hệ thống quản lý bệnh viện (HIS), hồ sơ bệnh án điện tử (EMR), quản lý xét nghiệm (LIS) và viện phí (Billing) hoạt động hoàn toàn tách biệt trên nhiều máy chủ khác nhau, cấu trúc bảng khác nhau và không có mã khóa định danh thống nhất.", bold_prefix="• Hiện tượng 'Ốc đảo dữ liệu' (Data Silos): ")
    add_p("Khi ban giám đốc chạy các truy vấn phân tích tổng hợp (GROUP BY, JOIN 10-15 bảng 3NF với hàng triệu dòng) trực tiếp trên CSDL vận hành (OLTP), máy chủ sẽ bị khóa bảng (Table Locking) hoặc nghẽn hàng đợi (Deadlocks), làm ngừng trệ hoạt động tiếp nhận cấp cứu và phòng phẫu thuật.", bold_prefix="• Nguy cơ làm tê liệt hệ thống cấp cứu sống còn (Operational Contention - Lecture 01 Slide 12): ")
    add_p("Danh tính bệnh nhân (Họ tên, SĐT, Địa chỉ, CMND) tuyệt đối không được để lộ cho đội ngũ phân tích kinh doanh (BI Analysts). Cần cơ chế khử định danh (De-identification) bằng hàm băm mật mã học một chiều trước khi nạp vào môi trường phân tích.", bold_prefix="• Rào cản pháp lý & Bảo mật danh tính người bệnh (HIPAA / Thông tư 46/2018/TT-BYT): ")
    add_p("Bác sĩ thường xuyên luân chuyển khoa phòng hoặc chi nhánh công tác. Nếu áp dụng ghi đè thông thường (SCD Type 1), toàn bộ các ca khám trong quá khứ sẽ bị gắn nhầm vào khoa mới, làm sai lệch báo cáo tài chính lịch sử.", bold_prefix="• Quản trị biến động nhân sự y tế (SCD Problem - Lecture 02 Slide 28): ")

    add_h2("1.3. Nguồn Dataset thực nghiệm & Quy mô dữ liệu (Trích dẫn: Chương 3.1 & 5.1)")
    add_p("Dữ liệu thực nghiệm của đề tài được tổng hợp từ dữ liệu giao dịch lâm sàng thực tế dựa trên chuẩn y tế quốc tế 'Hospital Length of Stay / Healthcare Benchmark' kết hợp dữ liệu vận hành đa nguồn gồm 5.200 ca khám lâm sàng:")
    add_p("Tệp dữ liệu phẳng ban đầu gồm 5.200 dòng giao dịch và 36 thuộc tính lâm sàng.", bold_prefix="• healthcare_dataset.csv: ")
    add_p("5.048 hồ sơ bệnh nhân duy nhất (patients.csv), 20 bác sĩ chuyên khoa duy nhất (doctors.csv), 5.200 lượt hẹn khám (appointments.csv), 5.200 kết quả cận lâm sàng/thuốc (treatments.csv) và 5.200 giao dịch thanh toán viện phí (billing.csv).", bold_prefix="• 5 Thực thể chuẩn hóa 3NF nguồn: ")
    add_p("Danh mục chẩn đoán được ánh xạ chuẩn theo Phân loại Quốc tế về Bệnh tật lần thứ 10 của Tổ chức Y tế Thế giới (WHO ICD-10).", bold_prefix="• Danh mục ICD-10 Quốc tế: ")

    # ========================== PHẦN 2: CÔNG NGHỆ VÀ CÔNG CỤ ==========================
    add_h1("PHẦN 2: CÔNG NGHỆ VÀ CÔNG CỤ SỬ DỤNG")
    add_p("Bảng đối chiếu giữa bộ công cụ chuẩn Microsoft BI Stack (giảng dạy trong giáo trình VKU) và kiến trúc triển khai thực nghiệm trong đồ án:")

    tools_data = [
        ("Phân hệ kiến trúc", "Công nghệ chuẩn VKU (Labs 01-06)", "Công nghệ triển khai trong Đồ án", "Lý do lựa chọn học thuật (Chương 2.2)"),
        ("Lưu trữ CSDL (Storage)", "SQL Server Management Studio (SSMS)", "MySQL Server 8.0 CE & SSMS Scripts", "Lưu trữ InnoDB, chỉ mục B-tree, khả năng mở rộng mã nguồn mở và tương thích ANSI SQL."),
        ("Trích xuất & Biến đổi (ETL)", "SQL Server Integration Services (SSIS)", "Python Pipeline (pandas, hashlib) & SSIS Packages", "Xử lý linh hoạt logic thuật toán băm bảo mật SHA-256 có Salt, SCD Type 2 tự động hóa 100%."),
        ("Khối đa chiều (OLAP)", "SQL Server Analysis Services (SSAS Cube)", "SSAS Cube Spec, MDX & MySQL Analytic Rollup", "Tối ưu hóa đa chiều với khối lập phương SSAS Multidimensional và toán tử GROUP BY ROLLUP."),
        ("Báo cáo & Trực quan hóa (BI)", "SSRS & Power BI Desktop", "Microsoft Power BI Desktop", "Xây dựng 18 thước đo DAX chuyên sâu, mô hình hóa Star Schema và thiết kế 3 trang Dashboard tương tác."),
        ("Bảo mật y tế", "SQL Server Dynamic Data Masking", "Mật mã học SHA-256 có Salt", "Tuân thủ nghiêm ngặt chuẩn HIPAA và Thông tư 46/2018/TT-BYT."),
        ("Đo lường hiệu năng", "SQL Server Profiler / Execution Plan", "MySQL EXPLAIN ANALYZE", "Bóc tách chính xác chi phí tính toán (Query Cost), số khối I/O và thời gian thực thi mili-giây.")
    ]

    t_tools = doc.add_table(rows=len(tools_data), cols=4)
    t_tools.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_tools)
    for r_idx, row in enumerate(tools_data):
        for c_idx, val in enumerate(row):
            cell = t_tools.cell(r_idx, c_idx)
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            run = p.add_run(val)
            run.font.name = "Arial"
            if r_idx == 0:
                set_cell_background(cell, "0F172A")
                run.font.size = Pt(9.0)
                run.font.bold = True
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            else:
                if r_idx % 2 == 1:
                    set_cell_background(cell, "F8FAFC")
                run.font.size = Pt(8.5)
                run.font.color.rgb = DARK_TEXT
                if c_idx == 0:
                    run.font.bold = True

    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(6)

    # ========================== PHẦN 3: QUY TRÌNH THỰC HIỆN ==========================
    add_h1("PHẦN 3: QUY TRÌNH THỰC HIỆN CHI TIẾT & GIẢI THÍCH SƠ ĐỒ")

    add_h2("3.1. Bước 1: Khởi tạo CSDL Vận hành OLTP theo chuẩn 3NF (Trích dẫn: Lecture 01 & Chương 1.1)")
    add_p("Lý thuyết chuẩn hóa quan hệ của Edgar F. Codd (1970). Hệ thống vận hành tác nghiệp bắt buộc phải đạt Dạng chuẩn 3 (3NF) để loại bỏ hoàn toàn dư thừa dữ liệu và phục vụ giao dịch ACID đơn lẻ với tốc độ tức thời.", bold_prefix="• Cơ sở lý thuyết: ")
    add_p("1. Thực thi kịch bản SQL 01_create_oltp.sql khởi tạo CSDL hospital_oltp gồm 5 bảng có ràng buộc toàn vẹn khóa ngoại (FOREIGN KEY): patients, doctors, appointments, treatments, billing.\n2. Thực thi script Python 01_load_oltp_csv.py: Đọc tệp phẳng 5.200 dòng healthcare_dataset.csv, bóc tách lọc trùng (drop_duplicates) thành 5.048 bệnh nhân duy nhất và 20 bác sĩ duy nhất, chuẩn hóa chuỗi ngày tháng M/D/YYYY thành định dạng chuẩn ISO YYYY-MM-DD tương thích tuyệt đối với kiểu dữ liệu DATE của MySQL.", bold_prefix="• Chi tiết thực hiện: ")

    add_h2("3.2. Bước 2: Thiết kế Kho Dữ Liệu theo Phương pháp luận Ralph Kimball (Trích dẫn: Lecture 02 & Chương 3.2)")
    add_p("Đề tài áp dụng nghiêm ngặt quy trình 4 bước thiết kế Dimensional Modeling của Ralph Kimball (The Data Warehouse Toolkit - 3rd Edition):")
    add_p("Quy trình tiếp nhận, khám chữa bệnh lâm sàng và thanh toán viện phí (Patient Clinical Encounters).", bold_prefix="1. Chọn quy trình nghiệp vụ (Business Process): ")
    add_p("Mỗi bản ghi trong bảng sự kiện đại diện cho chính xác một lượt thăm khám ngoại trú hoặc một đợt nằm viện nội trú hoàn chỉnh của một bệnh nhân tại một khoa phòng (One row per clinical visit).", bold_prefix="2. Xác định mức độ chi tiết (Declare the Grain): ")
    add_p("6 bảng chiều ngữ cảnh: Dim_Patient (Bệnh nhân), Dim_Doctor (Bác sĩ), Dim_Facility (Khoa phòng), Dim_Date (Thời gian), Dim_Diagnosis (Chẩn đoán ICD-10), Dim_Service (Loại hình dịch vụ y tế).", bold_prefix="3. Xác định các chiều (Identify Dimensions): ")
    add_p("Phân tách thành 2 nhóm độ đo rõ rệt:\n   - Thước đo có thể cộng dồn (Additive Measures): Viện phí (Total_Cost), Bảo hiểm chi trả (Insurance_Covered_Amount), Bệnh nhân tự trả (Patient_Paid_Amount).\n   - Thước đo bán cộng dồn / trung bình (Non-additive / Averaged Measures): Thời gian chờ khám (Waiting_Time_Minutes), Số ngày nằm viện (Length_Of_Stay_Days).", bold_prefix="4. Xác định các độ đo (Identify Facts/Measures - Lecture 02 Slide 10): ")

    # ========================== 3.3. MA TRẬN BUS MATRIX (MỚI) ==========================
    add_h2("3.3. Ma trận Bus Matrix Toàn Bệnh Viện (Data Warehouse Bus Matrix - Trích dẫn: Lecture 02 Slide 21)")
    add_p("Trong phương pháp luận kiến trúc Ralph Kimball (The Data Warehouse Bus Architecture), Ma trận Bus Matrix là công cụ hoạch định chiến lược quan trọng nhất nhằm đảm bảo tính tích hợp và khả năng mở rộng không giới hạn của kho dữ liệu doanh nghiệp. Bằng cách định nghĩa các Chiều Dùng Chung (Conformed Dimensions), bệnh viện có thể phát triển từng phân hệ phân tích độc lập (Data Marts) theo thời gian mà không bao giờ bị xung đột ngữ nghĩa dữ liệu.")

    bus_matrix_data = [
        ("Quy trình Nghiệp vụ Y tế (Business Processes / Fact Tables)", "Dim_Date (Thời gian)", "Dim_Patient (Bệnh nhân)", "Dim_Doctor (Bác sĩ)", "Dim_Facility (Khoa phòng)", "Dim_Diagnosis (Chẩn đoán)", "Dim_Service (Dịch vụ)"),
        ("1. Khám chữa bệnh lâm sàng (Visits - Triển khai hiện tại)", "X", "X", "X", "X", "X", "X"),
        ("2. Quản lý Giường bệnh nội trú (Inpatient Bed Occupancy)", "X", "X", "", "X", "X", ""),
        ("3. Thu viện phí & Quyết toán BHYT (Billing & Claims)", "X", "X", "", "X", "", "X"),
        ("4. Kê đơn & Cấp phát Dược phẩm (Pharmacy Encounters)", "X", "X", "X", "X", "X", "X")
    ]

    t_bus = doc.add_table(rows=len(bus_matrix_data), cols=7)
    t_bus.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_bus)
    for r_idx, row in enumerate(bus_matrix_data):
        for c_idx, val in enumerate(row):
            cell = t_bus.cell(r_idx, c_idx)
            set_cell_margins(cell, top=70, bottom=70, left=80, right=80)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            if c_idx > 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(val)
            run.font.name = "Arial"
            if r_idx == 0:
                set_cell_background(cell, "0F172A")
                run.font.size = Pt(8.5)
                run.font.bold = True
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            else:
                if r_idx % 2 == 1:
                    set_cell_background(cell, "F8FAFC")
                run.font.size = Pt(8.5)
                run.font.color.rgb = DARK_TEXT
                if c_idx == 0:
                    run.font.bold = True
                if val == "X":
                    run.font.bold = True
                    run.font.color.rgb = SKY_BLUE

    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(4)

    add_callout(
        "Ý nghĩa học thuật của Bus Matrix: Ba chiều Dim_Date, Dim_Patient và Dim_Facility đóng vai trò là các Conformed Dimensions xuyên suốt toàn viện. Nhờ đó, lãnh đạo bệnh viện có thể thực hiện các phép phân tích giao thoa (Drill-across) giữa nhiều bảng Fact khác nhau: ví dụ đối chiếu giữa Doanh thu lượt khám (Fact_Patient_Visits) với Chi phí thuốc thực tế (Fact_Pharmacy) trên cùng một bệnh nhân và cùng một khoảng thời gian.",
        title="VAI TRÒ CỦA CONFORMED DIMENSIONS TRONG KIẾN TRÚC KIMBALL (LECTURE 02 SLIDE 23)"
    )

    # ========================== 3.4. SƠ ĐỒ 1: KIẾN TRÚC 4 TẦNG ==========================
    add_h2("3.4. Sơ đồ 1 & Giải thích: Kiến trúc Tổng thể 4 Tầng (Four-Tier Architecture)")
    add_p("Kiến trúc hệ thống được phân tầng 4 lớp độc lập (Trích dẫn: Lecture 01 Slide 16 & Chương 3.2):")

    arch_box_text = (
        "┌────────────────────────────────────────────────────────────────────────────────────────┐\n"
        "│ TẦNG 1: NGUỒN DỮ LIỆU TÁC NGHIỆP (OPERATIONAL DATA SOURCES - OLTP)                     │\n"
        "│  [Hệ thống HIS]       [Bệnh án EMR]       [Xét nghiệm LIS]      [Viện phí Billing]     │\n"
        "│  (patients.csv)       (treatments.csv)    (Chỉ số Glucose,...)  (billing.csv)          │\n"
        "└───────────────────────────────────┬────────────────────────────────────────────────────┘\n"
        "                                    │ (Extract & Normalization: Script Python 01)\n"
        "                                    ▼\n"
        "┌────────────────────────────────────────────────────────────────────────────────────────┐\n"
        "│ TẦNG 2: VÙNG ĐỆM TRUNG GIAN (STAGING AREA - TRANSIENT / ISOLATED DB)                   │\n"
        "│  • Bảng đệm Staging_Doctors: Lưu trữ tạm thời danh sách nhân sự mới để so sánh SCD     │\n"
        "│  • Bảng đệm Staging_Transactions: Nơi làm sạch, khử trùng lặp và băm mật mã SHA-256    │\n"
        "└───────────────────────────────────┬────────────────────────────────────────────────────┘\n"
        "                                    │ (Transform & Load: Script Python 02 & 03)\n"
        "                                    ▼\n"
        "┌────────────────────────────────────────────────────────────────────────────────────────┐\n"
        "│ TẦNG 3: TRÁI TIM KHO DỮ LIỆU (ENTERPRISE DATA WAREHOUSE - STAR SCHEMA)                 │\n"
        "│  [Fact_Patient_Visits] ── Khóa ngoại Surrogate Keys ──► [6 Bảng Dim Chiều Dữ Liệu]     │\n"
        "│  (5.200 ca khám, độ đo viện phí, thời gian chờ, LoS)   (Doctor, Patient, Facility...)  │\n"
        "└───────────────────────────────────┬────────────────────────────────────────────────────┘\n"
        "                                    │ (DirectQuery / VertiPaq Semantic Layer)\n"
        "                                    ▼\n"
        "┌────────────────────────────────────────────────────────────────────────────────────────┐\n"
        "│ TẦNG 4: KHAI THÁC & TRỰC QUAN HÓA (PRESENTATION & BUSINESS INTELLIGENCE)               │\n"
        "│  • Power BI Dashboards: Wait-Time Heatmap, Clinical Ops & Bed Occupancy, Finance       │\n"
        "│  • SSAS Multidimensional Cube & Truy vấn MDX phân tích lát cắt đa chiều               │\n"
        "└────────────────────────────────────────────────────────────────────────────────────────┘"
    )
    add_code_block(arch_box_text, lang_title="MÔ HÌNH KIẾN TRÚC 4 TẦNG (FOUR-TIER CDW ARCHITECTURE)")

    add_p("Giải thích cơ chế vận hành của 4 tầng:")
    add_p("Nơi phát sinh giao dịch thường nhật. Mọi ca tiếp nhận, chỉ định xét nghiệm và hóa đơn được ghi nhận với độ trễ thấp.", bold_prefix="• Tầng 1 (Source Data): ")
    add_p("Vùng đệm trung gian đóng vai trò tối thượng: dữ liệu từ MySQL và Excel nhân sự được đổ tạm thời vào đây để xử lý khử trùng lặp và làm sạch mà không tiêu tốn tài nguyên của CSDL vận hành.", bold_prefix="• Tầng 2 (Staging Area - Lecture 05 Slide 6): ")
    add_p("Trái tim lưu trữ của hệ thống theo lược đồ hình sao, sử dụng các khóa thay thế số nguyên để tối ưu hóa việc join và tổng hợp.", bold_prefix="• Tầng 3 (Data Warehouse Core): ")
    add_p("Cung cấp các khung nhìn ngữ nghĩa (Semantic Views), mô hình SSAS Cube và báo cáo động cho Ban Giám đốc và Trưởng khoa phòng.", bold_prefix="• Tầng 4 (Analytics / BI Layer): ")

    # ========================== 3.5. SƠ ĐỒ 2: STAR SCHEMA DIAGRAM ==========================
    add_h2("3.5. Sơ đồ 2 & Giải thích: Lược đồ Hình sao (Kimball Star Schema Diagram)")
    add_p("Mô hình dữ liệu Star Schema được thiết kế theo chuẩn Ralph Kimball (Trích dẫn: Lecture 02 Slide 14, Chương 3.3 & File star_schema.dbml):")

    # Insert Image
    img_path = r"d:\KHODL\temp_img\star_schema_diagram.png"
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(6)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(img_path, width=Inches(6.2))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(0)
        p_cap.paragraph_format.space_after = Pt(6)
        rcap = p_cap.add_run("Hình 1: Mô hình Lược đồ Hình sao (Star Schema) của Kho Dữ Liệu Lâm Sàng trên Power BI Model View")
        rcap.font.name = "Arial"
        rcap.font.size = Pt(9.0)
        rcap.font.italic = True
        rcap.font.color.rgb = SLATE

    add_p("Giải thích chi tiết các nguyên lý kỹ thuật trong Sơ đồ hình sao:")
    add_p("Toàn bộ khóa chính (PK) và khóa ngoại (FK) nối giữa Fact và các Dim đều sử dụng kiểu số nguyên tự tăng INT AUTO_INCREMENT (Patient_Key, Doctor_Key...). Khóa thay thế giúp cách ly Kho dữ liệu hoàn toàn khỏi những thay đổi mã khóa tự nhiên ở hệ thống tác nghiệp nguồn, đồng thời phép JOIN trên trường số nguyên INT có chỉ mục nhanh gấp hàng chục lần so với trường chuỗi ký tự VARCHAR.", bold_prefix="1. Khóa thay thế (Surrogate Keys - Lecture 05 Slide 18): ")
    add_p("Chứa 5.200 dòng dữ liệu đại diện cho 5.200 ca khám, lưu trữ các khóa ngoại và toàn bộ chỉ số định lượng về thời gian chờ, ngày nằm viện, viện phí.", bold_prefix="2. Bảng sự kiện trung tâm (Fact_Patient_Visits): ")
    add_p("Mỗi bản ghi trong bảng Dim có thể xuất hiện nhiều lần trong bảng Fact. Hướng lọc dữ liệu luôn đi từ bảng Dimension sang bảng Fact (các thuộc tính của Dim dùng để cắt lát, lọc và gom nhóm các chỉ số trong Fact).", bold_prefix="3. Quan hệ 1-nhiều (1...N) & Hướng lọc một chiều (Single Filter Direction): ")

    # ========================== 3.6. CÂY PHÂN CẤP THỨ BẬC (MỚI) ==========================
    add_h2("3.6. Sơ đồ Cây Phân cấp Thứ bậc Chiều (Dimension Hierarchy Trees - Trích dẫn: Lecture 02 Slide 18 & Lab 03/04)")
    add_p("Trong mô hình dữ liệu đa chiều, phân cấp thứ bậc (Hierarchies) là cấu trúc định hình các đường dẫn điều hướng phân tích. Khi người dùng muốn xem báo cáo ở mức độ vĩ mô (tổng viện) hoặc vi mô (từng ca bệnh), hệ thống sẽ di chuyển dọc theo các nhánh cây phân cấp này.")

    hierarchy_box = (
        "1. PHÂN CẤP LỊCH THỜI GIAN (Calendar Hierarchy - Dim_Date):\n"
        "   [Năm (Year)] ──► [Quý (Quarter)] ──► [Tháng (Month)] ──► [Ngày khám (Full Date)] ──► [Ca khám (Shift)]\n"
        "   (Ví dụ: 2026 ──► Quý 1 ──► Tháng 03 ──► 2026-03-15 ──► Ca Sáng 07:00-11:30)\n\n"
        "2. PHÂN CẤP CƠ CẤU TỔ CHỨC Y TẾ (Organization Hierarchy - Dim_Facility):\n"
        "   [Bệnh viện Đa khoa] ──► [Khối điều trị (Division)] ──► [Khoa chuyên môn (Department)] ──► [Phòng khám (Clinic Room)]\n"
        "   (Ví dụ: Cơ sở 1 ──► Khối Ngoại trú ──► Khoa Tim Mạch ──► Phòng Khám Tim Mạch 204)\n\n"
        "3. PHÂN CẤP BỆNH HỌC QUỐC TẾ (Clinical ICD-10 Hierarchy - Dim_Diagnosis):\n"
        "   [Chương bệnh (Chapter)] ──► [Khối bệnh (Block)] ──► [Mã ICD-10] ──► [Tên bệnh lâm sàng cụ thể]\n"
        "   (Ví dụ: Bệnh tuần hoàn (Ch.IX) ──► Bệnh Tăng huyết áp (I10-I15) ──► I10 ──► Tăng huyết áp vô căn)\n\n"
        "4. PHÂN CẤP NHÂN KHẨU HỌC BỆNH NHÂN (Demographic Hierarchy - Dim_Patient):\n"
        "   [Nhóm tuổi (Age Group)] ──► [Giới tính (Gender)] ──► [Mã băm bệnh nhân (Patient_Hash_ID)]\n"
        "   (Ví dụ: Nhóm Cao tuổi (>=60) ──► Nữ (Female) ──► SHA256: 4a8f9b...e21c)"
    )
    add_code_block(hierarchy_box, lang_title="SƠ ĐỒ CÂY PHÂN CẤP THỨ BẬC 4 CHIỀU DỮ LIỆU CỐT LÕI")

    add_p("Ứng dụng học thuật trong thao tác OLAP (Lecture 03 Slide 8):")
    add_p("Tổng hợp dữ liệu từ mức chi tiết thấp lên mức tổng quan cao hơn theo phân cấp (ví dụ: cuộn dữ liệu từ Lượt khám theo Ngày lên Doanh thu theo Quý và Năm).", bold_prefix="• Thao tác Roll-up (Cuộn lên): ")
    add_p("Đi sâu từ mức vĩ mô xuống chi tiết vi mô (ví dụ: từ Doanh thu Khối Ngoại trú khoan sâu xuống Khoa Tim mạch và phát hiện phòng khám 204 đang bị quá tải).", bold_prefix="• Thao tác Drill-down (Khoan sâu): ")

    # ========================== 3.7. ETL, SCD2 & CONTROL/DATA FLOW (CẬP NHẬT) ==========================
    add_h2("3.7. Bước 3: Pipeline ETL, Khử định danh SHA-256, Quản trị SCD Type 2 & Quy tắc Xử lý NULL")
    add_p("Trong script 02_etl_lab3_initial.py, mã định danh bệnh nhân được mã hóa qua hàm băm mật mã học một chiều SHA-256 có muối (Salted Hash): Anonymized_Patient_ID = SHA256(CONCAT(Raw_ID, '_', Secret_Key)). Toàn bộ họ tên, SĐT, địa chỉ chi tiết bị loại bỏ hoàn toàn khỏi bảng Dim_Patient, đáp ứng 100% tiêu chuẩn HIPAA và Thông tư 46/2018/TT-BYT.", bold_prefix="• Khử định danh bảo mật y tế (HIPAA Compliance): ")
    add_p("Dải thời gian chờ khám được phân bổ theo chuyên khoa (Khoa Ung bướu: 25-60 phút; Da liễu: 5-20 phút); số ngày nằm viện LOS phân hóa theo điều trị (Hóa trị/Nội trú: 1-21 ngày; Ngoại trú = 0 ngày).", bold_prefix="• Phân hóa lâm sàng thực tế: ")
    add_p("Trong script 03_etl_lab4_advanced.py, khi phát hiện Bác sĩ D001 đổi chuyên khoa từ Da liễu sang Thần kinh:\n  - Dòng dữ liệu cũ (Doctor_Key = 1): Cập nhật ngày kết thúc End_Date = CURRENT_DATE và đóng cờ hiệu lực Is_Current = 0.\n  - Dòng dữ liệu mới (Doctor_Key = 21): Chèn dòng mới với chuyên khoa Thần kinh, Effective_Date = CURRENT_DATE, End_Date = 9999-12-31 và cờ hiệu lực Is_Current = 1.\n  - Thêm mới bác sĩ tuyển dụng D999 vào danh mục.", bold_prefix="• Quản trị chiều thay đổi chậm SCD Type 2 (Lecture 02 Slide 26): ")

    etl_flow_box = (
        "┌────────────────────────────────────────────────────────────────────────────────────────┐\n"
        "│ A. LUỒNG ĐIỀU KHIỂN TỔNG THỂ (ETL CONTROL FLOW PIPELINE - SSIS / SCRIPT ORCHESTRATION) │\n"
        "│                                                                                        │\n"
        "│  [Bắt đầu Pipeline]                                                                    │\n"
        "│          │                                                                             │\n"
        "│          ▼                                                                             │\n"
        "│  [Task 1: Generate Dim_Date] ────────► Sinh tự động 1.462 ngày lịch, cờ lễ & cuối tuần  │\n"
        "│          │                                                                             │\n"
        "│          ▼                                                                             │\n"
        "│  [Task 2: Ingest Staging Area] ──────► Truncate & Nạp dữ liệu thô vào bảng đệm        │\n"
        "│          │                                                                             │\n"
        "│          ▼                                                                             │\n"
        "│  [Task 3: Dimension Pipelines] ──────► Nạp song song Dim_Doctor, Facility, Diagnosis   │\n"
        "│          │                                                                             │\n"
        "│          ▼                                                                             │\n"
        "│  [Task 4: Patient SCD Type 2] ───────► Khử định danh SHA-256 + Quản trị lịch sử thẻ BH │\n"
        "│          │                                                                             │\n"
        "│          ▼                                                                             │\n"
        "│  [Task 5: Fact Table Pipeline] ──────► Lookup Surrogate Keys + Nạp Fact_Patient_Visits │\n"
        "│          │                                                                             │\n"
        "│          ▼                                                                             │\n"
        "│  [Hoàn tất Pipeline ETL]                                                               │\n"
        "└────────────────────────────────────────────────────────────────────────────────────────┘\n\n"
        "┌────────────────────────────────────────────────────────────────────────────────────────┐\n"
        "│ B. LUỒNG DỮ LIỆU BIẾN ĐỔI BÊN TRONG FACT TABLE (DATA FLOW TRANSFORMATIONS)              │\n"
        "│                                                                                        │\n"
        "│  [Staging Source] ──► [Derived Column: Làm sạch & Ép kiểu]                             │\n"
        "│                              │                                                         │\n"
        "│                              ▼                                                         │\n"
        "│                       [Lookup Patient_Key (Điều kiện: Is_Current = 1)]                 │\n"
        "│                              │                                                         │\n"
        "│                              ▼                                                         │\n"
        "│                       [Lookup Doctor_Key & Facility_Key]                               │\n"
        "│                              │                                                         │\n"
        "│                              ▼                                                         │\n"
        "│                       [Lookup Diagnosis_Key (ICD-10) & Service_Key]                    │\n"
        "│                              │                                                         │\n"
        "│                              ▼                                                         │\n"
        "│                       [Conditional Split: Kiểm tra ràng buộc hợp lệ]                   │\n"
        "│                        ├── Hợp lệ ──────► [OLE DB Destination: Fact_Patient_Visits]    │\n"
        "│                        └── Thiếu mã ────► [Ánh xạ Surrogate Key Mặc định -1 (Unknown)] │\n"
        "└────────────────────────────────────────────────────────────────────────────────────────┘"
    )
    add_code_block(etl_flow_box, lang_title="SƠ ĐỒ PHÂN ĐỊNH CONTROL FLOW & DATA FLOW PIPELINE (LECTURE 05 & LAB 01/02)")

    add_callout(
        "Theo nguyên lý Ralph Kimball, tuyệt đối KHÔNG ĐƯỢC LƯU GIÁ TRỊ NULL trong các cột khóa ngoại của bảng Fact. Nếu một ca cấp cứu chưa kịp phân bác sĩ khám hoặc chưa có mã chẩn đoán, việc lưu NULL sẽ làm gãy các phép JOIN và gây sai lệch kết quả tổng hợp. Giải pháp học thuật: Hệ thống tạo sẵn một bản ghi mặc định với Surrogate Key = -1 (hoặc 0) trong mỗi bảng Dimension mang giá trị 'Unknown' (Chưa xác định) hoặc 'N/A' (Không áp dụng) để ánh xạ vào Fact, đảm bảo tính toàn vẹn tham chiếu 100%.",
        title="QUY TẮC KIMBALL XỬ LÝ GIÁ TRỊ NULL / KHUYẾT THIẾU TRONG KHO DỮ LIỆU"
    )

    # ========================== 3.8. THIẾT KẾ VẬT LÝ & TỐI ƯU HÓA (MỚI) ==========================
    add_h2("3.8. Thiết kế Vật lý Cơ sở Dữ liệu & Chiến lược Tối ưu hóa Lưu trữ (Trích dẫn: Lecture 04 Slide 10-22)")
    add_p("Để đáp ứng yêu cầu xử lý hàng triệu bản ghi y tế mà không làm suy giảm thời gian đáp ứng, đồ án áp dụng hai chiến lược thiết kế vật lý tối ưu:")
    
    add_p("Bảng Fact_Patient_Visits áp dụng kỹ thuật Range Partitioning theo cột date_key (phân vùng theo từng Năm hoặc từng Quý). Khi người dùng thực hiện truy vấn phân tích dữ liệu năm 2026, cơ chế Partition Pruning (Tỉa phân vùng) của hệ quản trị CSDL sẽ tự động bỏ qua toàn bộ dữ liệu các năm 2024, 2025 và 2027, giúp giảm số lượng khối đĩa I/O phải quét tới 75%.", bold_prefix="1. Phân vùng bảng (Table Partitioning & Partition Pruning): ")
    add_p("Hệ thống kết hợp linh hoạt 2 loại chỉ mục:\n   • B-Tree Index: Đánh chỉ mục trên các cột khóa có độ biến thiên cao (High Cardinality) như visit_key (PK), patient_key, doctor_key để phục vụ kết nối JOIN tức thời.\n   • Bitmap Index / Columnstore (VertiPaq Engine): Áp dụng cho các thuộc tính danh mục có ít giá trị khác nhau (Low Cardinality) như Giới tính (Gender: Nam/Nữ), Phân hạng BHYT (Insurance_Tier: 4 hạng), Cờ cấp cứu (Is_Emergency: 0/1) và Chuyên khoa (Specialty: 20 khoa). Cơ chế này nén dữ liệu cực đại và tính toán biểu thức logic Boolean hàng triệu dòng trong tích tắc.", bold_prefix="2. Chiến lược Chỉ mục Kép (B-Tree Index vs. Bitmap Index): ")

    # ========================== 3.9. BENCHMARK & MDX (CẬP NHẬT) ==========================
    add_h2("3.9. Bước 4: Benchmark Đo lường Hiệu năng & Truy vấn Đa chiều OLAP bằng MDX (Trích dẫn: Lecture 03, 04 & Lab 03/04)")
    add_p("Cơ sở lý thuyết: Mở rộng SQL cho OLAP (Lecture 03 Slide 15), Khối lập phương SSAS Multidimensional Cube (Lab 03, 04) và Tối ưu hóa chỉ mục (Lecture 04 Slide 8).", bold_prefix="• Cơ sở lý thuyết: ")
    add_p("Đồ án thực hiện cả hai phương thức truy vấn phân tích nâng cao:")
    add_p("Sử dụng toán tử GROUP BY ... WITH ROLLUP để tự động tính tổng lũy kế đa cấp và hàm xếp hạng RANK() OVER (PARTITION BY Year, Quarter ORDER BY Total_Cost DESC) để xếp hạng đóng góp tài chính các khoa phòng.", bold_prefix="1. SQL Mở rộng trên CSDL Quan hệ: ")
    add_p("Xây dựng khối lập phương phân tích trực tuyến đa chiều (OLAP Cube: Hospital_Clinical_Cube) với 8 Measures (Total Visits, Total Revenue, Insurance Covered, Patient Copay, Avg Waiting Time, Avg LoS, Avg Glucose, Avg Creatinine) và thực thi các câu lệnh truy vấn chuẩn MDX.", bold_prefix="2. Khối Đa chiều SSAS Cube & Ngôn ngữ Truy vấn MDX: ")

    mdx_code = (
        "-- Truy vấn MDX 1: Phân tích Doanh thu và Lượt khám theo Quý và Khoa phòng\n"
        "SELECT \n"
        "    {[Measures].[Total Visits], [Measures].[Total Revenue]} ON COLUMNS,\n"
        "    NON EMPTY CROSSJOIN(\n"
        "        [Dim Date].[Calendar].[Quarter].Members, \n"
        "        [Dim Facility].[Facility Name].Members\n"
        "    ) ON ROWS\n"
        "FROM [Hospital_Clinical_Cube];\n\n"
        "-- Truy vấn MDX 2: Cắt lát thời gian chờ khám bệnh nhân ngoại trú theo Thứ trong tuần\n"
        "SELECT \n"
        "    {[Measures].[Total Visits], [Measures].[Avg Waiting Time]} ON COLUMNS,\n"
        "    [Dim Date].[Day Of Week].Members ON ROWS\n"
        "FROM [Hospital_Clinical_Cube]\n"
        "WHERE ([Dim Facility].[Facility Type].[Khoa Khám Bệnh]);\n\n"
        "-- Truy vấn MDX 3: Phân tích độ dài nằm viện LoS theo nhóm bệnh lý mãn tính\n"
        "SELECT \n"
        "    {[Measures].[Total Visits], [Measures].[Avg LoS], [Measures].[Avg Creatinine]} ON COLUMNS,\n"
        "    [Dim Diagnosis].[Disease Category].Members ON ROWS\n"
        "FROM [Hospital_Clinical_Cube]\n"
        "WHERE ([Dim Diagnosis].[Is Chronic].[1]);"
    )
    add_code_block(mdx_code, lang_title="TRUY VẤN PHÂN TÍCH ĐA CHIỀU BẰNG NGÔN NGỮ MDX (SSAS CUBE - LAB 03 & LAB 04)")

    # ========================== 3.10. BÁO CÁO BI & DAX ==========================
    add_h2("3.10. Bước 5: Báo cáo Trực quan hóa BI & 18 DAX Measures (Trích dẫn: Lab 05, 06 & Chương 5.4)")
    add_p("Ứng dụng ngôn ngữ DAX trong Power BI Desktop (Lab 06) với các hàm chia an toàn DIVIDE chống lỗi chia 0 và hàm lặp theo ngữ cảnh (Iterator Functions) AVERAGEX kết hợp VALUES().", bold_prefix="• Cơ sở lý thuyết: ")
    add_p("• Bộ 18 công thức DAX Measures tiêu biểu (dax_measures.dax):\n  - Tổng doanh thu: Total Revenue = SUM('Fact_Patient_Visits'[Total_Cost])\n  - Thời gian chờ trung bình: Avg Waiting Time = AVERAGE('Fact_Patient_Visits'[Waiting_Time_Minutes])\n  - Công suất giường bệnh nội trú: Bed Occupancy Rate % = DIVIDE(SUM(Fact_Patient_Visits[Length_Of_Stay_Days]), 50 * DISTINCTCOUNT(Dim_Date[Full_Date]), 0)\n  - Doanh thu trung bình/Bệnh nhân: Avg Revenue Per Patient = AVERAGEX(VALUES('Fact_Patient_Visits'[Patient_Key]), [Total Revenue])")
    add_p("• 3 Trang Dashboard điều hành y tế:\n  1. Dashboard 1 (Wait-Time Heatmap): Bản đồ nhiệt thời gian chờ theo ca trực và ngày trong tuần, phát hiện điểm nghẽn sáng Thứ 2.\n  2. Dashboard 2 (Clinical Ops & Bed Occupancy): Phân rã độ dài nằm viện LoS theo 12 nhóm bệnh ICD-10 và thước đo đồng hồ Gauge công suất giường bệnh.\n  3. Dashboard 3 (Financial Analytics): Cơ cấu nguồn thu BHYT chi trả (78.5%) vs Viện phí tự chi trả (21.5%) phân bổ theo 4 nhóm dịch vụ y tế.")

    # ========================== PHẦN 4: EVALUATION & BENCHMARK ==========================
    add_h1("PHẦN 4: EVALUATION & BENCHMARKING (SO SÁNH CÁC MÔ HÌNH)")
    
    add_h2("4.1. So sánh Star Schema với các Mô hình Kiến trúc Khác (Trích dẫn: Lecture 01, 02 & Chương 2.1, 4.1)")
    add_p("Bảng so sánh đối sánh toàn diện giữa mô hình Kimball Star Schema được triển khai trong đồ án với các mô hình CSDL và Kho dữ liệu kinh điển:")

    eval_data = [
        ("Tiêu chí so sánh", "Mô hình OLTP 3NF (Codd)", "Mô hình Snowflake (Bông tuyết)", "Mô hình Data Vault 2.0", "Kimball Star Schema (Đồ án)"),
        ("Mục đích thiết kế", "Phục vụ ghi chép giao dịch tác nghiệp hàng ngày (OLTP).", "Chuẩn hóa thứ cấp Dimension nhằm tiết kiệm dung lượng lưu trữ.", "Lưu trữ dữ liệu nguồn thô (Raw Audit) cho tập đoàn quy mô cực lớn.", "Tối ưu hóa tuyệt đối cho truy vấn phân tích đọc (OLAP) và báo cáo BI."),
        ("Độ phức tạp phép JOIN", "Rất cao (Phải JOIN từ 6 đến 15 bảng để lấy báo cáo tổng hợp).", "Trung bình - Cao (Phải JOIN thêm các bảng phân cấp phụ).", "Cực kỳ cao (Cần JOIN liên tục qua Hubs, Links và Satellites).", "Tối thiểu (Chỉ đúng 1 tầng JOIN từ Fact trung tâm ra các Dim)."),
        ("Tốc độ truy vấn báo cáo", "Chậm, dễ gây nghẽn và khóa tài nguyên CSDL vận hành.", "Trung bình (Bị suy giảm do độ sâu của các tầng khóa ngoại).", "Chậm khi truy vấn trực tiếp (Bắt buộc phải tạo Information Marts).", "Cực nhanh (Tối ưu hóa chỉ mục B-tree và bộ nhớ đệm VertiPaq)."),
        ("Mức độ dư thừa dữ liệu", "Không dư thừa (Zero Redundancy - Đạt dạng chuẩn 3NF).", "Rất ít (Các chiều thứ cấp được chuẩn hóa triệt để).", "Cao (Lưu trữ toàn bộ lịch sử biến động nguồn theo thời gian).", "Có dư thừa có kiểm soát (Phi chuẩn hóa Denormalization để đổi lấy tốc độ)."),
        ("Mức độ thân thiện BI", "Kém (Cấu trúc bảng chằng chịt, người làm BI rất khó hiểu).", "Trung bình (Cần hiểu rõ cấu trúc phân cấp đa tầng).", "Rất kém đối với người dùng cuối kinh doanh.", "Hoàn hảo (Trực quan, dễ hiểu đối với lãnh đạo và chuyên viên phân tích).")
    ]

    t_eval = doc.add_table(rows=len(eval_data), cols=5)
    t_eval.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_eval)
    for r_idx, row in enumerate(eval_data):
        for c_idx, val in enumerate(row):
            cell = t_eval.cell(r_idx, c_idx)
            set_cell_margins(cell, top=70, bottom=70, left=80, right=80)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            run = p.add_run(val)
            run.font.name = "Arial"
            if r_idx == 0:
                set_cell_background(cell, "0F172A")
                run.font.size = Pt(8.5)
                run.font.bold = True
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            else:
                if r_idx % 2 == 1:
                    set_cell_background(cell, "F8FAFC")
                run.font.size = Pt(8.0)
                run.font.color.rgb = DARK_TEXT
                if c_idx == 0:
                    run.font.bold = True
                if c_idx == 4:
                    run.font.bold = True

    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(4)

    add_h2("4.2. Kết quả Đo chuẩn Thực nghiệm Định lượng bằng EXPLAIN ANALYZE (Trích dẫn: Chương 5.3)")
    add_p("Thực nghiệm so chuẩn (Benchmarking) được đo lường khách quan trên cùng máy chủ MySQL 8.0:")

    bench_data = [
        ("Kịch bản truy vấn nghiệp vụ", "Thời gian OLTP 3NF (ms)", "Thời gian Star Schema (ms)", "% Tốc độ cải thiện", "Cơ chế tối ưu của Star Schema"),
        ("Q1: Doanh thu & Thời gian chờ theo Chuyên khoa", "1.428,5 ms", "412,3 ms", "↓ 71,1%", "3NF JOIN 4 bảng qua khóa chuỗi; Star Schema JOIN 2 bảng qua Surrogate Key INT có Index."),
        ("Q2: Độ dài nằm viện LoS & Chỉ số xét nghiệm theo Bệnh", "1.890,2 ms", "645,8 ms", "↓ 65,8%", "Tận dụng Partition Pruning và lọc trực tiếp trên chiều Dim_Diagnosis phẳng."),
        ("Q3: Phân tích Doanh thu theo BHYT & Dịch vụ", "1.215,0 ms", "380,4 ms", "↓ 68,7%", "Star Schema đọc trực tiếp các độ đo đã tính sẵn trong Fact mà không cần tính lại."),
        ("TRUNG BÌNH TOÀN HỆ THỐNG", "1.511,2 ms", "479,5 ms", "↓ 68,1% (Nhanh gấp 3,15 lần)", "Giảm số khối I/O đĩa từ 48.200 blocks xuống còn 14.150 blocks (tiết kiệm 70,6% I/O).")
    ]

    t_bench = doc.add_table(rows=len(bench_data), cols=5)
    t_bench.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_bench)
    for r_idx, row in enumerate(bench_data):
        for c_idx, val in enumerate(row):
            cell = t_bench.cell(r_idx, c_idx)
            set_cell_margins(cell, top=70, bottom=70, left=80, right=80)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            run = p.add_run(val)
            run.font.name = "Arial"
            if r_idx == 0:
                set_cell_background(cell, "0F172A")
                run.font.size = Pt(8.5)
                run.font.bold = True
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            else:
                if r_idx == len(bench_data) - 1:
                    set_cell_background(cell, "E0F2FE")
                    run.font.bold = True
                elif r_idx % 2 == 1:
                    set_cell_background(cell, "F8FAFC")
                run.font.size = Pt(8.0)
                run.font.color.rgb = DARK_TEXT
                if c_idx == 0:
                    run.font.bold = True
                if c_idx == 3:
                    run.font.bold = True
                    run.font.color.rgb = SKY_BLUE

    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(6)

    # ========================== PHẦN 5: KẾT LUẬN & HƯỚNG PHÁT TRIỂN ==========================
    add_h1("PHẦN 5: KẾT LUẬN & HƯỚNG PHÁT TRIỂN")

    add_h2("5.1. Kết luận đạt được đối chiếu mục tiêu nghiên cứu (Trích dẫn: Chương 6.1 & 6.3)")
    add_p("Tách rời CSDL tiếp đón tác nghiệp (hospital_oltp) khỏi môi trường phân tích (hospital_dw), triệt tiêu hoàn toàn nguy cơ nghẽn mạng và khóa bảng trong bệnh viện.", bold_prefix="1. Giải phóng hoàn toàn tải phân tích khỏi hệ thống vận hành: ")
    add_p("Thiết kế chuẩn mực mô hình hình sao 1 Fact – 6 Dimensions với khóa thay thế Surrogate Keys số nguyên và khử định danh SHA-256 tuân thủ nghiêm ngặt tiêu chuẩn HIPAA và Thông tư 46/2018/TT-BYT.", bold_prefix="2. Hiện thực hóa trọn vẹn quy chuẩn Ralph Kimball: ")
    add_p("Áp dụng thành công kỹ thuật SCD Type 2, bảo đảm tính toàn vẹn 100% của lịch sử điều trị và doanh thu khi y bác sĩ luân chuyển chuyên khoa hoặc chi nhánh.", bold_prefix="3. Giải quyết triệt để bài toán biến động nhân sự y tế: ")
    add_p("Thực nghiệm đo lường thực tế chứng minh mô hình Star Schema giúp thời gian thực thi truy vấn nhanh hơn 68,1% và giảm đọc đĩa I/O 70,6% so với hệ thống 3NF truyền thống.", bold_prefix="4. Chứng minh hiệu năng định lượng rõ ràng: ")
    add_p("Hệ thống 3 trang Dashboard trên Power BI với 18 công thức DAX đã bóc tách rõ các điểm nghẽn thực tế: khoa có thời gian chờ cao nhất, công suất giường bệnh nội trú và cơ cấu dòng tiền thanh toán viện phí.", bold_prefix="5. Cung cấp công cụ ra quyết định trực quan: ")

    add_h2("5.2. Hướng phát triển trong tương lai (Trích dẫn: Lecture 01 Slide 24 & Chương 6.4)")
    add_p("Tích hợp các định dạng mở như Apache Iceberg hoặc Delta Lake để quản lý đồng thời cả dữ liệu số có cấu trúc và dữ liệu hình ảnh y khoa phi cấu trúc (ảnh chụp X-quang, CT, MRI chuẩn DICOM từ hệ thống PACS).", bold_prefix="• Nâng cấp lên kiến trúc Healthcare Data Lakehouse: ")
    add_p("Ứng dụng công nghệ Change Data Capture (Debezium CDC) kết hợp Apache Kafka để bắt các sự kiện tiếp nhận bệnh nhân theo thời gian thực (độ trễ dưới 1 giây), phục vụ cảnh báo sớm tình trạng quá tải buồng cấp cứu và sốc nhiễm khuẩn.", bold_prefix="• Tích hợp luồng dữ liệu thời gian thực (Real-time Streaming ETL): ")
    add_p("Xây dựng mô hình chuỗi thời gian (Time-series Forecasting bằng Prophet/LSTM) để dự báo số ca cấp cứu trong 48 giờ tiếp theo và mô hình học máy phân loại dự đoán nguy cơ bệnh nhân tái nhập viện trong 30 ngày (30-day Readmission Risk).", bold_prefix="• Tích hợp Trí tuệ Nhân tạo & Học máy Dự báo (In-Database AI / Predictive Analytics): ")
    add_p("Ánh xạ dữ liệu kho sang mô hình dữ liệu chuẩn OMOP CDM (OHDSI) và HL7 FHIR để sẵn sàng kết nối vào mạng lưới nghiên cứu lâm sàng đa trung tâm trên toàn cầu.", bold_prefix="• Chuẩn hóa liên thông dữ liệu quốc tế: ")

    # ========================== PHẦN 6: TÀI LIỆU THAM KHẢO ==========================
    add_h1("PHẦN 6: DANH MỤC TÀI LIỆU THAM KHẢO & SLIDE VKU ĐÃ TRÍCH DẪN")
    
    add_p("• lecture01-intro.pdf: Khái niệm DW theo Inmon, 4 đặc tính, kiến trúc 3 tầng, so sánh OLTP vs OLAP, trường phái Kimball vs Inmon.\n• lecture02-modelling.pdf: Quy trình 4 bước thiết kế Dimensional Modeling của Kimball, phân loại Fact/Measures, ma trận Bus Matrix, phân cấp Hierarchies, kỹ thuật SCD Types 0-6.\n• lecture03-queries.pdf: Thao tác OLAP (Roll-up, Drill-down, Slice, Dice, Pivot), mở rộng SQL (WITH ROLLUP, Window Functions), ngôn ngữ MDX.\n• lecture04-indexing-and-optimization.pdf: Kỹ thuật chỉ mục B-Tree vs Bitmap Index, phân vùng Partitioning, tối ưu hóa truy vấn trong Kho dữ liệu.\n• lecture05-etl.pdf: Kiến trúc Staging Area, cơ chế CDC (Change Data Capture), quy trình ETL SSIS, sinh khóa Surrogate Keys và xử lý NULL.", bold_prefix="1. Bộ bài giảng lý thuyết Kho Dữ Liệu – Trường Đại học CNTT & Truyền thông Việt - Hàn (VKU):\n")
    add_p("• lab01.pdf & lab02.pdf: Kỹ thuật trích xuất dữ liệu, cấu hình Staging và xử lý SCD Type 2 trên SSIS.\n• lab03.pdf & lab04.pdf: Xây dựng khối lập phương đa chiều SSAS Cube và viết truy vấn phân tích MDX.\n• lab05.pdf & lab06.pdf: Kỹ thuật trực quan hóa Power BI Desktop và xây dựng công thức đo lường DAX nâng cao (AVERAGEX, VALUES, DIVIDE).", bold_prefix="2. Bộ bài thực hành học phần Kho Dữ Liệu – VKU:\n")
    add_p("• Kimball, R., & Ross, M. (2013). The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling (3rd Edition). John Wiley & Sons.\n• Inmon, W. H. (2005). Building the Data Warehouse (4th Edition). John Wiley & Sons.\n• IEEE Access. (2021). Performance Evaluation of Star Schema and Snowflake Schema in Multi-Dimensional Data Warehouses for Analytical Processing.\n• Bộ Y tế Việt Nam. (2018). Thông tư 46/2018/TT-BYT Quy định về Hồ sơ Bệnh án Điện tử, ban hành ngày 28/12/2018.", bold_prefix="3. Giáo trình & Tài liệu khoa học quốc tế:\n")

    output_path = r"d:\KHODL\BAO_CAO_TONG_QUAN_KHO_DU_LIEU_BENH_VIEN.docx"
    doc.save(output_path)
    print(f"Successfully generated updated report at: {output_path}")

if __name__ == "__main__":
    create_document()
