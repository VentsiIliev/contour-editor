"""
Centralized API endpoint constants and utilities.
Eliminates scattered endpoint strings throughout the codebase.
"""
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass


class HttpMethod(Enum):
    """HTTP methods enum for type safety."""
    GET = "GET"
    POST = "POST" 
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


@dataclass(frozen=True)
class Endpoint:
    """Immutable endpoint definition with metadata."""
    path: str
    method: HttpMethod
    description: str
    requires_auth: bool = True
    rate_limited: bool = True
    
    @property
    def full_url(self) -> str:
        """Get full URL path."""
        return self.path
    
    @property
    def method_str(self) -> str:
        """Get HTTP method as string."""
        return self.method.value
    
    def build_url(self, **params) -> str:
        """Build URL with path parameters."""
        url = self.path
        for key, value in params.items():
            url = url.replace(f"{{{key}}}", str(value))
        return url


class ApiEndpoints:
    """
    Centralized repository of all API endpoints.
    
    Benefits:
    - Single source of truth for all endpoints
    - Type-safe endpoint definitions
    - Prevents typos and inconsistencies
    - Easy to maintain and update
    - Auto-completion in IDEs
    """
    
    # ============================================================================
    # AUTHENTICATION ENDPOINTS
    # ============================================================================
    
    AUTH_LOGIN = Endpoint(
        path="/api/v2/auth/login",
        method=HttpMethod.POST,
        description="User login with credentials",
        requires_auth=False
    )
    
    AUTH_QR_LOGIN = Endpoint(
        path="/api/v2/auth/qr-login",
        method=HttpMethod.POST,
        description="User login with QR code",
        requires_auth=False
    )
    
    AUTH_LOGOUT = Endpoint(
        path="/api/v2/auth/logout",
        method=HttpMethod.POST,
        description="User logout"
    )
    
    AUTH_SESSION = Endpoint(
        path="/api/v2/auth/session",
        method=HttpMethod.GET,
        description="Get current session information"
    )
    
    AUTH_REFRESH = Endpoint(
        path="/api/v2/auth/refresh",
        method=HttpMethod.POST,
        description="Refresh authentication token"
    )
    
    # ============================================================================
    # SYSTEM ENDPOINTS
    # ============================================================================
    
    SYSTEM_START = Endpoint(
        path="/api/v2/system/start",
        method=HttpMethod.POST,
        description="Start system operations"
    )
    
    SYSTEM_STOP = Endpoint(
        path="/api/v2/system/stop",
        method=HttpMethod.POST,
        description="Stop system operations"
    )
    
    SYSTEM_STATUS = Endpoint(
        path="/api/v2/system/status",
        method=HttpMethod.GET,
        description="Get current system status",
        rate_limited=False
    )
    
    SYSTEM_TEST_RUN = Endpoint(
        path="/api/v2/system/test",
        method=HttpMethod.POST,
        description="Execute system test run"
    )
    
    SYSTEM_EMERGENCY_STOP = Endpoint(
        path="/api/v2/system/emergency-stop",
        method=HttpMethod.POST,
        description="Emergency system shutdown",
        rate_limited=False
    )
    
    # ============================================================================
    # ROBOT ENDPOINTS
    # ============================================================================
    
    ROBOT_STATUS = Endpoint(
        path="/api/v2/robot/status",
        method=HttpMethod.GET,
        description="Get robot status and current position",
        rate_limited=False
    )
    
    ROBOT_JOG = Endpoint(
        path="/api/v2/robot/jog",
        method=HttpMethod.POST,
        description="Jog robot in specified axis and direction"
    )
    
    ROBOT_MOVE_POSITION = Endpoint(
        path="/api/v2/robot/move/position",
        method=HttpMethod.POST,
        description="Move robot to predefined position"
    )
    
    ROBOT_MOVE_COORDINATES = Endpoint(
        path="/api/v2/robot/move/coordinates",
        method=HttpMethod.POST,
        description="Move robot to specific coordinates"
    )
    
    ROBOT_STOP = Endpoint(
        path="/api/v2/robot/stop",
        method=HttpMethod.POST,
        description="Stop robot movement immediately",
        rate_limited=False
    )
    
    ROBOT_CALIBRATE = Endpoint(
        path="/api/v2/robot/calibration",
        method=HttpMethod.POST,
        description="Perform robot calibration"
    )
    
    ROBOT_CALIBRATION_POINTS = Endpoint(
        path="/api/v2/robot/calibration/points",
        method=HttpMethod.POST,
        description="Save robot calibration points"
    )
    
    ROBOT_PICKUP_AREA = Endpoint(
        path="/api/v2/robot/calibration/pickup-area",
        method=HttpMethod.POST,
        description="Calibrate pickup area"
    )
    
    # ============================================================================
    # CAMERA ENDPOINTS
    # ============================================================================
    
    CAMERA_STATUS = Endpoint(
        path="/api/v2/camera/status",
        method=HttpMethod.GET,
        description="Get camera status and settings",
        rate_limited=False
    )
    
    CAMERA_CAPTURE = Endpoint(
        path="/api/v2/camera/capture",
        method=HttpMethod.POST,
        description="Capture image from camera"
    )
    
    CAMERA_STREAM = Endpoint(
        path="/api/v2/camera/stream",
        method=HttpMethod.GET,
        description="Get latest camera frame",
        rate_limited=False
    )
    
    CAMERA_CALIBRATE = Endpoint(
        path="/api/v2/camera/calibration",
        method=HttpMethod.POST,
        description="Perform camera calibration"
    )
    
    CAMERA_TEST_CALIBRATION = Endpoint(
        path="/api/v2/camera/calibration/test",
        method=HttpMethod.POST,
        description="Test camera calibration"
    )
    
    CAMERA_RAW_MODE = Endpoint(
        path="/api/v2/camera/raw-mode",
        method=HttpMethod.PUT,
        description="Toggle camera raw mode on/off"
    )
    
    CAMERA_WORK_AREA = Endpoint(
        path="/api/v2/camera/work-area",
        method=HttpMethod.POST,
        description="Set camera work area points"
    )
    
    CAMERA_STOP_CONTOUR_DETECTION = Endpoint(
        path="/api/v2/camera/stop-contour-detection",
        method=HttpMethod.POST,
        description="Stop camera contour detection",
        requires_auth=True,
        rate_limited=True
    )
    
    # ============================================================================
    # WORKPIECE ENDPOINTS
    # ============================================================================
    
    WORKPIECES_LIST = Endpoint(
        path="/api/v2/workpieces",
        method=HttpMethod.GET,
        description="Get list of workpieces with optional filtering"
    )
    
    WORKPIECES_CREATE = Endpoint(
        path="/api/v2/workpieces",
        method=HttpMethod.POST,
        description="Create new workpiece"
    )
    
    WORKPIECE_BY_ID = Endpoint(
        path="/api/v2/workpieces/{id}",
        method=HttpMethod.GET,
        description="Get specific workpiece by ID"
    )
    
    WORKPIECE_UPDATE = Endpoint(
        path="/api/v2/workpieces/{id}",
        method=HttpMethod.PUT,
        description="Update existing workpiece"
    )
    
    WORKPIECE_DELETE = Endpoint(
        path="/api/v2/workpieces/{id}",
        method=HttpMethod.DELETE,
        description="Delete workpiece"
    )
    
    WORKPIECE_FROM_CAMERA = Endpoint(
        path="/api/v2/workpieces/create/camera",
        method=HttpMethod.POST,
        description="Create workpiece from camera capture"
    )
    
    WORKPIECE_FROM_DXF = Endpoint(
        path="/api/v2/workpieces/create/dxf",
        method=HttpMethod.POST,
        description="Create workpiece from DXF file upload"
    )
    
    WORKPIECE_EXECUTE = Endpoint(
        path="/api/v2/workpieces/{id}/execute",
        method=HttpMethod.POST,
        description="Execute workpiece production"
    )
    
    # ============================================================================
    # SETTINGS ENDPOINTS
    # ============================================================================
    
    SETTINGS_ROBOT_GET = Endpoint(
        path="/api/v2/settings/robot",
        method=HttpMethod.GET,
        description="Get robot configuration settings"
    )
    
    SETTINGS_ROBOT_UPDATE = Endpoint(
        path="/api/v2/settings/robot",
        method=HttpMethod.PUT,
        description="Update robot configuration settings"
    )
    
    SETTINGS_CAMERA_GET = Endpoint(
        path="/api/v2/settings/camera",
        method=HttpMethod.GET,
        description="Get camera configuration settings"
    )
    
    SETTINGS_CAMERA_UPDATE = Endpoint(
        path="/api/v2/settings/camera",
        method=HttpMethod.PUT,
        description="Update camera configuration settings"
    )
    
    SETTINGS_GLUE_GET = Endpoint(
        path="/api/v2/settings/glue",
        method=HttpMethod.GET,
        description="Get glue dispensing settings"
    )
    
    SETTINGS_GLUE_UPDATE = Endpoint(
        path="/api/v2/settings/glue",
        method=HttpMethod.PUT,
        description="Update glue dispensing settings"
    )
    
    # ============================================================================
    # GLUE SYSTEM ENDPOINTS
    # ============================================================================
    
    GLUE_STATUS = Endpoint(
        path="/api/v2/glue/status",
        method=HttpMethod.GET,
        description="Get glue system status and readings",
        rate_limited=False
    )
    
    GLUE_PRIME = Endpoint(
        path="/api/v2/glue/prime",
        method=HttpMethod.POST,
        description="Prime glue dispensing system"
    )
    
    GLUE_DISPENSE_START = Endpoint(
        path="/api/v2/glue/dispense/start",
        method=HttpMethod.POST,
        description="Start glue dispensing"
    )
    
    GLUE_DISPENSE_STOP = Endpoint(
        path="/api/v2/glue/dispense/stop",
        method=HttpMethod.POST,
        description="Stop glue dispensing"
    )
    
    GLUE_PURGE = Endpoint(
        path="/api/v2/glue/purge",
        method=HttpMethod.POST,
        description="Purge glue system"
    )
    
    GLUE_PRESSURE_GET = Endpoint(
        path="/api/v2/glue/pressure",
        method=HttpMethod.GET,
        description="Get glue system pressure readings",
        rate_limited=False
    )
    
    GLUE_PRESSURE_SET = Endpoint(
        path="/api/v2/glue/pressure/set",
        method=HttpMethod.POST,
        description="Set glue system pressure"
    )
    
    GLUE_TEMPERATURE = Endpoint(
        path="/api/v2/glue/temperature",
        method=HttpMethod.GET,
        description="Get glue system temperature",
        rate_limited=False
    )
    
    GLUE_NOZZLE_CHANGE = Endpoint(
        path="/api/v2/glue/nozzle/change",
        method=HttpMethod.POST,
        description="Change glue nozzle"
    )
    
    GLUE_NOZZLE_STATUS = Endpoint(
        path="/api/v2/glue/nozzle/status",
        method=HttpMethod.GET,
        description="Get current nozzle status",
        rate_limited=False
    )
    
    GLUE_CALIBRATE = Endpoint(
        path="/api/v2/glue/calibrate",
        method=HttpMethod.POST,
        description="Calibrate glue dispenser"
    )
    
    GLUE_TEST_PATTERN = Endpoint(
        path="/api/v2/glue/test-pattern",
        method=HttpMethod.POST,
        description="Execute test spray pattern"
    )
    
    GLUE_FLOW_RATE_GET = Endpoint(
        path="/api/v2/glue/flow-rate",
        method=HttpMethod.GET,
        description="Get glue flow rate",
        rate_limited=False
    )
    
    GLUE_FLOW_RATE_SET = Endpoint(
        path="/api/v2/glue/flow-rate/set",
        method=HttpMethod.POST,
        description="Set glue flow rate"
    )
    
    GLUE_MAINTENANCE = Endpoint(
        path="/api/v2/glue/maintenance",
        method=HttpMethod.POST,
        description="Perform glue system maintenance operations"
    )
    
    # ============================================================================
    # STATISTICS ENDPOINTS
    # ============================================================================
    
    STATS_ALL = Endpoint(
        path="/api/v2/stats/all",
        method=HttpMethod.GET,
        description="Get all system statistics",
        rate_limited=False
    )
    
    STATS_GENERATOR = Endpoint(
        path="/api/v2/stats/generator",
        method=HttpMethod.GET,
        description="Get generator statistics",
        rate_limited=False
    )
    
    STATS_TRANSDUCER = Endpoint(
        path="/api/v2/stats/transducer", 
        method=HttpMethod.GET,
        description="Get transducer statistics",
        rate_limited=False
    )
    
    STATS_PUMPS = Endpoint(
        path="/api/v2/stats/pumps",
        method=HttpMethod.GET,
        description="Get all pump statistics",
        rate_limited=False
    )
    
    STATS_PUMP_BY_ID = Endpoint(
        path="/api/v2/stats/pumps/{pump_id}",
        method=HttpMethod.GET,
        description="Get specific pump statistics by ID",
        rate_limited=False
    )
    
    STATS_FAN = Endpoint(
        path="/api/v2/stats/fan",
        method=HttpMethod.GET,
        description="Get fan statistics", 
        rate_limited=False
    )
    
    STATS_LOADCELLS = Endpoint(
        path="/api/v2/stats/loadcells",
        method=HttpMethod.GET,
        description="Get all loadcell statistics",
        rate_limited=False
    )
    
    STATS_LOADCELL_BY_ID = Endpoint(
        path="/api/v2/stats/loadcells/{loadcell_id}",
        method=HttpMethod.GET,
        description="Get specific loadcell statistics by ID",
        rate_limited=False
    )
    
    RESET_ALL_STATS = Endpoint(
        path="/api/v2/stats/reset/all",
        method=HttpMethod.POST,
        description="Reset all system statistics"
    )
    
    RESET_GENERATOR = Endpoint(
        path="/api/v2/stats/reset/generator",
        method=HttpMethod.POST,
        description="Reset generator statistics"
    )
    
    RESET_TRANSDUCER = Endpoint(
        path="/api/v2/stats/reset/transducer",
        method=HttpMethod.POST,
        description="Reset transducer statistics"
    )
    
    RESET_FAN = Endpoint(
        path="/api/v2/stats/reset/fan",
        method=HttpMethod.POST,
        description="Reset fan statistics"
    )
    
    RESET_PUMP_MOTOR = Endpoint(
        path="/api/v2/stats/reset/pumps/{pump_id}/motor",
        method=HttpMethod.POST,
        description="Reset specific pump motor statistics"
    )
    
    RESET_PUMP_BELT = Endpoint(
        path="/api/v2/stats/reset/pumps/{pump_id}/belt",
        method=HttpMethod.POST,
        description="Reset specific pump belt statistics"
    )
    
    RESET_LOADCELL = Endpoint(
        path="/api/v2/stats/reset/loadcells/{loadcell_id}",
        method=HttpMethod.POST,
        description="Reset specific loadcell statistics"
    )
    
    STATS_EXPORT_CSV = Endpoint(
        path="/api/v2/stats/export/csv",
        method=HttpMethod.POST,
        description="Export statistics data as CSV"
    )
    
    STATS_EXPORT_JSON = Endpoint(
        path="/api/v2/stats/export/json", 
        method=HttpMethod.POST,
        description="Export statistics data as JSON"
    )
    
    STATS_REPORT_DAILY = Endpoint(
        path="/api/v2/stats/reports/daily",
        method=HttpMethod.GET,
        description="Get daily statistics report",
        rate_limited=False
    )
    
    STATS_REPORT_WEEKLY = Endpoint(
        path="/api/v2/stats/reports/weekly",
        method=HttpMethod.GET,
        description="Get weekly statistics report",
        rate_limited=False
    )
    
    STATS_REPORT_MONTHLY = Endpoint(
        path="/api/v2/stats/reports/monthly",
        method=HttpMethod.GET,
        description="Get monthly statistics report",
        rate_limited=False
    )


