from app.core.security import JwtService, PasswordHasher


def test_jwt_generation_and_verification():
    service = JwtService()
    assert service.algorithm == "HS384"

    token = service.create_token(
        email="student.a@ptconnect.vn",
        role="STUDENT",
        user_id=1,
        full_name="Nguyen Van A",
    )
    assert isinstance(token, str)

    payload = service.decode_token(token)
    assert payload["sub"] == "student.a@ptconnect.vn"
    assert payload["role"] == "STUDENT"
    assert payload["userId"] == 1
    assert payload["fullName"] == "Nguyen Van A"

    assert service.extract_email(token) == "student.a@ptconnect.vn"
    assert service.extract_role(token) == "STUDENT"
    assert service.extract_user_id(token) == 1
    assert not service.is_token_expired(token)
    assert service.validate_token(token, "student.a@ptconnect.vn")
    assert not service.validate_token(token, "other@domain.vn")


def test_jwt_expired():
    # Service with negative expiration
    service = JwtService(expiration_ms=-1000)
    token = service.create_token(email="test@ptconnect.vn", role="STUDENT")
    assert service.is_token_expired(token)


def test_password_hasher_compatibility():
    hasher = PasswordHasher()

    # Spring $2a$ hash from init.sql
    spring_hash = "$2a$10$IciBJIW1NX.1Za3YIyYqjO7H/SpL//eFExQrDxRk/33YLKZjOvyey"
    assert hasher.verify_password("Password123@", spring_hash)
    assert not hasher.verify_password("WrongPassword", spring_hash)

    # Generated $2b$ hash
    pwd = "MySecretPassword!2026"
    new_hash = hasher.hash_password(pwd)
    assert new_hash.startswith("$2b$")
    assert hasher.verify_password(pwd, new_hash)
    assert not hasher.verify_password("wrong", new_hash)
