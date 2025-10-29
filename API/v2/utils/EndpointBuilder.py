"""
Type-safe endpoint builders for parameterized URLs and request construction.
Provides utilities for building endpoint URLs with parameters and request objects.
"""
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from ..constants.ApiEndpoints import ApiEndpoints, HttpMethod, Endpoint
from ..models.BaseModel import BaseModel


@dataclass
class RequestContext:
    """Context information for API requests."""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    user_id: Optional[str] = None
    session_token: Optional[str] = None


class EndpointBuilder:
    """
    Type-safe endpoint builder for constructing parameterized URLs and requests.
    
    Features:
    - Parameter substitution with validation
    - Query string building
    - Request context injection
    - Type-safe request construction
    - URL validation
    """
    
    def __init__(self, context: Optional[RequestContext] = None):
        """Initialize builder with optional context."""
        self.context = context or RequestContext()
    
    def build_url(self, endpoint: Endpoint, path_params: Optional[Dict[str, Union[str, int]]] = None, 
                  query_params: Optional[Dict[str, Any]] = None) -> str:
        """
        Build complete URL with path and query parameters.
        
        Args:
            endpoint: Endpoint definition
            path_params: Parameters to substitute in path (e.g., {'id': '123'})
            query_params: Query string parameters
            
        Returns:
            Complete URL string
            
        Raises:
            ValueError: If required path parameters are missing
        """
        url = endpoint.path
        
        # Substitute path parameters
        if path_params:
            for param_name, param_value in path_params.items():
                placeholder = f"{{{param_name}}}"
                if placeholder not in url:
                    raise ValueError(f"Parameter '{param_name}' not found in path '{url}'")
                url = url.replace(placeholder, str(param_value))
        
        # Check for unsubstituted parameters
        if '{' in url and '}' in url:
            import re
            missing_params = re.findall(r'\{([^}]+)\}', url)
            raise ValueError(f"Missing required path parameters: {missing_params}")
        
        # Add query parameters
        if query_params:
            query_parts = []
            for key, value in query_params.items():
                if isinstance(value, list):
                    for item in value:
                        query_parts.append(f"{key}={self._encode_param(item)}")
                elif value is not None:
                    query_parts.append(f"{key}={self._encode_param(value)}")
            
            if query_parts:
                url += "?" + "&".join(query_parts)
        
        return url
    
    def build_request(self, endpoint: Endpoint, data: Optional[Union[BaseModel, Dict[str, Any]]] = None,
                     path_params: Optional[Dict[str, Union[str, int]]] = None,
                     query_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Build complete API request with URL, method, and data.
        
        Args:
            endpoint: Endpoint definition
            data: Request data (model or dict)
            path_params: URL path parameters
            query_params: URL query parameters
            
        Returns:
            Dictionary with 'url', 'method', and 'data' keys
        """
        url = self.build_url(endpoint, path_params, query_params)
        
        # Prepare request data
        request_data = {}
        
        if data:
            if isinstance(data, BaseModel):
                request_data = data.to_dict()
            elif isinstance(data, dict):
                request_data = data.copy()
        
        # Inject context if not already present
        if 'request_id' not in request_data:
            request_data['request_id'] = self.context.request_id
        if 'timestamp' not in request_data:
            request_data['timestamp'] = self.context.timestamp
        
        # Add authentication context if available
        if self.context.user_id and 'user_id' not in request_data:
            request_data['user_id'] = self.context.user_id
        
        return {
            'url': url,
            'method': endpoint.method.value,
            'data': request_data if request_data else None
        }
    
    def _encode_param(self, value: Any) -> str:
        """URL-encode parameter value."""
        import urllib.parse
        return urllib.parse.quote(str(value))


class TypedEndpointBuilder:
    """
    Strongly typed endpoint builders for specific API operations.
    Provides pre-configured builders for common endpoint patterns.
    """
    
    def __init__(self, context: Optional[RequestContext] = None):
        self.builder = EndpointBuilder(context)
    
    # Authentication endpoints
    def login_request(self, user_id: str, password: str) -> Dict[str, Any]:
        """Build login request."""
        from ..models.Authentication import LoginRequest
        
        login_data = LoginRequest(user_id=user_id, password=password)
        return self.builder.build_request(ApiEndpoints.AUTH_LOGIN, login_data)
    
    def qr_login_request(self, qr_token: str) -> Dict[str, Any]:
        """Build QR login request."""
        from ..models.Authentication import QRLoginRequest
        
        qr_data = QRLoginRequest(qr_token=qr_token)
        return self.builder.build_request(ApiEndpoints.AUTH_QR_LOGIN, qr_data)
    
    def logout_request(self) -> Dict[str, Any]:
        """Build logout request."""
        return self.builder.build_request(ApiEndpoints.AUTH_LOGOUT)
    
    def session_request(self) -> Dict[str, Any]:
        """Build session info request."""
        return self.builder.build_request(ApiEndpoints.AUTH_SESSION)
    
    # Robot endpoints
    def robot_jog_request(self, axis: str, direction: str, step_size: float = 1.0) -> Dict[str, Any]:
        """Build robot jog request."""
        from ..models.Robot import JogRequest, Axis, Direction
        
        jog_data = JogRequest(
            axis=Axis(axis.upper()),
            direction=Direction(direction.lower()),
            step_size=step_size
        )
        return self.builder.build_request(ApiEndpoints.ROBOT_JOG, jog_data)
    
    def robot_move_position_request(self, position: str, velocity: float = 50.0) -> Dict[str, Any]:
        """Build robot move to position request."""
        from ..models.Robot import MoveToPositionRequest, RobotPosition
        
        move_data = MoveToPositionRequest(
            position=RobotPosition(position.upper()),
            velocity=velocity
        )
        return self.builder.build_request(ApiEndpoints.ROBOT_MOVE_POSITION, move_data)
    
    def robot_move_coordinates_request(self, x: float, y: float, z: float, 
                                     velocity: float = 50.0) -> Dict[str, Any]:
        """Build robot move to coordinates request."""
        from ..models.Robot import MoveToCoordinatesRequest
        
        move_data = MoveToCoordinatesRequest(x=x, y=y, z=z, velocity=velocity)
        return self.builder.build_request(ApiEndpoints.ROBOT_MOVE_COORDINATES, move_data)
    
    def robot_status_request(self) -> Dict[str, Any]:
        """Build robot status request."""
        return self.builder.build_request(ApiEndpoints.ROBOT_STATUS)
    
    # Camera endpoints
    def camera_capture_request(self, save_path: Optional[str] = None) -> Dict[str, Any]:
        """Build camera capture request."""
        from ..models.Camera import CaptureRequest
        
        capture_data = CaptureRequest(save_path=save_path)
        return self.builder.build_request(ApiEndpoints.CAMERA_CAPTURE, capture_data)
    
    def camera_stream_request(self) -> Dict[str, Any]:
        """Build camera stream request."""
        return self.builder.build_request(ApiEndpoints.CAMERA_STREAM)
    
    def camera_raw_mode_request(self, enabled: bool) -> Dict[str, Any]:
        """Build camera raw mode toggle request."""
        from ..models.Camera import RawModeRequest
        
        raw_mode_data = RawModeRequest(enabled=enabled)
        return self.builder.build_request(ApiEndpoints.CAMERA_RAW_MODE, raw_mode_data)
    
    # Workpiece endpoints
    def workpieces_list_request(self, status_filter: Optional[str] = None, 
                               limit: Optional[int] = None) -> Dict[str, Any]:
        """Build workpieces list request."""
        query_params = {}
        if status_filter:
            query_params['status'] = status_filter
        if limit:
            query_params['limit'] = limit
        
        return self.builder.build_request(ApiEndpoints.WORKPIECES_LIST, 
                                        query_params=query_params)
    
    def workpiece_get_request(self, workpiece_id: str) -> Dict[str, Any]:
        """Build get single workpiece request."""
        return self.builder.build_request(ApiEndpoints.WORKPIECE_GET, 
                                        path_params={'id': workpiece_id})
    
    def workpiece_create_request(self, workpiece_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build workpiece creation request."""
        from ..models.Workpiece import SaveWorkpieceRequest
        
        save_data = SaveWorkpieceRequest.from_dict(workpiece_data)
        return self.builder.build_request(ApiEndpoints.WORKPIECES_CREATE, save_data)
    
    def workpiece_update_request(self, workpiece_id: str, 
                               workpiece_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build workpiece update request."""
        from ..models.Workpiece import UpdateWorkpieceRequest
        
        update_data = UpdateWorkpieceRequest.from_dict(workpiece_data)
        return self.builder.build_request(ApiEndpoints.WORKPIECE_UPDATE, update_data,
                                        path_params={'id': workpiece_id})
    
    def workpiece_delete_request(self, workpiece_id: str) -> Dict[str, Any]:
        """Build workpiece deletion request."""
        return self.builder.build_request(ApiEndpoints.WORKPIECE_DELETE,
                                        path_params={'id': workpiece_id})
    
    def workpiece_execute_request(self, workpiece_id: str, 
                                parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Build workpiece execution request."""
        from ..models.Workpiece import ExecuteWorkpieceRequest
        
        execute_data = ExecuteWorkpieceRequest(
            workpiece_id=workpiece_id,
            parameters=parameters or {}
        )
        return self.builder.build_request(ApiEndpoints.WORKPIECE_EXECUTE, execute_data,
                                        path_params={'id': workpiece_id})
    
    # Settings endpoints
    def settings_robot_get_request(self) -> Dict[str, Any]:
        """Build robot settings get request."""
        return self.builder.build_request(ApiEndpoints.SETTINGS_ROBOT_GET)
    
    def settings_robot_set_request(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Build robot settings update request."""
        from ..models.Settings import RobotSettingsRequest
        
        settings_data = RobotSettingsRequest.from_dict(settings)
        return self.builder.build_request(ApiEndpoints.SETTINGS_ROBOT_SET, settings_data)
    
    def settings_camera_get_request(self) -> Dict[str, Any]:
        """Build camera settings get request."""
        return self.builder.build_request(ApiEndpoints.SETTINGS_CAMERA_GET)
    
    def settings_camera_set_request(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Build camera settings update request."""
        from ..models.Settings import CameraSettingsRequest
        
        settings_data = CameraSettingsRequest.from_dict(settings)
        return self.builder.build_request(ApiEndpoints.SETTINGS_CAMERA_SET, settings_data)


# Convenience functions
def create_builder(user_id: Optional[str] = None, 
                  session_token: Optional[str] = None) -> TypedEndpointBuilder:
    """Create a typed endpoint builder with optional authentication context."""
    context = RequestContext(user_id=user_id, session_token=session_token)
    return TypedEndpointBuilder(context)


def build_url(endpoint: Endpoint, **params) -> str:
    """Quick URL builder for simple cases."""
    builder = EndpointBuilder()
    
    # Separate path and query parameters
    path_params = {}
    query_params = {}
    
    # Simple heuristic: if parameter name exists in path, it's a path param
    for key, value in params.items():
        if f"{{{key}}}" in endpoint.path:
            path_params[key] = value
        else:
            query_params[key] = value
    
    return builder.build_url(endpoint, path_params, query_params)


# Example usage patterns
if __name__ == "__main__":
    """Example usage of endpoint builders."""
    
    print("🔧 Endpoint Builder Examples")
    print("=" * 30)
    
    # Create builder with authentication context
    builder = create_builder(user_id="admin", session_token="token123")
    
    # Example 1: Simple login request
    login_req = builder.login_request("admin", "password")
    print("Login Request:")
    print(f"  URL: {login_req['url']}")
    print(f"  Method: {login_req['method']}")
    print(f"  Data: {login_req['data']}")
    print()
    
    # Example 2: Robot jog with parameters
    jog_req = builder.robot_jog_request("X", "positive", 10.0)
    print("Robot Jog Request:")
    print(f"  URL: {jog_req['url']}")
    print(f"  Method: {jog_req['method']}")
    print(f"  Data: {jog_req['data']}")
    print()
    
    # Example 3: Workpiece with path parameters
    workpiece_req = builder.workpiece_get_request("wp_12345")
    print("Get Workpiece Request:")
    print(f"  URL: {workpiece_req['url']}")
    print(f"  Method: {workpiece_req['method']}")
    print()
    
    # Example 4: List with query parameters
    list_req = builder.workpieces_list_request(status_filter="ready", limit=50)
    print("List Workpieces Request:")
    print(f"  URL: {list_req['url']}")
    print(f"  Method: {list_req['method']}")
    print()
    
    # Example 5: Direct URL building
    direct_url = build_url(ApiEndpoints.WORKPIECE_GET, id="wp_67890")
    print(f"Direct URL Build: {direct_url}")
    print()
    
    print("✅ All builder examples completed successfully!")