class EndpointGroups:
    """Logical grouping of endpoints for easier organization."""
    
    AUTHENTICATION = [
        ApiEndpoints.AUTH_LOGIN,
        ApiEndpoints.AUTH_QR_LOGIN,
        ApiEndpoints.AUTH_LOGOUT,
        ApiEndpoints.AUTH_SESSION,
        ApiEndpoints.AUTH_REFRESH,
    ]
    
    SYSTEM = [
        ApiEndpoints.SYSTEM_START,
        ApiEndpoints.SYSTEM_STOP,
        ApiEndpoints.SYSTEM_STATUS,
        ApiEndpoints.SYSTEM_TEST_RUN,
        ApiEndpoints.SYSTEM_EMERGENCY_STOP,
    ]
    
    ROBOT = [
        ApiEndpoints.ROBOT_STATUS,
        ApiEndpoints.ROBOT_JOG,
        ApiEndpoints.ROBOT_MOVE_POSITION,
        ApiEndpoints.ROBOT_MOVE_COORDINATES,
        ApiEndpoints.ROBOT_STOP,
        ApiEndpoints.ROBOT_CALIBRATE,
        ApiEndpoints.ROBOT_CALIBRATION_POINTS,
        ApiEndpoints.ROBOT_PICKUP_AREA,
    ]
    
    CAMERA = [
        ApiEndpoints.CAMERA_STATUS,
        ApiEndpoints.CAMERA_CAPTURE,
        ApiEndpoints.CAMERA_STREAM,
        ApiEndpoints.CAMERA_CALIBRATE,
        ApiEndpoints.CAMERA_TEST_CALIBRATION,
        ApiEndpoints.CAMERA_RAW_MODE,
        ApiEndpoints.CAMERA_WORK_AREA,
        ApiEndpoints.CAMERA_STOP_CONTOUR_DETECTION,
    ]
    
    WORKPIECES = [
        ApiEndpoints.WORKPIECES_LIST,
        ApiEndpoints.WORKPIECES_CREATE,
        ApiEndpoints.WORKPIECE_BY_ID,
        ApiEndpoints.WORKPIECE_UPDATE,
        ApiEndpoints.WORKPIECE_DELETE,
        ApiEndpoints.WORKPIECE_FROM_CAMERA,
        ApiEndpoints.WORKPIECE_FROM_DXF,
        ApiEndpoints.WORKPIECE_EXECUTE,
    ]
    
    SETTINGS = [
        ApiEndpoints.SETTINGS_ROBOT_GET,
        ApiEndpoints.SETTINGS_ROBOT_UPDATE,
        ApiEndpoints.SETTINGS_CAMERA_GET,
        ApiEndpoints.SETTINGS_CAMERA_UPDATE,
        ApiEndpoints.SETTINGS_GLUE_GET,
        ApiEndpoints.SETTINGS_GLUE_UPDATE,
    ]
    
    GLUE = [
        ApiEndpoints.GLUE_STATUS,
        ApiEndpoints.GLUE_PRIME,
        ApiEndpoints.GLUE_DISPENSE_START,
        ApiEndpoints.GLUE_DISPENSE_STOP,
        ApiEndpoints.GLUE_PURGE,
        ApiEndpoints.GLUE_PRESSURE_GET,
        ApiEndpoints.GLUE_PRESSURE_SET,
        ApiEndpoints.GLUE_TEMPERATURE,
        ApiEndpoints.GLUE_NOZZLE_CHANGE,
        ApiEndpoints.GLUE_NOZZLE_STATUS,
        ApiEndpoints.GLUE_CALIBRATE,
        ApiEndpoints.GLUE_TEST_PATTERN,
        ApiEndpoints.GLUE_FLOW_RATE_GET,
        ApiEndpoints.GLUE_FLOW_RATE_SET,
        ApiEndpoints.GLUE_MAINTENANCE,
    ]
    
    STATISTICS = [
        ApiEndpoints.STATS_ALL,
        ApiEndpoints.STATS_GENERATOR,
        ApiEndpoints.STATS_TRANSDUCER,
        ApiEndpoints.STATS_PUMPS,
        ApiEndpoints.STATS_PUMP_BY_ID,
        ApiEndpoints.STATS_FAN,
        ApiEndpoints.STATS_LOADCELLS,
        ApiEndpoints.STATS_LOADCELL_BY_ID,
        ApiEndpoints.RESET_ALL_STATS,
        ApiEndpoints.RESET_GENERATOR,
        ApiEndpoints.RESET_TRANSDUCER,
        ApiEndpoints.RESET_FAN,
        ApiEndpoints.RESET_PUMP_MOTOR,
        ApiEndpoints.RESET_PUMP_BELT,
        ApiEndpoints.RESET_LOADCELL,
        ApiEndpoints.STATS_EXPORT_CSV,
        ApiEndpoints.STATS_EXPORT_JSON,
        ApiEndpoints.STATS_REPORT_DAILY,
        ApiEndpoints.STATS_REPORT_WEEKLY,
        ApiEndpoints.STATS_REPORT_MONTHLY,
    ]
    
    @classmethod
    def get_all_endpoints(cls) -> List[Endpoint]:
        """Get all endpoints from all groups."""
        all_endpoints = []
        for group_name in dir(cls):
            if not group_name.startswith('_') and group_name != 'get_all_endpoints':
                group = getattr(cls, group_name)
                if isinstance(group, list):
                    all_endpoints.extend(group)
        return all_endpoints
    
    @classmethod
    def get_public_endpoints(cls) -> List[Endpoint]:
        """Get endpoints that don't require authentication."""
        return [ep for ep in cls.get_all_endpoints() if not ep.requires_auth]
    
    @classmethod
    def get_rate_limited_endpoints(cls) -> List[Endpoint]:
        """Get endpoints that are rate limited."""
        return [ep for ep in cls.get_all_endpoints() if ep.rate_limited]


