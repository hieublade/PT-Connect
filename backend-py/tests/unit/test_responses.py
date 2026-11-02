import re

from app.core.responses import ApiResponse, created_response, error_response, ok_response


def test_api_response_envelope():
    res = ApiResponse.success(data={"id": 1}, message="Thành công")
    dumped = res.model_dump(mode="json")

    assert dumped["status"] == 200
    assert dumped["message"] == "Thành công"
    assert dumped["data"] == {"id": 1}

    # Timestamp format: yyyy-MM-dd'T'HH:mm:ss'Z'
    pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
    assert re.match(pattern, dumped["timestamp"])


def test_api_response_created():
    res = ApiResponse.created(data={"id": 2}, message="Tạo mới thành công")
    assert res.status == 201
    assert res.message == "Tạo mới thành công"
    assert res.data == {"id": 2}


def test_api_response_error():
    res = ApiResponse.error(status=404, message="Không tìm thấy")
    assert res.status == 404
    assert res.message == "Không tìm thấy"
    assert res.data is None


def test_response_helpers():
    r1 = ok_response(data={"foo": "bar"})
    assert r1.status_code == 200

    r2 = created_response(data={"foo": "bar"}, status_code=201, body_status=200)
    assert r2.status_code == 201

    r3 = error_response(message="Lỗi", status_code=400)
    assert r3.status_code == 400
