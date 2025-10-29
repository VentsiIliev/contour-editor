"""
Workpiece API models for workpiece management operations.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from .BaseModel import BaseModel, ApiRequest, ApiResponse


class WorkpieceStatus(Enum):
    """Workpiece processing status."""
    DRAFT = "draft"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Contour(BaseModel):
    """Geometric contour definition."""
    points: List[List[float]]  # List of [x, y] coordinates
    closed: bool = True
    
    def validate(self) -> bool:
        return len(self.points) >= 3 and all(len(p) == 2 for p in self.points)


@dataclass
class SprayPattern(BaseModel):
    """Spray pattern configuration."""
    contour_paths: List[Contour] = field(default_factory=list)
    fill_paths: List[Contour] = field(default_factory=list)
    spray_speed: float = 1.0
    spray_pressure: float = 1.0
    
    def validate(self) -> bool:
        return (all(c.validate() for c in self.contour_paths) and
                all(f.validate() for f in self.fill_paths) and
                0 < self.spray_speed <= 10 and
                0 < self.spray_pressure <= 10)


@dataclass
class WorkpieceMetadata(BaseModel):
    """Workpiece metadata and properties."""
    name: str
    description: Optional[str] = None
    material_type: Optional[str] = None
    thickness: float = 4.0
    dimensions: Optional[Dict[str, float]] = None
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    
    def validate(self) -> bool:
        return bool(self.name) and self.thickness > 0


@dataclass
class Workpiece(BaseModel):
    """Complete workpiece definition."""
    id: Optional[str] = None
    metadata: Optional[WorkpieceMetadata] = None
    external_contour: Optional[Contour] = None
    spray_pattern: Optional[SprayPattern] = None
    status: WorkpieceStatus = WorkpieceStatus.DRAFT
    contour_area: float = 0.0
    preview_image: Optional[str] = None  # Base64 encoded image
    
    def validate(self) -> bool:
        validations = [
            self.metadata is None or self.metadata.validate(),
            self.external_contour is None or self.external_contour.validate(),
            self.spray_pattern is None or self.spray_pattern.validate(),
            self.contour_area >= 0
        ]
        return all(validations)


@dataclass
class CreateWorkpieceRequest(ApiRequest):
    """Request to create workpiece from camera."""
    capture_new_image: bool = True
    detection_params: Optional[Dict[str, Any]] = None


@dataclass
class SaveWorkpieceRequest(ApiRequest):
    """Request to save workpiece."""
    workpiece: Workpiece
    
    def validate(self) -> bool:
        return self.workpiece.validate()


@dataclass
class WorkpieceFromDxfRequest(ApiRequest):
    """Request to create workpiece from DXF file."""
    dxf_file_path: str
    scale_factor: float = 1.0
    
    def validate(self) -> bool:
        return bool(self.dxf_file_path) and self.scale_factor > 0


@dataclass 
class WorkpieceListRequest(ApiRequest):
    """Request to list workpieces with filtering."""
    status_filter: Optional[WorkpieceStatus] = None
    limit: int = 50
    offset: int = 0
    
    def validate(self) -> bool:
        return 0 <= self.limit <= 1000 and self.offset >= 0


@dataclass
class ExecuteWorkpieceRequest(ApiRequest):
    """Request to execute workpiece production."""
    workpiece_id: str
    execution_params: Optional[Dict[str, Any]] = None
    
    def validate(self) -> bool:
        return bool(self.workpiece_id)


@dataclass
class WorkpieceResponse(ApiResponse):
    """Response containing workpiece data."""
    workpiece: Optional[Workpiece] = None
    workpieces: Optional[List[Workpiece]] = None
    total_count: Optional[int] = None
    
    @classmethod
    def single_workpiece(cls, workpiece: Workpiece, message: str = "Workpiece retrieved") -> 'WorkpieceResponse':
        """Create response for single workpiece."""
        return cls(
            success=True,
            message=message,
            timestamp=cls._current_timestamp(),
            workpiece=workpiece
        )
    
    @classmethod
    def workpiece_list(cls, workpieces: List[Workpiece], total_count: int,
                       message: str = "Workpieces retrieved") -> 'WorkpieceResponse':
        """Create response for workpiece list."""
        return cls(
            success=True,
            message=message,
            timestamp=cls._current_timestamp(),
            workpieces=workpieces,
            total_count=total_count
        )
    
    @staticmethod
    def _current_timestamp():
        from datetime import datetime
        return datetime.now().isoformat()


@dataclass
class WorkpieceCreationResponse(ApiResponse):
    """Response for workpiece creation with image and contours."""
    captured_image: Optional[str] = None  # Base64 encoded
    detected_contours: Optional[List[Contour]] = None
    processing_metadata: Optional[Dict[str, Any]] = None
    
    @classmethod
    def successful(cls, image: str, contours: List[Contour],
                   metadata: Optional[Dict] = None) -> 'WorkpieceCreationResponse':
        """Create successful creation response."""
        return cls(
            success=True,
            message="Workpiece created from camera capture",
            timestamp=cls._current_timestamp(),
            captured_image=image,
            detected_contours=contours,
            processing_metadata=metadata or {}
        )
    
    @staticmethod
    def _current_timestamp():
        from datetime import datetime
        return datetime.now().isoformat()