"""
Authentication API models.
"""
from dataclasses import dataclass
from typing import Optional
from .BaseModel import BaseModel, ApiRequest, ApiResponse


@dataclass
class LoginRequest(ApiRequest):
    """User login request."""
    user_id: str = ""
    password: str = ""

    def validate(self) -> bool:
        return bool(self.user_id and self.password and self.user_id.isdigit())


@dataclass
class UserInfo(BaseModel):
    """User information model."""
    id: int
    first_name: str
    last_name: str
    role: str

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


@dataclass
class LoginResponse(ApiResponse):
    """Login response with user info and token."""
    user: Optional[UserInfo] = None
    session_token: Optional[str] = None
    session_expires: Optional[str] = None

    @classmethod
    def authenticated(cls, user: UserInfo, token: str, expires: str) -> 'LoginResponse':
        """Create successful login response."""
        return cls(
            success=True,
            message=f"Welcome, {user.full_name}",
            timestamp=cls._current_timestamp(),
            user=user,
            session_token=token,
            session_expires=expires
        )

    @classmethod
    def failed(cls, reason: str) -> 'LoginResponse':
        """Create failed login response."""
        error_messages = {
            "user_not_found": "User not found",
            "invalid_password": "Invalid password",
            "invalid_credentials": "Invalid credentials format"
        }

        return cls(
            success=False,
            message=error_messages.get(reason, "Authentication failed"),
            timestamp=cls._current_timestamp(),
            errors={"auth": reason}
        )

    @staticmethod
    def _current_timestamp():
        from datetime import datetime
        return datetime.now().isoformat()


@dataclass
class QRLoginRequest(ApiRequest):
    """QR code login request."""
    qr_data: str = ""

    def validate(self) -> bool:
        return bool(self.qr_data)
