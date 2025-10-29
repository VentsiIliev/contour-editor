"""
RESTful endpoint registry for the industrial automation API.
Provides clean, semantic URLs with proper HTTP methods.
"""
from typing import Dict, Tuple
from enum import Enum
from ..constants.ApiEndpoints import ApiEndpoints, HttpMethod


class ApiEndpoint:
    """API endpoint definition."""
    
    def __init__(self, path: str, method: HttpMethod, description: str,
                 request_model=None, response_model=None):
        self.path = path
        self.method = method
        self.description = description
        self.request_model = request_model
        self.response_model = response_model
    
    def __str__(self):
        return f"{self.method.value} {self.path} - {self.description}"


class EndpointRegistry:
    """
    Registry of all API endpoints with semantic, RESTful URLs.
    
    This replaces the string-based routing system with proper REST semantics:
    - Resource-based URLs
    - Proper HTTP methods
    - Hierarchical structure
    - Consistent patterns
    """
    
    # Authentication endpoints
    AUTH_LOGIN = ApiEndpoint(
        ApiEndpoints.AUTH_LOGIN.path, 
        ApiEndpoints.AUTH_LOGIN.method, 
        ApiEndpoints.AUTH_LOGIN.description
    )
    
    AUTH_QR_LOGIN = ApiEndpoint(
        ApiEndpoints.AUTH_QR_LOGIN.path,
        ApiEndpoints.AUTH_QR_LOGIN.method,
        ApiEndpoints.AUTH_QR_LOGIN.description
    )
    
    AUTH_LOGOUT = ApiEndpoint(
        ApiEndpoints.AUTH_LOGOUT.path,
        ApiEndpoints.AUTH_LOGOUT.method,
        ApiEndpoints.AUTH_LOGOUT.description
    )
    
    AUTH_SESSION = ApiEndpoint(
        ApiEndpoints.AUTH_SESSION.path,
        ApiEndpoints.AUTH_SESSION.method,
        ApiEndpoints.AUTH_SESSION.description
    )
    
    # System endpoints
    SYSTEM_START = ApiEndpoint(
        ApiEndpoints.SYSTEM_START.path,
        ApiEndpoints.SYSTEM_START.method,
        ApiEndpoints.SYSTEM_START.description
    )
    
    SYSTEM_STOP = ApiEndpoint(
        ApiEndpoints.SYSTEM_STOP.path, 
        ApiEndpoints.SYSTEM_STOP.method,
        ApiEndpoints.SYSTEM_STOP.description
    )
    
    SYSTEM_STATUS = ApiEndpoint(
        ApiEndpoints.SYSTEM_STATUS.path,
        ApiEndpoints.SYSTEM_STATUS.method,
        ApiEndpoints.SYSTEM_STATUS.description
    )
    
    SYSTEM_TEST_RUN = ApiEndpoint(
        ApiEndpoints.SYSTEM_TEST_RUN.path,
        ApiEndpoints.SYSTEM_TEST_RUN.method,
        ApiEndpoints.SYSTEM_TEST_RUN.description
    )
    
    # Robot endpoints
    ROBOT_STATUS = ApiEndpoint(
        ApiEndpoints.ROBOT_STATUS.path,
        ApiEndpoints.ROBOT_STATUS.method,
        ApiEndpoints.ROBOT_STATUS.description
    )
    
    ROBOT_JOG = ApiEndpoint(
        ApiEndpoints.ROBOT_JOG.path,
        ApiEndpoints.ROBOT_JOG.method,
        ApiEndpoints.ROBOT_JOG.description
    )
    
    ROBOT_MOVE_POSITION = ApiEndpoint(
        ApiEndpoints.ROBOT_MOVE_POSITION.path,
        ApiEndpoints.ROBOT_MOVE_POSITION.method,
        ApiEndpoints.ROBOT_MOVE_POSITION.description
    )
    
    ROBOT_MOVE_COORDINATES = ApiEndpoint(
        ApiEndpoints.ROBOT_MOVE_COORDINATES.path,
        ApiEndpoints.ROBOT_MOVE_COORDINATES.method,
        ApiEndpoints.ROBOT_MOVE_COORDINATES.description
    )
    
    ROBOT_CALIBRATE = ApiEndpoint(
        ApiEndpoints.ROBOT_CALIBRATE.path,
        ApiEndpoints.ROBOT_CALIBRATE.method,
        ApiEndpoints.ROBOT_CALIBRATE.description
    )
    
    ROBOT_SAVE_CALIBRATION_POINT = ApiEndpoint(
        ApiEndpoints.ROBOT_CALIBRATION_POINTS.path,
        ApiEndpoints.ROBOT_CALIBRATION_POINTS.method,
        ApiEndpoints.ROBOT_CALIBRATION_POINTS.description
    )
    
    # Camera endpoints
    CAMERA_STATUS = ApiEndpoint(
        ApiEndpoints.CAMERA_STATUS.path,
        ApiEndpoints.CAMERA_STATUS.method,
        ApiEndpoints.CAMERA_STATUS.description
    )
    
    CAMERA_CAPTURE = ApiEndpoint(
        ApiEndpoints.CAMERA_CAPTURE.path,
        ApiEndpoints.CAMERA_CAPTURE.method,
        ApiEndpoints.CAMERA_CAPTURE.description
    )
    
    CAMERA_STREAM = ApiEndpoint(
        ApiEndpoints.CAMERA_STREAM.path,
        ApiEndpoints.CAMERA_STREAM.method,
        ApiEndpoints.CAMERA_STREAM.description
    )
    
    CAMERA_CALIBRATE = ApiEndpoint(
        ApiEndpoints.CAMERA_CALIBRATE.path,
        ApiEndpoints.CAMERA_CALIBRATE.method,
        ApiEndpoints.CAMERA_CALIBRATE.description
    )
    
    CAMERA_RAW_MODE = ApiEndpoint(
        ApiEndpoints.CAMERA_RAW_MODE.path,
        ApiEndpoints.CAMERA_RAW_MODE.method,
        ApiEndpoints.CAMERA_RAW_MODE.description
    )
    
    CAMERA_WORK_AREA = ApiEndpoint(
        ApiEndpoints.CAMERA_WORK_AREA.path,
        ApiEndpoints.CAMERA_WORK_AREA.method,
        ApiEndpoints.CAMERA_WORK_AREA.description
    )
    
    # Workpiece endpoints
    WORKPIECES_LIST = ApiEndpoint(
        ApiEndpoints.WORKPIECES_LIST.path,
        ApiEndpoints.WORKPIECES_LIST.method,
        ApiEndpoints.WORKPIECES_LIST.description
    )
    
    WORKPIECES_CREATE = ApiEndpoint(
        ApiEndpoints.WORKPIECES_CREATE.path,
        ApiEndpoints.WORKPIECES_CREATE.method,
        ApiEndpoints.WORKPIECES_CREATE.description
    )
    
    WORKPIECE_BY_ID = ApiEndpoint(
        ApiEndpoints.WORKPIECE_BY_ID.path,
        ApiEndpoints.WORKPIECE_BY_ID.method,
        ApiEndpoints.WORKPIECE_BY_ID.description
    )
    
    WORKPIECE_UPDATE = ApiEndpoint(
        ApiEndpoints.WORKPIECE_UPDATE.path,
        ApiEndpoints.WORKPIECE_UPDATE.method,
        ApiEndpoints.WORKPIECE_UPDATE.description
    )
    
    WORKPIECE_DELETE = ApiEndpoint(
        ApiEndpoints.WORKPIECE_DELETE.path,
        ApiEndpoints.WORKPIECE_DELETE.method,
        ApiEndpoints.WORKPIECE_DELETE.description
    )
    
    WORKPIECE_FROM_CAMERA = ApiEndpoint(
        ApiEndpoints.WORKPIECE_FROM_CAMERA.path,
        ApiEndpoints.WORKPIECE_FROM_CAMERA.method,
        ApiEndpoints.WORKPIECE_FROM_CAMERA.description
    )
    
    WORKPIECE_FROM_DXF = ApiEndpoint(
        ApiEndpoints.WORKPIECE_FROM_DXF.path,
        ApiEndpoints.WORKPIECE_FROM_DXF.method,
        ApiEndpoints.WORKPIECE_FROM_DXF.description
    )
    
    WORKPIECE_EXECUTE = ApiEndpoint(
        ApiEndpoints.WORKPIECE_EXECUTE.path,
        ApiEndpoints.WORKPIECE_EXECUTE.method,
        ApiEndpoints.WORKPIECE_EXECUTE.description
    )
    
    # Settings endpoints
    SETTINGS_ROBOT = ApiEndpoint(
        ApiEndpoints.SETTINGS_ROBOT_GET.path,
        ApiEndpoints.SETTINGS_ROBOT_GET.method,
        ApiEndpoints.SETTINGS_ROBOT_GET.description
    )
    
    SETTINGS_ROBOT_UPDATE = ApiEndpoint(
        ApiEndpoints.SETTINGS_ROBOT_UPDATE.path,
        ApiEndpoints.SETTINGS_ROBOT_UPDATE.method,
        ApiEndpoints.SETTINGS_ROBOT_UPDATE.description
    )
    
    SETTINGS_CAMERA = ApiEndpoint(
        ApiEndpoints.SETTINGS_CAMERA_GET.path,
        ApiEndpoints.SETTINGS_CAMERA_GET.method,
        ApiEndpoints.SETTINGS_CAMERA_GET.description
    )
    
    SETTINGS_CAMERA_UPDATE = ApiEndpoint(
        ApiEndpoints.SETTINGS_CAMERA_UPDATE.path,
        ApiEndpoints.SETTINGS_CAMERA_UPDATE.method,
        ApiEndpoints.SETTINGS_CAMERA_UPDATE.description
    )
    
    SETTINGS_GLUE = ApiEndpoint(
        ApiEndpoints.SETTINGS_GLUE_GET.path,
        ApiEndpoints.SETTINGS_GLUE_GET.method,
        ApiEndpoints.SETTINGS_GLUE_GET.description
    )
    
    SETTINGS_GLUE_UPDATE = ApiEndpoint(
        ApiEndpoints.SETTINGS_GLUE_UPDATE.path,
        ApiEndpoints.SETTINGS_GLUE_UPDATE.method,
        ApiEndpoints.SETTINGS_GLUE_UPDATE.description
    )
    
    @classmethod
    def get_all_endpoints(cls) -> Dict[str, ApiEndpoint]:
        """Get all registered endpoints."""
        endpoints = {}
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, ApiEndpoint):
                endpoints[attr_name] = attr
        return endpoints
    
    @classmethod
    def find_endpoint(cls, path: str, method: HttpMethod) -> Tuple[str, ApiEndpoint]:
        """Find endpoint by path and method."""
        for name, endpoint in cls.get_all_endpoints().items():
            if endpoint.path == path and endpoint.method == method:
                return name, endpoint
        return None, None
    
    @classmethod
    def get_endpoint_by_name(cls, name: str) -> ApiEndpoint:
        """Get endpoint by name."""
        return getattr(cls, name, None)


