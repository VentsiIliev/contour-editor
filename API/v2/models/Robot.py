"""
Robot API models for all robot-related operations.
"""
from dataclasses import dataclass
from typing import List, Optional, Literal
from enum import Enum
from .BaseModel import BaseModel, ApiRequest, ApiResponse


class Axis(Enum):
    """Robot axes."""
    X = "X"
    Y = "Y" 
    Z = "Z"
    RX = "RX"
    RY = "RY"
    RZ = "RZ"


class Direction(Enum):
    """Movement directions."""
    POSITIVE = "positive"
    NEGATIVE = "negative"


class RobotPosition(Enum):
    """Predefined robot positions."""
    HOME = "home"
    CALIBRATION = "calibration"
    LOGIN = "login"


@dataclass
class Position3D(BaseModel):
    """3D position coordinates."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    rx: float = 0.0
    ry: float = 0.0
    rz: float = 0.0
    
    def to_list(self) -> List[float]:
        """Convert to list format."""
        return [self.x, self.y, self.z, self.rx, self.ry, self.rz]


@dataclass
class JogRequest(ApiRequest):
    """Robot jog movement request."""
    axis: Axis = Axis.X
    direction: Direction = Direction.POSITIVE
    step_size: float = 1.0
    
    def validate(self) -> bool:
        return self.step_size > 0


@dataclass
class MoveToPositionRequest(ApiRequest):
    """Move robot to predefined position."""
    position: RobotPosition = RobotPosition.HOME
    velocity: Optional[float] = None
    acceleration: Optional[float] = None


@dataclass
class MoveToCoordinatesRequest(ApiRequest):
    """Move robot to specific coordinates."""
    position: Optional[Position3D] = None
    velocity: Optional[float] = None
    acceleration: Optional[float] = None
    
    def validate(self) -> bool:
        return self.position.validate()


@dataclass
class RobotStatus(BaseModel):
    """Current robot status."""
    position: Optional[Position3D] = None
    is_moving: bool = False
    is_calibrated: bool = False
    error_state: bool = False
    error_message: Optional[str] = None
    tool_position: Optional[Position3D] = None


@dataclass
class CalibrationRequest(ApiRequest):
    """Robot calibration request."""
    calibration_type: Literal["robot", "pickup_area"] = "robot"
    
    
@dataclass
class CalibrationResponse(ApiResponse):
    """Robot calibration response."""
    calibration_image: Optional[str] = None  # Base64 encoded image
    calibration_points: Optional[List[Position3D]] = None
    calibration_matrix: Optional[List[List[float]]] = None
    
    @classmethod
    def successful(cls, message: str = "Calibration completed", 
                   image: Optional[str] = None,
                   points: Optional[List[Position3D]] = None) -> 'CalibrationResponse':
        """Create successful calibration response."""
        return cls(
            success=True,
            message=message,
            timestamp=cls._current_timestamp(),
            calibration_image=image,
            calibration_points=points
        )
    
    @staticmethod
    def _current_timestamp():
        from datetime import datetime
        return datetime.now().isoformat()


@dataclass
class RobotResponse(ApiResponse):
    """General robot operation response."""
    robot_status: Optional[RobotStatus] = None
    
    @classmethod
    def with_status(cls, message: str, status: RobotStatus) -> 'RobotResponse':
        """Create response with robot status."""
        return cls(
            success=True,
            message=message,
            timestamp=cls._current_timestamp(),
            robot_status=status
        )
    
    @staticmethod
    def _current_timestamp():
        from datetime import datetime
        return datetime.now().isoformat()