class EndpointBuilder:
    """Utility class for building endpoint URLs with parameters."""
    
    @staticmethod
    def build_workpiece_url(endpoint: Endpoint, workpiece_id: int) -> str:
        """Build workpiece-specific URL."""
        return endpoint.build_url(id=workpiece_id)
    
    @staticmethod
    def build_url_with_params(endpoint: Endpoint, **params) -> str:
        """Build URL with arbitrary parameters."""
        return endpoint.build_url(**params)
    
    @staticmethod
    def get_base_path(endpoint: Endpoint) -> str:
        """Extract base path without parameters."""
        import re
        return re.sub(r'/\{[^}]+\}', '', endpoint.path)


# Legacy compatibility mapping
LEGACY_ENDPOINT_MAPPING = {
    # Authentication
    "login": ApiEndpoints.AUTH_LOGIN,
    "camera/login": ApiEndpoints.AUTH_QR_LOGIN,
    "logout": ApiEndpoints.AUTH_LOGOUT,
    
    # System
    "start": ApiEndpoints.SYSTEM_START,
    "stop": ApiEndpoints.SYSTEM_STOP,
    "status": ApiEndpoints.SYSTEM_STATUS,
    "test_run": ApiEndpoints.SYSTEM_TEST_RUN,
    "emergency_stop": ApiEndpoints.SYSTEM_EMERGENCY_STOP,
    
    # Robot
    "robot/status": ApiEndpoints.ROBOT_STATUS,
    "robot/jog": ApiEndpoints.ROBOT_JOG,
    "robot/move/home": ApiEndpoints.ROBOT_MOVE_POSITION,
    "robot/move/calibPos": ApiEndpoints.ROBOT_MOVE_POSITION,
    "robot/move/login": ApiEndpoints.ROBOT_MOVE_POSITION,
    "robot/coordinates": ApiEndpoints.ROBOT_MOVE_COORDINATES,
    "robot/stop": ApiEndpoints.ROBOT_STOP,
    "robot/calibrate": ApiEndpoints.ROBOT_CALIBRATE,
    "robot/savePoint": ApiEndpoints.ROBOT_CALIBRATION_POINTS,
    "robot/pickupArea": ApiEndpoints.ROBOT_PICKUP_AREA,
    
    # Camera  
    "camera/status": ApiEndpoints.CAMERA_STATUS,
    "camera/capture": ApiEndpoints.CAMERA_CAPTURE,
    "camera/getLatestFrame": ApiEndpoints.CAMERA_STREAM,
    "camera/calibrate": ApiEndpoints.CAMERA_CALIBRATE,
    "camera/testCalibration": ApiEndpoints.CAMERA_TEST_CALIBRATION,
    "camera/rawModeOn": ApiEndpoints.CAMERA_RAW_MODE,
    "camera/rawModeOff": ApiEndpoints.CAMERA_RAW_MODE,
    "camera/saveWorkAreaPoints": ApiEndpoints.CAMERA_WORK_AREA,
    "camera/STOP_CONTOUR_DETECTION": ApiEndpoints.CAMERA_STOP_CONTOUR_DETECTION,
    
    # Workpieces
    "workpiece/list": ApiEndpoints.WORKPIECES_LIST,
    "workpiece/create": ApiEndpoints.WORKPIECE_FROM_CAMERA,
    "workpiece/save": ApiEndpoints.WORKPIECES_CREATE,
    "workpiece/get": ApiEndpoints.WORKPIECE_BY_ID,
    "workpiece/update": ApiEndpoints.WORKPIECE_UPDATE,
    "workpiece/delete": ApiEndpoints.WORKPIECE_DELETE,
    "workpiece/dxf": ApiEndpoints.WORKPIECE_FROM_DXF,
    "workpiece/execute": ApiEndpoints.WORKPIECE_EXECUTE,
    "workpiece/getall": ApiEndpoints.WORKPIECES_LIST,
    
    # Settings
    "settings/robot/get": ApiEndpoints.SETTINGS_ROBOT_GET,
    "settings/robot/set": ApiEndpoints.SETTINGS_ROBOT_UPDATE,
    "settings/camera/get": ApiEndpoints.SETTINGS_CAMERA_GET,
    "settings/camera/set": ApiEndpoints.SETTINGS_CAMERA_UPDATE,
    "settings/glue/get": ApiEndpoints.SETTINGS_GLUE_GET,
    "settings/glue/set": ApiEndpoints.SETTINGS_GLUE_UPDATE,
    
    # Glue system
    "glue/status": ApiEndpoints.GLUE_STATUS,
    "glue/prime": ApiEndpoints.GLUE_PRIME,
    "glue/start": ApiEndpoints.GLUE_DISPENSE_START,
    "glue/stop": ApiEndpoints.GLUE_DISPENSE_STOP,
    "glue/purge": ApiEndpoints.GLUE_PURGE,
    "glue/pressure": ApiEndpoints.GLUE_PRESSURE_GET,
    "glue/setPressure": ApiEndpoints.GLUE_PRESSURE_SET,
    "glue/temperature": ApiEndpoints.GLUE_TEMPERATURE,
    "glue/changeNozzle": ApiEndpoints.GLUE_NOZZLE_CHANGE,
    "glue/nozzleStatus": ApiEndpoints.GLUE_NOZZLE_STATUS,
    "glue/calibrate": ApiEndpoints.GLUE_CALIBRATE,
    "glue/testPattern": ApiEndpoints.GLUE_TEST_PATTERN,
    "glue/flowRate": ApiEndpoints.GLUE_FLOW_RATE_GET,
    "glue/setFlowRate": ApiEndpoints.GLUE_FLOW_RATE_SET,
    "glue/maintenance": ApiEndpoints.GLUE_MAINTENANCE,
    
    # Statistics
    "stats/all": ApiEndpoints.STATS_ALL,
    "stats/generator": ApiEndpoints.STATS_GENERATOR,
    "stats/transducer": ApiEndpoints.STATS_TRANSDUCER,
    "stats/pumps": ApiEndpoints.STATS_PUMPS,
    "stats/fan": ApiEndpoints.STATS_FAN,
    "stats/loadcells": ApiEndpoints.STATS_LOADCELLS,
    "reset/all": ApiEndpoints.RESET_ALL_STATS,
    "reset/generator": ApiEndpoints.RESET_GENERATOR,
    "reset/transducer": ApiEndpoints.RESET_TRANSDUCER,
    "reset/fan": ApiEndpoints.RESET_FAN,
    "stats/export/csv": ApiEndpoints.STATS_EXPORT_CSV,
    "stats/export/json": ApiEndpoints.STATS_EXPORT_JSON,
    "stats/reports/daily": ApiEndpoints.STATS_REPORT_DAILY,
    "stats/reports/weekly": ApiEndpoints.STATS_REPORT_WEEKLY,
    "stats/reports/monthly": ApiEndpoints.STATS_REPORT_MONTHLY,
}


