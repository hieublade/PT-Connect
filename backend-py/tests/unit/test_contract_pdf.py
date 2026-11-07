import time
from datetime import date
from decimal import Decimal

from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.pt_profile import PTProfile
from app.models.user import PT, Student
from app.pdf.contract import ContractPdfGenerator


def test_contract_pdf_generation_and_caching(tmp_path):
    generator = ContractPdfGenerator(contract_dir=tmp_path)

    student = Student(id=1, full_name="Nguyễn Văn A", email="a@example.com", phone="0912345678")
    pt_user = PT(id=2, full_name="Trần Huấn Luyện", email="hlv@example.com", phone="0987654321")
    pt_profile = PTProfile(id=1, pt=pt_user, experience_years=5)
    course = Course(
        id=1,
        title="Khóa Giảm Cân 12 Buổi",
        total_sessions=12,
        validity_days=90,
        base_price=Decimal("3600000.00"),
        pt=pt_profile,
    )

    enrollment = Enrollment(
        id=1,
        student=student,
        course=course,
        total_sessions=12,
        remaining_sessions=12,
        final_price=Decimal("3600000.00"),
        training_location="Quận 1, TP HCM",
        start_date=date(2026, 11, 1),
        end_date=date(2027, 2, 1),
    )

    start = time.perf_counter()
    pdf_bytes = generator.generate_contract_pdf(enrollment, transaction_ref="TXN-20261101-0001")
    duration = time.perf_counter() - start

    assert duration < 1.0, f"PDF generation took {duration:.2f}s, expected < 1.0s"
    assert len(pdf_bytes) > 0
    assert pdf_bytes.startswith(b"%PDF")

    # Cached read should return the saved bytes
    start_cached = time.perf_counter()
    cached_bytes = generator.get_existing_contract_pdf(enrollment.id)
    duration_cached = time.perf_counter() - start_cached

    assert cached_bytes == pdf_bytes
    assert duration_cached < 0.1
