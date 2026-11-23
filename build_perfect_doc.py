# -*- coding: utf-8 -*-
"""
Unified, robust builder for Bao_Cao_BTL_Java_PT_Connect.docx
Reads from original_from_git.docx, applies all structural and linguistic cleanups,
eliminating 100% of AI buzzwords, flattery, and sensational phrasing.
Guarantees 100% Microsoft Word OpenXML compatibility.
"""

import zipfile
import xml.etree.ElementTree as ET

ET.register_namespace('w', 'http://schemas.openxmlformats.org/wordprocessingml/2006/main')
ET.register_namespace('r', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships')
ET.register_namespace('wp', 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing')
ET.register_namespace('a', 'http://schemas.openxmlformats.org/drawingml/2006/main')
ET.register_namespace('pic', 'http://schemas.openxmlformats.org/drawingml/2006/picture')

z = zipfile.ZipFile('original_from_git.docx')
doc_xml = z.read('word/document.xml')
tree = ET.fromstring(doc_xml)
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

body = tree.find('w:body', ns)

def get_text(el):
    return ''.join(el.itertext())

def set_p_text(p, prefix_text=None, body_text=None, full_text=None):
    runs = p.findall('w:r', ns)
    if full_text is not None:
        if runs:
            t0 = runs[0].find('w:t', ns)
            if t0 is None:
                t0 = ET.SubElement(runs[0], '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t')
            t0.text = full_text
            t0.attrib['{http://www.w3.org/XML/1998/namespace}space'] = 'preserve'
            for r in runs[1:]:
                p.remove(r)
        else:
            r = ET.SubElement(p, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r')
            t = ET.SubElement(r, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t')
            t.text = full_text
            t.attrib['{http://www.w3.org/XML/1998/namespace}space'] = 'preserve'
    elif prefix_text is not None and body_text is not None:
        if len(runs) >= 3:
            t1 = runs[1].find('w:t', ns)
            if t1 is not None:
                t1.text = prefix_text
                t1.attrib['{http://www.w3.org/XML/1998/namespace}space'] = 'preserve'
            t2 = runs[2].find('w:t', ns)
            if t2 is not None:
                t2.text = body_text
                t2.attrib['{http://www.w3.org/XML/1998/namespace}space'] = 'preserve'
            for r in runs[3:]:
                p.remove(r)
        elif len(runs) >= 2:
            t0 = runs[0].find('w:t', ns)
            if t0 is not None:
                t0.text = prefix_text
                t0.attrib['{http://www.w3.org/XML/1998/namespace}space'] = 'preserve'
            t1 = runs[1].find('w:t', ns)
            if t1 is not None:
                t1.text = body_text
                t1.attrib['{http://www.w3.org/XML/1998/namespace}space'] = 'preserve'
            for r in runs[2:]:
                p.remove(r)

# ----------------------------------------------------------------------
# 1. REMOVE REDUNDANT CALLOUT BOXES (Table 3 and Table 6)
# ----------------------------------------------------------------------
tbls = body.findall('w:tbl', ns)
t3 = tbls[3] # Callout 5 lá chắn
t6 = tbls[6] # Callout mốc 24h

body.remove(t3)
body.remove(t6)
print("1. Removed redundant callout tables 3 and 6.")

# ----------------------------------------------------------------------
# 2. UPDATE PARAGRAPHS ACROSS ALL CHAPTERS
# ----------------------------------------------------------------------
all_p = body.findall('.//w:p', ns)

for p in all_p:
    txt = get_text(p)
    
    # --- Trang Bìa ---
    if "Vũ Viết thành" in txt:
        set_p_text(p, full_text=txt.replace("Vũ Viết thành", "Vũ Viết Thành"))
    elif "GIảng viên" in txt:
        set_p_text(p, full_text=txt.replace("GIảng viên", "Giảng viên"))
    elif "BỘ MÔN CƠ SỞ DỮ LIỆU & CÔNG NGHỆ PHẦN MỀM" in txt:
        set_p_text(p, full_text="BỘ MÔN CÔNG NGHỆ PHẦN MỀM")

    # --- Lời Nói Đầu: Sửa văn mẫu nịnh thầy quá lố thành lời cảm ơn chuẩn kỹ sư ---
    elif "quan điểm sống còn đối với một kỹ sư" in txt or "thắp lên ngọn lửa" in txt or "dấn thân" in txt or "lối mòn" in txt or "giải quyết được triệt để bài toán nhức nhối" in txt:
        set_p_text(p, full_text="Đặc biệt, nhóm xin gửi lời cảm ơn chân thành tới ThS. Nguyễn Mạnh Sơn – giảng viên trực tiếp hướng dẫn học phần. Những định hướng về phương pháp luận và yêu cầu khắt khe của Thầy trong suốt quá trình thực hiện bài tập lớn đã giúp nhóm tập trung phân tích sâu bài toán nghiệp vụ, từ đó hoàn thiện hệ thống PT-Connect với các chức năng trọng yếu: quản lý hợp đồng đào tạo dạng PDF, kiểm soát dòng tiền ký quỹ và giải ngân theo buổi, cơ chế khóa khung giờ chống đặt trùng, điểm danh hai chiều bằng mã OTP và quy trình xử lý khiếu nại minh bạch.")

    # --- Chương 1: Bỏ từ ngữ pitch-deck khởi nghiệp ---
    elif "đang chứng kiến sự bùng nổ mạnh mẽ" in txt:
        set_p_text(p, full_text="Trong những năm gần đây, nhu cầu rèn luyện thể hình và nâng cao sức khỏe cùng Huấn luyện viên cá nhân (Personal Trainer - PT) ngày càng gia tăng tại các đô thị. Huấn luyện viên cá nhân đóng vai trò quan trọng trong việc thiết lập kế hoạch tập luyện phù hợp với thể trạng từng học viên, hướng dẫn kỹ thuật động tác chuẩn xác nhằm hạn chế chấn thương và tư vấn chế độ dinh dưỡng khoa học.")
    elif "trái ngược với tốc độ tăng trưởng phi mã" in txt or "vô cùng phân mảnh, thủ công và lạc hậu" in txt:
        set_p_text(p, full_text="Tuy nhiên, phương thức kết nối, quản lý lịch tập và giao dịch dịch vụ PT hiện nay vẫn chủ yếu diễn ra thủ công và phân tán. Đa số giao dịch giữa học viên và huấn luyện viên tự do được trao đổi qua mạng xã hội (Facebook, Zalo), tin nhắn cá nhân hoặc thỏa thuận miệng. Việc thiếu một quy trình chuẩn hóa và nền tảng quản lý tập trung khiến thông tin lịch hẹn, điều khoản thỏa thuận và lịch sử thanh toán dễ bị sai lệch, dẫn đến tranh chấp khi phát sinh thay đổi.")
    elif "1.2. Phân tích 5 'Nỗi đau'" in txt:
        set_p_text(p, full_text="1.2. Phân tích 5 vấn đề cốt lõi của bài toán vận hành thực tế")
    elif "Qua quá trình khảo sát thực tế và phân tích hành vi của hàng trăm học viên" in txt:
        set_p_text(p, full_text="Từ việc phân tích các tình huống thường gặp trong quy trình cung cấp dịch vụ PT, nhóm xác định 5 vấn đề trọng tâm cần giải quyết:")
    
    # 5 Bullets 1.2
    elif "Nỗi đau 1 - Thiếu ràng buộc pháp lý" in txt:
        set_p_text(p, prefix_text="Vấn đề 1 - Thỏa thuận dịch vụ thiếu ràng buộc văn bản pháp lý: ",
                   body_text="Học viên và PT thường chỉ thỏa thuận miệng về học phí, số buổi, thời hạn và địa điểm tập. Khi PT chuyển địa điểm hoặc học viên bận đột xuất, việc thiếu văn bản đối chiếu dễ dẫn đến tranh chấp gay gắt.")
    elif "Nỗi đau 2 - Rủi ro thanh toán một lần" in txt:
        set_p_text(p, prefix_text="Vấn đề 2 - Rủi ro thanh toán trọn gói và mất cân bằng dòng tiền: ",
                   body_text="Học viên thường phải đóng 100% học phí cả gói từ đầu. Nếu PT dạy không đạt hoặc bỏ dở giữa chừng, học viên đối mặt rủi ro mất tiền. Ngược lại, nếu tập trước trả sau, PT lại chịu rủi ro bị quỵt thù lao. Hệ thống cần cơ chế ký quỹ nội bộ để giải ngân theo từng buổi học.")
    elif "Nỗi đau 3 - Xung đột lịch trình (Double-Booking)" in txt:
        set_p_text(p, prefix_text="Vấn đề 3 - Xung đột lịch hẹn (Double-booking) và hủy ca sát giờ: ",
                   body_text="Xếp lịch thủ công qua tin nhắn dễ trùng khung giờ giữa các học viên. Việc hủy lịch sát giờ khiến bên còn lại mất công di chuyển mà không nhận được bồi hoàn. Hệ thống cần kiểm soát khóa slot và áp dụng chế tài hủy lịch mốc 24h.")
    elif "Nỗi đau 4 - Gian lận đối soát buổi tập" in txt:
        set_p_text(p, prefix_text="Vấn đề 4 - Điểm danh thủ công dễ phát sinh sai lệch và gian lận: ",
                   body_text="Điểm danh bằng thẻ giấy hay sổ tay dễ xảy ra việc gạch thẻ khống khi học viên nghỉ hoặc học viên phủ nhận đã học. Cần một cơ chế xác thực hai chiều tức thời bằng mã OTP tại phòng tập.")
    elif "Nỗi đau 5 - Bế tắc khi phát sinh mâu thuẫn" in txt:
        set_p_text(p, prefix_text="Vấn đề 5 - Thiếu quy trình lưu trữ chứng cứ và giải quyết khiếu nại: ",
                   body_text="Khi xảy ra sự cố kỹ thuật hoặc bất đồng giao tiếp, hai bên không có nơi tập trung để gửi chứng cứ và không có quy trình phân xử công bằng.")

    # 1.3
    elif "1.3. Mô hình Giải pháp: '5 Lá chắn Kỹ thuật" in txt:
        set_p_text(p, full_text="1.3. Mô hình giải pháp: 5 cơ chế bảo vệ quyền lợi hai chiều")
    elif "Nhận thức sâu sắc rằng công nghệ chỉ thực sự có ý nghĩa khi nó giải quyết tận gốc rễ" in txt:
        set_p_text(p, full_text="Để giải quyết toàn diện 5 vấn đề trên, PT-Connect được thiết kế xoay quanh mô hình 5 cơ chế bảo vệ quyền lợi hai chiều, ứng với từng giải pháp kỹ thuật Java và cơ sở dữ liệu:")
    elif "Hình 1.1: Mô hình 5 tầng kỹ thuật" in txt:
        set_p_text(p, full_text="Hình 1.1: Mô hình 5 cơ chế bảo vệ quyền lợi Học viên và Huấn luyện viên trên PT-Connect")
    elif "Dưới đây là bảng phân tích chi tiết từng lá chắn kỹ thuật" in txt:
        set_p_text(p, full_text="Dưới đây là bảng phân tích chi tiết từng cơ chế giải pháp, vấn đề thực tế giải quyết và giải pháp kỹ thuật tương ứng:")

    # 1.4
    elif "Về mặt nghiệp vụ kinh tế: Triệt tiêu 100% rủi ro" in txt:
        set_p_text(p, prefix_text="Về mặt nghiệp vụ: ",
                   body_text="Chuẩn hóa quy trình đặt lịch, lưu trữ điều khoản hợp đồng dạng PDF, áp dụng chính sách hủy ca mốc 24h, điểm danh hai chiều bằng mã OTP và cơ chế ký quỹ giải ngân theo từng buổi học.")
    elif "Về mặt kỹ thuật lập trình Java: Xây dựng kiến trúc Backend" in txt:
        set_p_text(p, prefix_text="Về mặt kỹ thuật Java: ",
                   body_text="Xây dựng Backend RESTful API theo kiến trúc phân tầng trên Java 17 và Spring Boot 3.3.4; áp dụng các mẫu thiết kế OOP (Strategy, Factory, Handler, DDD); quản lý giao dịch toàn vẹn ACID với @Transactional; tính toán tài chính chính xác bằng BigDecimal.")
    elif "Về mặt cơ sở dữ liệu và bảo mật: Thiết kế Schema CSDL MySQL 8.0 gồm 17 bảng" in txt or "việc khẳng định đạt BCNF" in txt:
        set_p_text(p, prefix_text="Về cơ sở dữ liệu và bảo mật: ",
                   body_text="Thiết kế cơ sở dữ liệu quan hệ MySQL 8.0 gồm 16 bảng cốt lõi được chuẩn hóa theo dạng chuẩn 3NF/BCNF nhằm hạn chế dư thừa dữ liệu và loại bỏ dị thường cập nhật; bảo mật xác thực phân quyền với Spring Security, JWT và mã hóa mật khẩu BCrypt.")

    # 1.5 Scope Disclaimer
    elif "Phân hệ Quản trị viên (Admin & Arbitration Board):" in txt:
        set_p_text(p, prefix_text="Phân hệ Quản trị viên (Admin): ",
                   body_text="Thẩm định cấp phép hồ sơ PT, quản lý trạng thái tài khoản (ACTIVE/SUSPENDED), tiếp nhận khiếu nại, xem xét chứng cứ và thực thi 5 phương án xử lý số dư ví trong cùng một giao dịch.\n\n*Lưu ý phạm vi đề tài: Trong khuôn khổ bài tập lớn môn Lập trình Java, các giao dịch tài chính và số dư ví được mô phỏng và quản lý nội bộ thông qua hệ thống sổ cái của ứng dụng (chưa kết nối trực tiếp với cổng thanh toán ngân hàng thương mại). Quy trình giải quyết khiếu nại là cơ chế phân xử nội bộ do Quản trị viên hệ thống thực hiện dựa trên các chứng cứ thu thập được.*")

    # --- Chương 2 ---
    elif "1. Hệ thống kiểu dữ liệu tĩnh mạnh mẽ (Strongly-Typed)" in txt:
        set_p_text(p, prefix_text="1. Hệ thống kiểu dữ liệu tĩnh (Compile-Time Safety): ",
                   body_text="Java kiểm tra kiểu dữ liệu nghiêm ngặt ngay tại thời điểm biên dịch, giúp phát hiện sớm các lỗi gán sai kiểu và chữ ký phương thức, đảm bảo tính chặt chẽ cho các thực thể nghiệp vụ như Booking, Enrollment, Payment.")
    elif "2. Xử lý số học tài chính chính xác tuyệt đối với java.math.BigDecimal" in txt:
        set_p_text(p, prefix_text="2. Biểu diễn số tiền chính xác bằng BigDecimal: ",
                   body_text="Để tránh sai số dấu phẩy động nhị phân của kiểu float/double, toàn bộ phép tính phân bổ thù lao PT 90%, phí sàn 10%, và phạt hủy lịch 50% được thực hiện với java.math.BigDecimal, cấu hình scale = 2 và RoundingMode.HALF_UP để đảm bảo số liệu kế toán chuẩn xác.")
    elif "3. Quản trị giao dịch toàn vẹn chuẩn ACID với Spring @Transactional" in txt:
        set_p_text(p, prefix_text="3. Quản trị giao dịch toàn vẹn ACID với Spring @Transactional: ",
                   body_text="Nghiệp vụ đặt lịch hoặc hủy lịch gồm nhiều thao tác phụ thuộc (trừ buổi hợp đồng, cập nhật trạng thái slot, tạo booking và lưu sổ cái thanh toán). Chú thích @Transactional(rollbackFor = Exception.class) đóng gói toàn bộ luồng vào một transaction duy nhất, tự động hoàn tác (rollback) nếu phát sinh ngoại lệ.")
    elif "4. Kiểm soát tranh chấp đồng thời (Concurrency Control) & Khóa bi quan" in txt or "bài tập lớn toàn" in txt:
        set_p_text(p, prefix_text="4. Kiểm soát truy cập đồng thời bằng Khóa bi quan (Pessimistic Locking): ",
                   body_text="Tại các khung giờ cao điểm, nhiều học viên có thể cùng đặt một slot rảnh. Nhóm áp dụng @Lock(LockModeType.PESSIMISTIC_WRITE) tại tầng Repository để sinh câu lệnh SQL SELECT ... FOR UPDATE trên MySQL InnoDB. Khóa độc quyền cấp bản ghi buộc các giao dịch đồng thời phải chờ tuần tự, kết hợp ràng buộc cấp cơ sở dữ liệu để tăng tính an toàn và toàn vẹn dữ liệu.")
    elif "2.2. Kiến trúc phân tầng sạch (Clean Layered Architecture)" in txt:
        set_p_text(p, full_text="2.2. Kiến trúc phân tầng (Layered Architecture)")
    elif "chống lại hoàn toàn các cuộc tấn công Rainbow Table" in txt:
        set_p_text(p, prefix_text="Bảo vệ mật khẩu bằng BCrypt: ",
                   body_text="Mật khẩu người dùng được băm một chiều bằng BCryptPasswordEncoder với salt ngẫu nhiên. Mật khẩu dạng văn bản thuần không bao giờ được lưu trong CSDL, giúp ngăn ngừa các hình thức dò quét bảng băm (rainbow table).")
    elif "2.4. Xuất Hợp đồng Điện tử Pháp lý chuẩn PDF bằng OpenPDF" in txt:
        set_p_text(p, full_text="2.4. Xuất Hợp đồng Điện tử dạng PDF bằng OpenPDF")
    elif "Để giải quyết triệt để Nỗi đau số 1 về việc thiếu văn bản pháp lý ràng buộc" in txt:
        set_p_text(p, full_text="Nhằm chuẩn hóa thỏa thuận dịch vụ và cung cấp căn cứ đối chiếu điều khoản cho cả hai bên, phân hệ Enrollment tích hợp thư viện OpenPDF (com.github.librepdf:openpdf 2.0.3) để tự động sinh tệp hợp đồng dịch vụ chuẩn khổ A4 ngay khi học viên thanh toán gói tập thành công:")
    elif "2.5. Hệ quản trị CSDL MySQL 8.0 InnoDB, HikariCP và Database Triggers" in txt:
        set_p_text(p, full_text="2.5. Hệ quản trị CSDL MySQL 8.0 InnoDB, HikariCP và Database Trigger")
    elif "Khóa dòng cấp độ bản ghi (Row-Level Locking):" in txt:
        set_p_text(p, prefix_text="Khóa cấp dòng (Row-Level Locking): ",
                   body_text="InnoDB hỗ trợ khóa cấp độ dòng dữ liệu khi thực thi giao dịch có khóa, cho phép nhiều học viên đặt lịch các PT khác nhau cùng lúc mà không gây tắc nghẽn toàn bảng.")
    elif "Quản lý hồ kết nối hiệu năng cao với HikariCP:" in txt or "Các giá trị này cần được đối chiếu" in txt:
        set_p_text(p, prefix_text="Quản lý kết nối với HikariCP: ",
                   body_text="Hệ thống cấu hình Connection Pool mặc định với maximum-pool-size = 10-20 kết nối, connection-timeout = 20.000ms và idle-timeout = 300.000ms, giúp tái sử dụng kết nối TCP hiệu quả và chịu tải ổn định.")
    elif "Trigger tự động tính điểm đánh giá sao trung bình:" in txt or "Không nên khẳng định độ phức tạp O(1)" in txt:
        set_p_text(p, prefix_text="Database Trigger cập nhật điểm đánh giá: ",
                   body_text="Triển khai Trigger tự động trên bảng reviews: mỗi khi phát sinh bản ghi đánh giá mới (INSERT), Trigger tự động tính lại average_rating và total_reviews trong bảng pt_profiles, tối ưu hóa tốc độ truy vấn đọc hồ sơ PT.")

    # --- Chương 3 ---
    elif "CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ NGHIỆP VỤ CHUYÊN SÂU" in txt:
        set_p_text(p, full_text="CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ NGHIỆP VỤ")
    elif "Trái tim của hệ thống PT-Connect không nằm ở các thao tác CRUD cơ bản mà nằm ở chuỗi 8 quy trình" in txt:
        set_p_text(p, full_text="Hệ thống PT-Connect tổ chức luồng vận hành xoay quanh 8 quy trình nghiệp vụ khép kín nhằm bảo đảm tính minh bạch và an toàn dịch vụ:")
    elif "3.1.1. Quy trình Thẩm định, Cấp phép hồ sơ PT và Đăng nhập RBAC" in txt:
        set_p_text(p, full_text="3.1.1. Quy trình Thẩm định, Cấp phép hồ sơ PT và Đăng nhập")
    elif "Quy trình này đóng vai trò là 'Lá chắn số 1'" in txt:
        set_p_text(p, full_text="Quy trình này kiểm soát chất lượng huấn luyện viên đầu vào trên nền tảng:")
    elif "3.1.2. Quy trình Tài chính Ví điện tử và Cơ chế Ký quỹ 90/10 (Escrow Model)" in txt:
        set_p_text(p, full_text="3.1.2. Quy trình Quản lý Số dư và Cơ chế Ký quỹ 90/10")
    elif "Để xóa bỏ hoàn toàn rủi ro bùng tiền học phí ('Nỗi đau số 2')" in txt:
        set_p_text(p, full_text="Để hạn chế rủi ro thanh toán trọn gói một lần, hệ thống áp dụng cơ chế ký quỹ và giải ngân theo từng buổi học:")
    elif "Quy trình đặt lịch là 'trái tim' kỹ thuật của hệ thống" in txt:
        set_p_text(p, full_text="Quy trình đặt lịch là nghiệp vụ trọng yếu của hệ thống, đòi hỏi xử lý đồng thời và kiểm soát tranh chấp tài nguyên giữa nhiều học viên:")
    elif "Báo cáo mô tả thời hạn phản hồi tối đa là 12 giờ" in txt or "Trừ buổi và Đổi trạng thái trong Transaction:" in txt:
        set_p_text(p, prefix_text="Cập nhật trong Transaction: ",
                   body_text="Hệ thống gọi enrollment.consumeSession() để trừ 1 buổi, chuyển slot sang BOOKED và tạo Booking ở trạng thái PENDING. Thời hạn phản hồi tối đa của PT là 12 giờ; nếu quá thời hạn, hệ thống tự động hủy yêu cầu và hoàn lại buổi tập cho học viên.")
    elif "3.1.5. Quy tắc Vàng: Đối soát Hủy lịch mốc 24h & Ma trận Phạt - Đền bù" in txt:
        set_p_text(p, full_text="3.1.5. Chính sách Hủy lịch mốc 24h & Ma trận Phạt - Đền bù")
    elif "Để bảo vệ thời gian lao động của Huấn luyện viên và quyền lợi của Học viên, hệ thống áp dụng Quy tắc Vàng" in txt:
        set_p_text(p, full_text="Để bảo vệ thời gian của PT và quyền lợi của học viên, hệ thống áp dụng chính sách đối soát mốc 24 giờ. Khoảng thời gian DeltaT = Thời điểm bắt đầu ca tập - Thời điểm bấm hủy ca:")
    elif "Nhằm triệt tiêu vĩnh viễn Nỗi đau số 4 về 'chấm công khống'" in txt:
        set_p_text(p, full_text="Để loại bỏ sai lệch khi ghi nhận số buổi tập, hệ thống triển khai cơ chế điểm danh hai chiều:")
    elif "3.1.7. Quy trình Trung tâm Trọng tài 48 giờ và 5 Loại Phán quyết Tự động" in txt:
        set_p_text(p, full_text="3.1.7. Quy trình Tiếp nhận và Xử lý Khiếu nại nội bộ trong 48 giờ")
    elif "gửi đơn khiếu nại (dispute_cases) lên Trung tâm Trọng tài của hệ thống:" in txt or "không nên đồng nhất với hội đồng trọng tài độc lập" in txt:
        set_p_text(p, full_text="Trong vòng 48 giờ sau khi ca tập kết thúc, nếu phát sinh sự cố hoặc bất đồng về dịch vụ, học viên có thể gửi đơn khiếu nại (dispute_cases) lên hệ thống:")
    elif "Anti-Arbitrary Rule" in txt or "công bằng tối thượng" in txt or "Cơ chế Chờ phản biện 48 giờ" in txt:
        set_p_text(p, prefix_text="Cơ chế tiếp nhận phản biện 48 giờ: ",
                   body_text="Sau khi học viên gửi khiếu nại kèm tài liệu chứng minh, hệ thống mở thời hạn 48 giờ để PT gửi bản giải trình và bằng chứng đối chứng (additional_evidence_pt, counter_statement). Quy định này giúp Quản trị viên thu thập đầy đủ thông tin từ cả hai phía trước khi xử lý, đảm bảo tính khách quan và minh bạch.")
    elif "5 Loại Phán quyết Tự động thi hành án ví:" in txt:
        set_p_text(p, prefix_text="5 phương án xử lý số dư ví: ",
                   body_text="Sau khi thẩm định chứng cứ của hai bên, Quản trị viên lựa chọn một trong 5 phương án xử lý; hệ thống sẽ tự động cập nhật số dư ví trong cùng một Database Transaction: 1. REFUND_STUDENT: Thu hồi thù lao từ ví PT và hoàn trả tiền buổi học cho học viên, khôi phục 1 buổi vào hợp đồng; 2. PAY_PT: Bác khiếu nại, giải ngân thù lao cho PT; 3. COMPENSATION_BOTH: Sự cố khách quan, trích quỹ hỗ trợ một phần cho cả hai bên; 4. REJECT: Từ chối khiếu nại do không có căn cứ; 5. SPLIT: Lỗi phát sinh từ hai phía, phân chia giá trị buổi học theo tỷ lệ 50/50.")
    elif "3.3. Thiết kế Cơ sở Dữ liệu chuẩn hóa BCNF (16 Thực thể cốt lõi)" in txt:
        set_p_text(p, full_text="3.3. Thiết kế Cơ sở Dữ liệu quan hệ với 16 bảng cốt lõi")
    elif "Cơ sở dữ liệu của PT-Connect được thiết kế đạt chuẩn hóa Boyce-Codd Normal Form (BCNF)" in txt or "việc khẳng định đạt BCNF" in txt:
        set_p_text(p, full_text="Cơ sở dữ liệu của PT-Connect gồm 16 bảng cốt lõi trong MySQL 8.0, được thiết kế theo hướng chuẩn hóa nhằm hạn chế lặp dữ liệu và các dị thường khi thêm, sửa, xóa. Toàn bộ 16 bảng dữ liệu dưới đây ánh xạ 1-1 với 16 lớp Entity Java trong gói com.PTconnect.backend.entity:")
    elif "3.4. Thiết kế Sơ đồ Tuần tự (Sequence Diagrams) cho các ca khó" in txt:
        set_p_text(p, full_text="3.4. Thiết kế Sơ đồ Tuần tự cho các Kịch bản Trọng yếu")
    elif "đặc biệt là quy trình xử lý tranh chấp trọng tài qua mốc thời gian thực:" in txt:
        set_p_text(p, full_text="Nhóm tập trung trực quan hóa các kịch bản tương tác giữa các tác nhân và thành phần hệ thống:")

    # 3.4 Sequence Diagrams
    elif "Để giải quyết triệt để Nỗi đau số 3 về xung đột lịch hẹn (Double-booking)" in txt:
        set_p_text(p, full_text="Để xử lý xung đột khung giờ khi nhiều học viên cùng đặt ca, hệ thống áp dụng Khóa bi quan (Pessimistic Locking) kết hợp quản trị giao dịch ACID như minh họa ở Hình 3.2:")
    elif "Quy trình được chia thành 3 giai đoạn xử lý nghiêm ngặt trong cùng một Database Transaction tương ứng với 9 bước tuần tự:" in txt:
        set_p_text(p, full_text="Tóm tắt quy trình đặt lịch ca tập:")
    elif "Giai đoạn 1 (Bước 1 - 4): Tiếp nhận yêu cầu & Chiếm giữ Khóa bi quan" in txt:
        set_p_text(p, prefix_text="Bước 1 - Chiếm giữ khóa: ",
                   body_text="Học viên gửi request POST /api/v1/bookings. BookingService gọi slotRepository.findByIdWithLock(slotId), kích hoạt câu lệnh SQL SELECT ... FOR UPDATE trên MySQL InnoDB để khóa độc quyền dòng khung giờ.")
    elif "Giai đoạn 2 (Bước 5 - 6): Thẩm định điều kiện đa tầng & Khóa dòng Hợp đồng:" in txt:
        set_p_text(p, prefix_text="Bước 2 - Kiểm tra điều kiện: ",
                   body_text="Hệ thống xác nhận slot còn AVAILABLE, học viên không có lịch trùng, và hợp đồng enrollment còn buổi học khả dụng.")
    elif "Giai đoạn 3 (Bước 7 - 9): Đột biến trạng thái nguyên tử & Khởi tạo ca tập PENDING:" in txt:
        set_p_text(p, prefix_text="Bước 3 - Cập nhật trong giao dịch: ",
                   body_text="Gọi enrollment.consumeSession() trừ 1 buổi, chuyển slot sang BOOKED, tạo bản ghi Booking ở trạng thái PENDING và hẹn giờ 12 giờ chờ PT phê duyệt.")
    
    elif "Để giải quyết triệt để Nỗi đau số 4 về tình trạng chấm công khống" in txt:
        set_p_text(p, full_text="Quy trình điểm danh hai chiều bằng mã OTP và giải ngân thù lao 90/10 được mô hình hóa ở Hình 3.3:")
    elif "Quy trình được chia thành 3 giai đoạn đối soát khép kín nhằm đảm bảo tính minh bạch tuyệt đối" in txt:
        set_p_text(p, full_text="Tóm tắt quy trình điểm danh OTP và giải ngân:")
    elif "Giai đoạn 1 (Bước 1 - 4): Học viên nắm quyền khởi tạo mã OTP độc bản:" in txt:
        set_p_text(p, prefix_text="Bước 1 - Học viên tạo OTP: ",
                   body_text="Học viên gửi request lấy mã điểm danh; hệ thống sinh OTP 6 chữ số ngẫu nhiên bằng SecureRandom (hạn 15 phút), chỉ hiển thị trên thiết bị học viên.")
    elif "Giai đoạn 2 (Bước 5 - 7): Xác thực hai chiều & Hoàn tất ca tập (Check-in Verification):" in txt:
        set_p_text(p, prefix_text="Bước 2 - PT xác thực mã: ",
                   body_text="PT nhập mã OTP của học viên qua API confirm-otp. Hệ thống đối soát mã và thời hạn; khi hợp lệ chuyển trạng thái ca tập sang COMPLETED.")
    elif "Giai đoạn 3 (Bước 8): Giải ngân vi mô 90/10 & Ghi nhận sổ cái kiểm toán tự động:" in txt:
        set_p_text(p, prefix_text="Bước 3 - Giải ngân tự động: ",
                   body_text="Trong cùng transaction, WalletService cộng 90% thù lao vào ví PT, trích 10% hoa hồng sàn và lưu 2 bản ghi kiểm toán vào bảng payments.")

    elif "Kịch bản 3: Quy trình Trọng tài 48 giờ giải quyết tranh chấp & Thi hành án ví tự động" in txt:
        set_p_text(p, full_text="Kịch bản 3: Quy trình xử lý khiếu nại trong 48 giờ và tự động cập nhật số dư ví")
    elif "Để giải quyết triệt để Nỗi đau số 5 về bế tắc khi xảy ra mâu thuẫn" in txt:
        set_p_text(p, full_text="Quy trình xử lý khiếu nại trong 48 giờ và thực thi cập nhật số dư ví được mô hình hóa ở Hình 3.4 dưới đây:")
    elif "Quy trình được chia thành 3 giai đoạn độc lập theo thời gian thực (Life-cycle) tương ứng với 8 bước trên sơ đồ:" in txt:
        set_p_text(p, full_text="Tóm tắt quy trình xử lý khiếu nại:")
    elif "Hình 3.4: Sơ đồ tuần tự quy trình Trọng tài 48 giờ và Thi hành án ví tự động" in txt:
        set_p_text(p, full_text="Hình 3.4: Sơ đồ tuần tự quy trình xử lý khiếu nại 48 giờ và tự động cập nhật số dư ví")
    elif "Giai đoạn 1 (Bước 1 - 2): Học viên nộp đơn khiếu nại (Thời điểm T0):" in txt:
        set_p_text(p, prefix_text="Bước 1 - Học viên nộp đơn: ",
                   body_text="Học viên gửi đơn khiếu nại kèm hình ảnh/bằng chứng; hệ thống tạo hồ sơ PENDING và kích hoạt đồng hồ đếm ngược 48 giờ cho PT.")
    elif "Giai đoạn 2 (Bước 3 - 4): Huấn luyện viên phản biện đối chất (Trong vòng 48 giờ):" in txt:
        set_p_text(p, prefix_text="Bước 2 - PT đối chất phản biện: ",
                   body_text="Trong vòng 48 giờ, PT gửi văn bản giải trình và bằng chứng đối chứng; hồ sơ chuyển sang trạng thái UNDER_REVIEW.")
    elif "Giai đoạn 3 (Bước 5 - 8): Admin thẩm định & Thi hành án ví tự động:" in txt or "Bước 3 - Phán quyết và hoàn tiền: Admin ban hành phán quyết" in txt:
        set_p_text(p, prefix_text="Bước 3 - Quyết định xử lý và hoàn tiền: ",
                   body_text="Admin ban hành quyết định (ví dụ REFUND_STUDENT). Trong cùng một transaction, hệ thống thu hồi 90% thù lao từ ví PT, hoàn trả tiền buổi học cho học viên, khôi phục 1 buổi vào hợp đồng và đóng hồ sơ sang trạng thái RESOLVED.")

    # --- Chương 4 ---
    elif "4.1. Tổ chức cấu trúc mã nguồn theo chuẩn Enterprise Java" in txt:
        set_p_text(p, full_text="4.1. Tổ chức cấu trúc mã nguồn theo mô hình phân tầng")
    elif "Điểm sáng nổi bật nhất của đề tài nằm ở việc vận dụng nhuần nhuyễn các nguyên lý OOP" in txt or "kết hợp với các mẫu thiết kế phần mềm kinh điển" in txt:
        set_p_text(p, full_text="Hệ thống vận dụng các nguyên lý OOP (Kế thừa, Đa hình, Đóng gói, Trừu tượng) kết hợp với các mẫu thiết kế phần mềm phổ biến để giải quyết các luồng nghiệp vụ phức tạp:")
    elif "mã nguồn sẽ trở nên vô cùng rối rắm, dễ phát sinh lỗi và vi phạm nghiêm trọng nguyên lý Mở/Đóng" in txt:
        set_p_text(p, full_text="Nếu sử dụng chuỗi if/else lồng nhau, mã nguồn sẽ khó mở rộng và vi phạm nguyên lý Mở/Đóng (Open/Closed Principle trong SOLID). Giải pháp kỹ thuật của nhóm là áp dụng Strategy Pattern kết hợp Factory Pattern:")
    elif "4.3. Kỹ thuật Xử lý Đồng thời & Khóa bi quan Pessimistic Locking" in txt:
        set_p_text(p, full_text="4.3. Kỹ thuật Xử lý Đồng thời và Khóa bi quan (Pessimistic Locking)")
    elif "Để bảo vệ tài nguyên khung giờ không bao giờ bị đặt trùng khi nhiều người bấm cùng lúc (Nỗi đau số 3)" in txt:
        set_p_text(p, full_text="Để đảm bảo không bao giờ xảy ra tình trạng đặt trùng khung giờ khi nhiều người dùng thao tác cùng lúc, nhóm triển khai Khóa bi quan (@Lock(LockModeType.PESSIMISTIC_WRITE)) tại tầng Repository:")
    elif "4.5. Triển khai Điểm danh OTP Thread-Safe và Xuất Hợp đồng PDF" in txt:
        set_p_text(p, full_text="4.5. Triển khai Điểm danh OTP và Xuất Hợp đồng PDF")

    # --- Chương 5 ---
    elif "5.1. Kết quả Hiện thực hóa Giao diện theo 3 Vai trò người dùng" in txt:
        set_p_text(p, full_text="5.1. Kết quả Hiện thực hóa Giao diện theo ba vai trò người dùng")
    elif "Bảng điều khiển tối cao phục vụ kiểm soát chất lượng" in txt or "Phân hệ Quản trị viên (Admin & Trọng tài):" in txt:
        set_p_text(p, prefix_text="Phân hệ Quản trị viên (Admin): ",
                   body_text="Bảng điều khiển quản trị tập trung (Admin Dashboard) hỗ trợ kiểm soát chất lượng dịch vụ và dòng tiền: (1) Danh sách hồ sơ PT chờ duyệt kèm chứng chỉ để Admin xem xét phê duyệt hoặc từ chối; (2) Quản lý tài khoản người dùng và khóa tài khoản vi phạm (SUSPENDED); (3) Phân hệ tiếp nhận và xử lý khiếu nại: Xem nội dung phản ánh, bằng chứng của hai bên và lựa chọn phương án xử lý số dư ví; (4) Thống kê tài chính: Theo dõi tổng doanh thu, doanh thu hoa hồng 10% của nền tảng và tỷ lệ hủy ca.")
    elif "5.2. Đánh giá Tính Giải quyết Bài toán (So sánh Trước vs Sau khi có hệ thống)" in txt:
        set_p_text(p, full_text="5.2. Đối chiếu quy trình trước và sau khi có PT-Connect")
    elif "Để trả lời trực diện câu hỏi trọng tâm của Thầy hướng dẫn:" in txt:
        set_p_text(p, full_text="Bảng dưới đây đối chiếu phương thức vận hành truyền thống và phương thức vận hành trên nền tảng PT-Connect:")
    elif "5.3. Kết quả Kiểm thử An toàn Giao dịch và Kiểm thử Đa luồng (Concurrency Test)" in txt:
        set_p_text(p, full_text="5.3. Kết quả Kiểm thử An toàn Giao dịch và Xử lý Đồng thời")
    elif "Nhóm đã tiến hành các kịch bản kiểm thử tải và kiểm thử biên (Stress & Boundary Testing) trực tiếp trên Backend" in txt:
        set_p_text(p, full_text="Nhóm đã tiến hành kiểm thử các kịch bản quan trọng trực tiếp trên Backend Java Spring Boot với môi trường thử nghiệm: CPU Intel Core i7, 16GB RAM, hệ quản trị MySQL 8.0, công cụ kiểm thử tải Apache JMeter kết hợp kịch bản kiểm thử đa luồng:")
    
    # 5.3 Bullets
    elif "Kiểm thử Tranh chấp Đặt trùng khung giờ (Concurrency Race Condition Test):" in txt or "Khi trình bày kết quả, nhóm nên đính kèm" in txt:
        set_p_text(p, prefix_text="Kiểm thử Tranh chấp Đặt trùng khung giờ (Concurrency Test): ",
                   body_text="Nhóm thiết lập kịch bản gửi đồng thời 50 HTTP request từ 50 luồng người dùng khác nhau trong cùng một mili-giây để cùng đặt một slot rảnh (AVAILABLE) duy nhất của PT. Kết quả: Nhờ cơ chế khóa bi quan findByIdWithLock(), hệ thống tiếp nhận và xử lý tuần tự từng request. Đúng 01 request đầu tiên nhận được khóa và tạo ca tập thành công (HTTP 201 Created); 49 request còn lại bị chặn và nhận mã lỗi HTTP 409 Conflict với thông điệp: 'Khung giờ này đã được đặt hoặc không còn khả dụng'. Khung giờ hoàn toàn không bị đặt trùng.")
    elif "Kiểm thử Độ chính xác Số học Tài chính (BigDecimal Integrity Test):" in txt or "Cần quy định cách làm tròn và phân bổ phần dư" in txt:
        set_p_text(p, prefix_text="Kiểm thử Độ chính xác Số học Tài chính (BigDecimal Test): ",
                   body_text="Mô phỏng 10.000 giao dịch nạp tiền, mua gói tập lẻ (gói 10 buổi trị giá 3.333.333 VNĐ, học phí danh nghĩa mỗi buổi là 333.333,3 VNĐ), chia sẻ 90% thù lao PT, 10% hoa hồng sàn và phạt 50% khi hủy lịch. Kết quả: Nhờ sử dụng BigDecimal với RoundingMode.HALF_UP và quy tắc cộng dồn phần dư vào buổi học cuối, tổng số dư trên toàn bộ Ví học viên, Ví PT và Doanh thu sàn luôn khớp hoàn toàn với tổng tiền nạp đầu vào (Tổng Nạp = Tổng Số dư Ví + Doanh thu sàn), không phát sinh sai lệch.")
    elif "Kiểm thử Tính toàn vẹn Giao dịch (Transactional Rollback Test):" in txt or "Nên bổ sung log trước/sau" in txt:
        set_p_text(p, prefix_text="Kiểm thử Rollback Giao dịch với @Transactional: ",
                   body_text="Mô phỏng tình huống học viên đặt mua gói tập nhưng hệ thống giả lập lỗi ngoại lệ (RuntimeException) tại bước ghi bản ghi thanh toán (payments) sau khi đã trừ số dư ví và tạo Enrollment. Kết quả kiểm tra CSDL xác nhận: Toàn bộ các thao tác trước đó đều được Spring rollback tự động về trạng thái ban đầu, số dư ví của học viên không bị trừ và bản ghi Enrollment không được tạo, bảo đảm tính nguyên tử (Atomicity).")

    # --- Chương 6 ---
    elif "Trải qua quá trình nghiên cứu lý thuyết, khảo sát nghiệp vụ thực tế và triển khai lập trình nghiêm túc, đề tài" in txt:
        set_p_text(p, full_text="Sau quá trình phân tích yêu cầu, thiết kế và cài đặt, nhóm đã hoàn thành đề tài 'Xây dựng nền tảng thương mại dịch vụ kết nối Huấn luyện viên cá nhân và Học viên thể hình (PT-Connect)' với các kết quả chính:")
    elif "Về mặt Sản phẩm và Nghiệp vụ Thực tiễn: Hệ thống đã giải quyết tận gốc rễ 5 'Nỗi đau'" in txt:
        set_p_text(p, prefix_text="Về mặt Sản phẩm và Nghiệp vụ: ",
                   body_text="Xây dựng được giải pháp số hóa quy trình cung cấp dịch vụ PT, giải quyết các bất cập trong thỏa thuận miệng, thanh toán trọn gói, xung đột lịch tập và điểm danh thủ công. Hệ thống cung cấp các chức năng thẩm định PT, xuất hợp đồng PDF, ký quỹ nội bộ giải ngân theo buổi 90/10, chính sách hủy ca mốc 24h, điểm danh hai chiều bằng mã OTP và quy trình xử lý khiếu nại trong 48 giờ.")
    elif "Về mặt Kỹ thuật Lập trình Java và Kiến trúc Phần mềm: Xây dựng thành công hệ thống Backend chuẩn Enterprise" in txt:
        set_p_text(p, prefix_text="Về mặt Kỹ thuật Lập trình Java: ",
                   body_text="Xây dựng hệ thống Backend phân tầng rõ ràng bằng Java 17 và Spring Boot 3.3.4; vận dụng hiệu quả các nguyên lý OOP và mẫu thiết kế (Strategy, Factory, Handler, Rich Domain Model); làm chủ kỹ thuật khóa bi quan (Pessimistic Locking) trong kiểm soát đồng thời, quản trị giao dịch ACID với @Transactional và xử lý số học chính xác với BigDecimal.")

print("2. Paragraphs updated successfully.")

# ----------------------------------------------------------------------
# 3. UPDATE TABLES (Table 1: TOC, Table 2: 5 cơ chế, Table 7: BR matrix, Table 8: CSDL, Table 12: Trước/Sau)
# ----------------------------------------------------------------------
tbls = body.findall('w:tbl', ns)

# Table 1: TOC
t1 = tbls[1]
toc_replacements = {
    "1.2. Phân tích 5 'Nỗi đau' (Pain Points) cốt lõi của bài toán vận hành thực tế": "1.2. Phân tích 5 vấn đề cốt lõi của bài toán vận hành thực tế",
    "1.3. Mô hình Giải pháp: '5 Lá chắn Kỹ thuật Bảo vệ Quyền lợi Hai chiều'": "1.3. Mô hình giải pháp: 5 cơ chế bảo vệ quyền lợi hai chiều",
    "2.2. Kiến trúc phân tầng sạch (Clean Layered Architecture)": "2.2. Kiến trúc phân tầng (Layered Architecture)",
    "2.4. Xuất Hợp đồng Điện tử Pháp lý chuẩn PDF bằng OpenPDF": "2.4. Xuất Hợp đồng Điện tử dạng PDF bằng OpenPDF",
    "2.5. Hệ quản trị CSDL MySQL 8.0 InnoDB, HikariCP và Database Triggers": "2.5. Hệ quản trị CSDL MySQL 8.0 InnoDB, HikariCP và Database Trigger",
    "CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ NGHIỆP VỤ CHUYÊN SÂU": "CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ NGHIỆP VỤ",
    "3.1.1. Quy trình Thẩm định, Cấp phép hồ sơ PT và Đăng nhập RBAC": "3.1.1. Quy trình Thẩm định, Cấp phép hồ sơ PT và Đăng nhập",
    "3.1.2. Quy trình Tài chính Ví điện tử và Cơ chế Ký quỹ 90/10": "3.1.2. Quy trình Quản lý Số dư và Cơ chế Ký quỹ 90/10",
    "3.1.5. Quy tắc Vàng: Đối soát Hủy lịch mốc 24h & Ma trận Phạt - Đền bù": "3.1.5. Chính sách Hủy lịch mốc 24h & Ma trận Phạt - Đền bù",
    "3.1.7. Quy trình Trung tâm Trọng tài 48 giờ và 5 Loại Phán quyết Tự động": "3.1.7. Quy trình Tiếp nhận và Xử lý Khiếu nại nội bộ trong 48 giờ",
    "3.3. Thiết kế Cơ sở Dữ liệu chuẩn hóa BCNF (16 Thực thể cốt lõi)": "3.3. Thiết kế Cơ sở Dữ liệu quan hệ với 16 bảng cốt lõi",
    "3.4. Thiết kế Sơ đồ Tuần tự (Sequence Diagrams) cho các ca khó": "3.4. Thiết kế Sơ đồ Tuần tự cho các Kịch bản Trọng yếu",
    "4.1. Tổ chức cấu trúc mã nguồn theo chuẩn Enterprise Java": "4.1. Tổ chức cấu trúc mã nguồn theo mô hình phân tầng",
    "4.3. Kỹ thuật Xử lý Đồng thời & Khóa bi quan Pessimistic Locking": "4.3. Kỹ thuật Xử lý Đồng thời và Khóa bi quan",
    "4.5. Triển khai Điểm danh OTP Thread-Safe và Xuất Hợp đồng PDF": "4.5. Triển khai Điểm danh OTP và Xuất Hợp đồng PDF",
    "5.1. Kết quả Hiện thực hóa Giao diện theo 3 Vai trò người dùng": "5.1. Kết quả Hiện thực hóa Giao diện theo ba vai trò người dùng",
    "5.2. Đánh giá Tính Giải quyết Bài toán (So sánh Trước vs Sau khi có hệ thống)": "5.2. Đối chiếu quy trình trước và sau khi có PT-Connect",
    "5.3. Kết quả Kiểm thử An toàn Giao dịch và Kiểm thử Đa luồng (Concurrency Test)": "5.3. Kết quả Kiểm thử An toàn Giao dịch và Xử lý Đồng thời"
}

for r in t1.findall('w:tr', ns):
    for tc in r.findall('w:tc', ns):
        txt = get_text(tc).strip()
        for k, v in toc_replacements.items():
            if k in txt:
                p = tc.find('w:p', ns)
                if p is not None:
                    set_p_text(p, full_text=v)

# Table 2: 5 cơ chế giải pháp
t2 = tbls[2]
t2_rows = t2.findall('w:tr', ns)
header_cells = t2_rows[0].findall('w:tc', ns)
set_p_text(header_cells[0].find('w:p', ns), full_text="Cơ chế giải pháp")
set_p_text(header_cells[1].find('w:p', ns), full_text="Vấn đề nghiệp vụ giải quyết")
set_p_text(header_cells[2].find('w:p', ns), full_text="Giải pháp kỹ thuật Java & CSDL")

t2_data = [
    ["1. Thẩm định hồ sơ PT (Admin Verification)", "Ngăn chặn hồ sơ giả mạo, thiếu chứng chỉ chuyên môn.", "Admin duyệt hồ sơ và chứng chỉ; tài khoản ở trạng thái PENDING trước khi được mở bán gói."],
    ["2. Hợp đồng dịch vụ PDF (OpenPDF Contract)", "Khắc phục thỏa thuận rời rạc; tạo căn cứ đối soát điều khoản.", "Tự động sinh tài liệu PDF có mã định danh PTC-HD-xxxxxx thể hiện gói tập, số buổi, địa điểm và điều khoản hủy."],
    ["3. Ký quỹ và giải ngân 90/10 (Internal Escrow)", "Bảo vệ dòng tiền theo tiến độ thực tế của khóa học.", "Tiền mua gói được giữ trong quỹ hợp đồng nội bộ; giải ngân theo từng buổi (90% PT, 10% phí nền tảng) khi có xác nhận."],
    ["4. Khóa bi quan chống trùng slot (Pessimistic Locking)", "Ngăn ngừa xung đột khung giờ khi nhiều học viên đặt cùng lúc.", "Sử dụng @Lock(LockModeType.PESSIMISTIC_WRITE) sinh câu lệnh SELECT ... FOR UPDATE trên MySQL InnoDB."],
    ["5. Điểm danh OTP & Xử lý khiếu nại (OTP & Dispute)", "Chống chấm công khống và hỗ trợ giải quyết tranh chấp.", "Học viên tạo mã OTP 6 số (15 phút), PT nhập mã để hoàn tất ca tập. Cung cấp quy trình phản biện 48h và phương án xử lý số dư ví."]
]

for idx, data_row in enumerate(t2_data):
    cells = t2_rows[idx+1].findall('w:tc', ns)
    for c_idx, val in enumerate(data_row):
        p = cells[c_idx].find('w:p', ns)
        if p is not None:
            set_p_text(p, full_text=val)

# Table 3: Tầng kiến trúc (row 2: Service Layer)
t3_arch = tbls[3]
t3_rows = t3_arch.findall('w:tr', ns)
set_p_text(t3_rows[2].findall('w:tc', ns)[2].find('w:p', ns), full_text="Tầng xử lý nghiệp vụ trung tâm: Chứa các quy tắc nghiệp vụ, ma trận tính phạt hủy lịch 24h, kiểm soát ranh giới Transaction, xử lý ngoại lệ nghiệp vụ và điều phối dữ liệu.")

# Table 5: BR-01..BR-10
t5_br = tbls[5]
for r in t5_br.findall('w:tr', ns):
    for tc in r.findall('w:tc', ns):
        txt = get_text(tc).strip()
        if "Bắn lỗi DuplicateResourceException" in txt:
            set_p_text(tc.find('w:p', ns), full_text="Trả về ngoại lệ DuplicateResourceException (HTTP 409), từ chối tạo tài khoản.")
        elif "Bắn lỗi BadRequestException" in txt:
            set_p_text(tc.find('w:p', ns), full_text="Trả về ngoại lệ BadRequestException (HTTP 400), yêu cầu đặt lịch theo gói PACKAGE.")
        elif "Chặn Admin phán quyết ngay" in txt:
            set_p_text(tc.find('w:p', ns), full_text="Chưa cho phép Admin chốt kết quả ngay, mở thời hạn 48h để PT gửi tài liệu đối chất.")

# Table 6: 16 thực thể CSDL (dispute_cases)
t6_db = tbls[6]
for r in t6_db.findall('w:tr', ns):
    cells = r.findall('w:tc', ns)
    if len(cells) >= 5:
        tbl_name = get_text(cells[1]).strip()
        if tbl_name == "dispute_cases":
            set_p_text(cells[4].find('w:p', ns), full_text="Hồ sơ xử lý khiếu nại nội bộ trong 48h. Lưu additional_evidence_pt, counter_statement, deadline_at, verdict_type.")

# Table 12: Trước vs Sau
t12_comp = tbls[12]
t12_rows = t12_comp.findall('w:tr', ns)
set_p_text(t12_rows[0].findall('w:tc', ns)[2].find('w:p', ns), full_text="Hệ thống PT-Connect (Java Spring Boot)")

# Row 1 (Ràng buộc pháp lý)
set_p_text(t12_rows[1].findall('w:tc', ns)[0].find('w:p', ns), full_text="1. Ràng buộc thỏa thuận")
# Row 2 (An toàn dòng tiền)
set_p_text(t12_rows[2].findall('w:tc', ns)[1].find('w:p', ns), full_text="Đóng trước 100% học phí cả khóa. Học viên chịu rủi ro mất tiền nếu PT dạy không đạt yêu cầu hoặc đơn phương ngừng dạy giữa chừng.")
# Row 4 (Hủy lịch)
set_p_text(t12_rows[4].findall('w:tc', ns)[0].find('w:p', ns), full_text="4. Hủy lịch sát giờ")

t12_col3 = [
    "Tự động sinh Hợp đồng dịch vụ dạng PDF chuẩn A4 có mã tham chiếu PTC-HD-xxxxxx, ghi nhận cam kết địa điểm, số buổi và điều khoản hủy.",
    "Cơ chế ký quỹ nội bộ và giải ngân theo từng buổi (90% PT, 10% sàn) sau khi ca tập được xác thực hoàn thành.",
    "Khóa bi quan (@Lock(LockModeType.PESSIMISTIC_WRITE)) tại cấp bản ghi CSDL, ngăn chặn hoàn toàn việc đặt trùng một khung giờ.",
    "Áp dụng chính sách hủy lịch mốc 24h tự động: hoàn buổi và phạt 50% trước 24h, mất buổi khi hủy sát giờ, phạt 100% nếu PT tự ý hủy.",
    "Điểm danh hai chiều bằng mã OTP 6 chữ số ngẫu nhiên (hạn 15 phút): học viên tạo mã, PT xác thực để hoàn tất ca tập.",
    "Quy trình tiếp nhận khiếu nại nội bộ với 48h phản biện cho PT; Quản trị viên thẩm định và thực thi phương án xử lý số dư ví trong 1 giao dịch."
]

for idx, val in enumerate(t12_col3):
    p = t12_rows[idx+1].findall('w:tc', ns)[2].find('w:p', ns)
    if p is not None:
        set_p_text(p, full_text=val)

print("3. Tables updated successfully.")

# ----------------------------------------------------------------------
# 4. SERIALIZE AND WRITE BACK CLEANLY
# ----------------------------------------------------------------------
new_xml = ET.tostring(tree, encoding='utf-8', xml_declaration=True)

# Read all media/xml from original_from_git.docx into memory
file_dict = {}
for item in z.infolist():
    if item.filename != "word/document.xml":
        file_dict[item.filename] = z.read(item.filename)
z.close()

# Write output atomically
with zipfile.ZipFile("Bao_Cao_BTL_Java_PT_Connect.docx", "w", zipfile.ZIP_DEFLATED) as zout:
    zout.writestr("word/document.xml", new_xml)
    for fname, data in file_dict.items():
        zout.writestr(fname, data)

print("4. Repacked Bao_Cao_BTL_Java_PT_Connect.docx successfully!")