def get_endpoint_by_legacy_path(legacy_path: str) -> Optional[Endpoint]:
    """Convert legacy endpoint path to v2 endpoint."""
    return LEGACY_ENDPOINT_MAPPING.get(legacy_path)


def validate_endpoint_coverage() -> Dict[str, any]:
    """Validate that all endpoints are properly defined and mapped."""
    all_endpoints = EndpointGroups.get_all_endpoints()
    legacy_mapped = set(LEGACY_ENDPOINT_MAPPING.values())
    
    return {
        "total_endpoints": len(all_endpoints),
        "legacy_mappings": len(LEGACY_ENDPOINT_MAPPING),
        "unmapped_endpoints": [ep for ep in all_endpoints if ep not in legacy_mapped],
        "public_endpoints": len(EndpointGroups.get_public_endpoints()),
        "rate_limited_endpoints": len(EndpointGroups.get_rate_limited_endpoints()),
    }


if __name__ == "__main__":
    # Demo usage and validation
    print("🏭 Industrial Automation API v2 Endpoints")
    print("=" * 50)
    
    # Show endpoint groups
    for group_name in ['AUTHENTICATION', 'SYSTEM', 'ROBOT', 'CAMERA', 'WORKPIECES', 'SETTINGS', 'GLUE']:
        group = getattr(EndpointGroups, group_name)
        print(f"\n{group_name} ({len(group)} endpoints):")
        print("-" * 30)
        for ep in group[:3]:  # Show first 3 of each group
            print(f"  {ep.method_str:6} {ep.path:35} - {ep.description}")
        if len(group) > 3:
            print(f"  ... and {len(group) - 3} more")
    
    # Show validation results
    validation = validate_endpoint_coverage()
    print(f"\n📊 Validation Results:")
    print(f"  Total endpoints: {validation['total_endpoints']}")
    print(f"  Legacy mappings: {validation['legacy_mappings']}")
    print(f"  Public endpoints: {validation['public_endpoints']}")
    print(f"  Rate limited: {validation['rate_limited_endpoints']}")
    
    # Demo endpoint building
    print(f"\n🔨 Endpoint Building Demo:")
    workpiece_url = EndpointBuilder.build_workpiece_url(ApiEndpoints.WORKPIECE_BY_ID, 123)
    print(f"  Workpiece URL: {workpiece_url}")
    
    execute_url = EndpointBuilder.build_workpiece_url(ApiEndpoints.WORKPIECE_EXECUTE, 456)
    print(f"  Execute URL: {execute_url}")