# Legacy compatibility mapping - now uses centralized constants
from ..constants.ApiEndpoints import LEGACY_ENDPOINT_MAPPING
LEGACY_TO_V2_MAPPING = LEGACY_ENDPOINT_MAPPING


def get_v2_endpoint(legacy_path: str) -> ApiEndpoint:
    """Convert legacy endpoint to v2 endpoint."""
    return LEGACY_TO_V2_MAPPING.get(legacy_path)


if __name__ == "__main__":
    # Example usage and endpoint listing
    print("Industrial Automation API v2 Endpoints:")
    print("=" * 50)
    
    endpoints = EndpointRegistry.get_all_endpoints()
    
    # Group by resource
    groups = {}
    for name, endpoint in endpoints.items():
        resource = endpoint.path.split('/')[3] if len(endpoint.path.split('/')) > 3 else 'system'
        if resource not in groups:
            groups[resource] = []
        groups[resource].append((name, endpoint))
    
    for resource, endpoint_list in sorted(groups.items()):
        print(f"\n{resource.upper()} Endpoints:")
        print("-" * 30)
        for name, endpoint in sorted(endpoint_list):
            print(f"  {endpoint.method.value:6} {endpoint.path:35} - {endpoint.description}")
    
    print(f"\nTotal endpoints: {len(endpoints)}")
    print(f"Legacy mappings: {len(LEGACY_TO_V2_MAPPING)}")