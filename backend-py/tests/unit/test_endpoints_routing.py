from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_endpoint_inventory_count():
    openapi = app.openapi()
    paths = openapi["paths"]
    # Total operation entries across all paths
    total_ops = sum(len(methods) for methods in paths.values())
    assert total_ops >= 60, f"Expected at least 60 operations, found {total_ops}"


def test_public_health_envelope():
    res = client.get("/api/v1/public/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "UP"
    assert "message" in data


def test_auth_me_requires_auth():
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401
    body = res.json()
    assert body["status"] == 401
    assert "Chưa đăng nhập" in body["message"]


def test_route_precedence_bookings_my():
    """Verify /bookings/my is not captured by /bookings/{id} as an integer parsing error."""
    # When unauthenticated, /bookings/my should reject with 401, NOT 400 (which would happen if 'my' was parsed as id)
    res = client.get("/api/v1/bookings/my")
    assert res.status_code == 401
    assert "Chưa đăng nhập" in res.json()["message"]


def test_route_precedence_enrollments_my():
    """Verify /enrollments/my is not captured by /enrollments/{id}."""
    res = client.get("/api/v1/enrollments/my")
    assert res.status_code == 401
    assert "Chưa đăng nhập" in res.json()["message"]


def test_rbac_denial_returns_403(client, db_session):
    from app.core.security import jwt_service
    from app.models.enums import Role, UserStatus
    from app.models.user import Student

    student = Student(
        email="student_rbac@example.com",
        password_hash="hashed",
        full_name="Học Viên RBAC",
        phone="0911223344",
        role=Role.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)

    student_token = jwt_service.create_token(
        user_id=student.id,
        email=student.email,
        role="STUDENT",
        full_name=student.full_name,
    )
    headers = {"Authorization": f"Bearer {student_token}"}

    # Attempt to access an admin-only endpoint: /api/v1/admin/statistics
    res = client.get("/api/v1/admin/statistics", headers=headers)
    assert res.status_code == 403
    body = res.json()
    assert body["status"] == 403
    assert "Bạn không có quyền" in body["message"]

    # Attempt to access PT-only endpoint: /api/v1/pt/profile
    res = client.get("/api/v1/pt/profile", headers=headers)
    assert res.status_code == 403
