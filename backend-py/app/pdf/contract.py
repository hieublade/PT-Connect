import logging
import os
from pathlib import Path

from fpdf import FPDF

from app.models.enrollment import Enrollment

logger = logging.getLogger(__name__)

CONTRACT_DIR = Path("uploads/contracts")
FONTS_DIR = Path(__file__).resolve().parent.parent.parent / "assets" / "fonts"


class ContractPdf(FPDF):
    def __init__(self):
        super().__init__(format="A4", unit="mm")
        self.set_margins(15, 15, 15)
        self.set_auto_page_break(auto=True, margin=15)
        # Add DejaVu Sans font supporting full UTF-8 Vietnamese diacritics
        regular_font = str(FONTS_DIR / "DejaVuSans.ttf")
        bold_font = str(FONTS_DIR / "DejaVuSans-Bold.ttf")

        if os.path.exists(regular_font):
            self.add_font("DejaVu", "", regular_font)
            self.font_family_name = "DejaVu"
        else:
            self.font_family_name = "Helvetica"

        if os.path.exists(bold_font):
            self.add_font("DejaVu", "B", bold_font)


class ContractPdfGenerator:
    def __init__(self, contract_dir: Path = CONTRACT_DIR):
        self.contract_dir = contract_dir
        self.contract_dir.mkdir(parents=True, exist_ok=True)

    def generate_contract_pdf(self, enrollment: Enrollment, transaction_ref: str | None = None) -> bytes:
        pdf = ContractPdf()
        pdf.add_page()
        font = pdf.font_family_name

        # Header
        pdf.set_font(font, "B", 12)
        pdf.cell(0, 6, "CONG HOA XA HOI CHU NGHIA VIET NAM", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(font, "", 10)
        pdf.cell(0, 5, "Doc lap - Tu do - Hanh phuc", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        pdf.line(60, pdf.get_y(), 150, pdf.get_y())
        pdf.ln(5)

        # Title
        pdf.set_font(font, "B", 14)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 8, "HỢP ĐỒNG DỊCH VỤ HUẤN LUYỆN CÁ NHÂN (PT)", align="C", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font(font, "", 9)
        pdf.set_text_color(100, 100, 100)
        contract_num = f"Số: PTC-HD-{enrollment.id:06d}"
        pdf.cell(0, 5, contract_num, align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        # Part I: Parties
        pdf.set_text_color(25, 118, 210)
        pdf.set_font(font, "B", 11)
        pdf.cell(0, 6, "I. THÔNG TIN CÁC BÊN THỎA THUẬN", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)

        student_name = enrollment.student.full_name if enrollment.student else "N/A"
        student_email = enrollment.student.email if enrollment.student else "N/A"
        student_phone = enrollment.student.phone if enrollment.student and enrollment.student.phone else "Chưa cập nhật"

        pt_name = enrollment.pt.pt.full_name if enrollment.pt and enrollment.pt.pt else "N/A"
        pt_email = enrollment.pt.pt.email if enrollment.pt and enrollment.pt.pt else "N/A"
        pt_exp = enrollment.pt.experience_years if enrollment.pt else 0

        # Two columns for Ben A & Ben B
        col_w = 88
        start_y = pdf.get_y()

        # Ben A
        pdf.set_fill_color(248, 249, 250)
        pdf.rect(15, start_y, col_w, 32, "F")
        pdf.set_xy(17, start_y + 2)
        pdf.set_font(font, "B", 9)
        pdf.cell(col_w - 4, 5, "BÊN A (KHÁCH HÀNG / HỌC VIÊN):", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(font, "", 8)
        pdf.set_x(17)
        pdf.cell(col_w - 4, 5, f"- Họ và tên: {student_name}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(17)
        pdf.cell(col_w - 4, 5, f"- Email: {student_email}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(17)
        pdf.cell(col_w - 4, 5, f"- Điện thoại: {student_phone}", new_x="LMARGIN", new_y="NEXT")

        # Ben B
        pdf.rect(107, start_y, col_w, 32, "F")
        pdf.set_xy(109, start_y + 2)
        pdf.set_font(font, "B", 9)
        pdf.cell(col_w - 4, 5, "BÊN B (HUẤN LUYỆN VIÊN - PT):", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(font, "", 8)
        pdf.set_x(109)
        pdf.cell(col_w - 4, 5, f"- Họ và tên: {pt_name}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(109)
        pdf.cell(col_w - 4, 5, f"- Email: {pt_email}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(109)
        pdf.cell(col_w - 4, 5, f"- Kinh nghiệm: {pt_exp} năm", new_x="LMARGIN", new_y="NEXT")

        pdf.set_y(start_y + 36)

        # Part II: Course & Payment Details
        pdf.set_text_color(25, 118, 210)
        pdf.set_font(font, "B", 11)
        pdf.cell(0, 6, "II. CHI TIẾT GÓI HUẤN LUYỆN & THANH TOÁN", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)

        course_title = enrollment.course.title if enrollment.course else "Gói tập cá nhân"
        date_range = f"{enrollment.start_date.strftime('%d/%m/%Y')} đến {enrollment.end_date.strftime('%d/%m/%Y')}"
        formatted_price = f"{float(enrollment.final_price):,.0f} VND"
        txn_ref = transaction_ref or "N/A"

        items = [
            ("Khóa học / Gói tập:", course_title),
            ("Địa điểm tập luyện cố định:", enrollment.training_location),
            ("Tổng số buổi tập:", f"{enrollment.total_sessions} buổi"),
            ("Thời hạn hợp đồng:", date_range),
            ("Học phí chốt (Final Price):", formatted_price),
            ("Phương thức thanh toán:", "Ví điện tử nội bộ PT Connect (WALLET)"),
            ("Mã giao dịch thanh toán:", txn_ref),
        ]

        for label, val in items:
            pdf.set_font(font, "B", 8)
            pdf.cell(65, 6, label, border=1, fill=False)
            is_price = label.startswith("Học phí")
            pdf.set_font(font, "B" if is_price else "", 8)
            pdf.cell(115, 6, f" {val}", border=1, new_x="LMARGIN", new_y="NEXT")

        pdf.ln(4)

        # Part III: Terms
        pdf.set_text_color(25, 118, 210)
        pdf.set_font(font, "B", 11)
        pdf.cell(0, 6, "III. ĐIỀU KHOẢN CAM KẾT & QUY ĐỊNH", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.set_font(font, "", 8)
        pdf.ln(1)

        terms = [
            "1. Bên B cam kết hướng dẫn đúng giáo án khoa học, bảo đảm an toàn tập luyện.",
            "2. Bên A cam kết tuân thủ giờ giấc tập luyện. Mọi ca tập được đặt trước trên hệ thống PT Connect.",
            "3. Chính sách hủy lịch: Thực hiện tự động theo Quy định Hủy lịch & Đền bù của Nền tảng PT Connect.",
            "4. Hợp đồng có hiệu lực kể từ thời điểm Bên A thanh toán thành công qua Ví điện tử.",
        ]
        for term in terms:
            pdf.multi_cell(pdf.epw, 5, term)

        pdf.ln(5)

        # Electronic Signatures
        sig_w = 60
        sig_y = pdf.get_y()

        pdf.set_xy(15, sig_y)
        pdf.set_font(font, "B", 8)
        pdf.cell(sig_w, 4, "ĐẠI DIỆN BÊN A", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(font, "", 7)
        pdf.cell(sig_w, 4, "(Ký điện tử)", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(font, "", 8)
        pdf.cell(sig_w, 4, f"[Xác nhận OTP / Ví]\n{student_name}", align="C")

        pdf.set_xy(75, sig_y)
        pdf.set_font(font, "B", 8)
        pdf.cell(sig_w, 4, "ĐẠI DIỆN BÊN B", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(75)
        pdf.set_font(font, "", 7)
        pdf.cell(sig_w, 4, "(Ký điện tử)", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(75)
        pdf.set_font(font, "", 8)
        pdf.cell(sig_w, 4, f"[PT Đã Phê Duyệt]\n{pt_name}", align="C")

        pdf.set_xy(135, sig_y)
        pdf.set_font(font, "B", 8)
        pdf.cell(sig_w, 4, "NỀN TẢNG PT CONNECT", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(135)
        pdf.set_font(font, "", 7)
        pdf.cell(sig_w, 4, "(Chứng thực điện tử)", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(135)
        pdf.set_font(font, "", 8)
        pdf.cell(sig_w, 4, "[CHỨNG THỰC SỐ]\nPT-Connect Platform", align="C")

        pdf_bytes = bytes(pdf.output())
        self._save_contract_file(enrollment.id, pdf_bytes)
        return pdf_bytes

    def _save_contract_file(self, enrollment_id: int, pdf_bytes: bytes) -> None:
        try:
            file_path = self.contract_dir / f"contract_{enrollment_id}.pdf"
            with open(file_path, "wb") as f:
                f.write(pdf_bytes)
            logger.info("Saved contract PDF to %s", file_path)
        except Exception as e:
            logger.warning("Failed to write contract PDF to disk: %s", e)

    def get_existing_contract_pdf(self, enrollment_id: int) -> bytes | None:
        file_path = self.contract_dir / f"contract_{enrollment_id}.pdf"
        if file_path.exists():
            try:
                with open(file_path, "rb") as f:
                    return f.read()
            except Exception as e:
                logger.warning("Failed to read contract PDF: %s", e)
        return None


contract_pdf_generator = ContractPdfGenerator()
