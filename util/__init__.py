from enum import StrEnum

from config import app_bcrypt


class Collections(StrEnum):
    USER = 'users'
    PLAIN = 'plain'
    OTP_VALIDATOR = 'otp_validator'


def hash_password(password: str) -> bytes:
    return app_bcrypt.generate_password_hash(password=password)


def check_password(hashed_pass: bytes, password: str) -> bool:
    return app_bcrypt.check_password_hash(hashed_pass, password)
