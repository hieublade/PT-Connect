from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from app.core.exceptions import (
    BadRequestException,
    BookingConflictException,
    ForbiddenException,
    ResourceNotFoundException,
    UnauthorizedException,
)
from app.core.handlers import register_exception_handlers
from app.main import app


def test_public_health_endpoint():
    client = TestClient(app)
    response = client.get("/api/v1/public/health")
    assert response.status_code == 200
    data = response.json()
    assert data == {"status": "UP", "message": "PT-Connect Backend is healthy"}


def test_exception_handlers_mapping():
    test_app = FastAPI()
    register_exception_handlers(test_app)

    @test_app.get("/test-404")
    def route_404():
        raise ResourceNotFoundException("User not found")

    @test_app.get("/test-409")
    def route_409():
        raise BookingConflictException("Slot already booked")

    @test_app.get("/test-401")
    def route_401():
        raise UnauthorizedException("Chưa đăng nhập")

    @test_app.get("/test-403")
    def route_403():
        raise ForbiddenException("Bạn không có quyền truy cập tài nguyên này")

    @test_app.get("/test-400")
    def route_400():
        raise BadRequestException("Dữ liệu sai")

    class BodyRequest(BaseModel):
        full_name: str = Field(..., min_length=2)

    @test_app.post("/test-validation")
    def route_val(body: BodyRequest):
        return {"ok": True}

    client = TestClient(test_app)

    # 404
    r = client.get("/test-404")
    assert r.status_code == 404
    assert r.json()["message"] == "User not found"
    assert r.json()["status"] == 404
    assert r.json()["data"] is None

    # 409
    r = client.get("/test-409")
    assert r.status_code == 409
    assert r.json()["message"] == "Slot already booked"

    # 401
    r = client.get("/test-401")
    assert r.status_code == 401
    assert r.json()["message"] == "Chưa đăng nhập"

    # 403
    r = client.get("/test-403")
    assert r.status_code == 403
    assert r.json()["message"] == "Bạn không có quyền truy cập tài nguyên này"

    # 400
    r = client.get("/test-400")
    assert r.status_code == 400
    assert r.json()["message"] == "Dữ liệu sai"

    # Validation error 400: <field>: <message>
    r = client.post("/test-validation", json={"full_name": ""})
    assert r.status_code == 400
    assert r.json()["status"] == 400
    assert "fullName:" in r.json()["message"]
