"""
Base model classes for type-safe API data structures.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, Type, TypeVar
from datetime import datetime
import json


T = TypeVar('T', bound='BaseModel')


@dataclass
class BaseModel:
    """
    Base class for all API models providing serialization, validation, and type safety.
    """
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert model to JSON string."""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create model instance from dictionary."""
        # Filter out unknown fields to prevent errors
        valid_fields = {field.name for field in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)
    
    @classmethod
    def from_json(cls: Type[T], json_str: str) -> T:
        """Create model instance from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def validate(self) -> bool:
        """Override in subclasses for custom validation."""
        return True


@dataclass
class ApiResponse(BaseModel):
    """
    Standard API response wrapper.
    """
    success: bool
    message: str
    timestamp: str
    data: Optional[Dict[str, Any]] = None
    errors: Optional[Dict[str, str]] = None
    
    @classmethod
    def success_response(cls, message: str = "Operation successful", data: Optional[Dict] = None) -> 'ApiResponse':
        """Create success response."""
        return cls(
            success=True,
            message=message,
            timestamp=datetime.now().isoformat(),
            data=data or {}
        )
    
    @classmethod
    def error_response(cls, message: str, errors: Optional[Dict[str, str]] = None) -> 'ApiResponse':
        """Create error response."""
        return cls(
            success=False,
            message=message,
            timestamp=datetime.now().isoformat(),
            errors=errors or {}
        )


@dataclass
class ApiRequest(BaseModel):
    """
    Base API request structure.
    """
    request_id: str = ""
    timestamp: str = ""
    version: str = "2.0"
    
    def __post_init__(self):
        if not self.request_id:
            import uuid
            self.request_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()