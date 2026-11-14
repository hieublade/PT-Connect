import base64
import logging
import time
from typing import Any

import bcrypt
import jwt

from app.core.config import settings

logger = logging.getLogger(__name__)


class JwtService:
    def __init__(self, secret: str = settings.JWT_SECRET, expiration_ms: int = settings.JWT_EXPIRATION):
        self.secret = secret
        self.expiration_ms = expiration_ms
        self.key = self._derive_key(secret)
        self.algorithm = self._derive_algorithm(self.key)

    @staticmethod
    def _derive_key(secret: str) -> bytes:
        try:
            key_bytes = base64.b64decode(secret, validate=True)
        except Exception:
            key_bytes = secret.encode("utf-8")
        if len(key_bytes) < 32:
            key_bytes = key_bytes.ljust(32, b"\0")
        return key_bytes

    @staticmethod
    def _derive_algorithm(key: bytes) -> str:
        if len(key) >= 64:
            return "HS512"
        if len(key) >= 48:
            return "HS384"
        return "HS256"

    def create_token(
        self,
        email: str,
        role: str,
        user_id: int | None = None,
        full_name: str | None = None,
    ) -> str:
        now_ts = int(time.time())
        exp_ts = now_ts + int(self.expiration_ms / 1000)

        payload: dict[str, Any] = {
            "sub": email,
            "role": role,
            "iat": now_ts,
            "exp": exp_ts,
        }
        if user_id is not None:
            payload["userId"] = user_id
        if full_name is not None:
            payload["fullName"] = full_name

        return jwt.encode(payload, self.key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> dict[str, Any]:
        return jwt.decode(
            token,
            self.key,
            algorithms=[self.algorithm, "HS256", "HS384", "HS512"],
            options={"require": ["exp", "sub"]},
        )

    def extract_email(self, token: str) -> str | None:
        try:
            payload = self.decode_token(token)
            return payload.get("sub")
        except Exception as e:
            logger.warning("JWT email extraction failed: %s", e)
            return None

    def extract_role(self, token: str) -> str | None:
        try:
            payload = self.decode_token(token)
            return payload.get("role")
        except Exception as e:
            logger.warning("JWT role extraction failed: %s", e)
            return None

    def extract_user_id(self, token: str) -> int | None:
        try:
            payload = self.decode_token(token)
            uid = payload.get("userId")
            return int(uid) if uid is not None else None
        except Exception as e:
            logger.warning("JWT userId extraction failed: %s", e)
            return None

    def is_token_expired(self, token: str) -> bool:
        try:
            payload = self.decode_token(token)
            exp = payload.get("exp", 0)
            return exp < time.time()
        except jwt.ExpiredSignatureError:
            return True
        except Exception:
            return True

    def validate_token(self, token: str, email: str | None = None) -> bool:
        try:
            payload = self.decode_token(token)
            if email is not None and payload.get("sub") != email:
                return False
            return True
        except Exception:
            return False


class PasswordHasher:
    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt(rounds=10)
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            # bcrypt accepts both $2a$ and $2b$ hashes
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8"),
            )
        except Exception as e:
            logger.warning("Password verification failed: %s", e)
            return False


jwt_service = JwtService()
password_hasher = PasswordHasher()
