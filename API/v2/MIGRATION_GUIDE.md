# API v2 Migration and Usage Guide

## Table of Contents
1. [Quick Start](#quick-start)
2. [Step-by-Step Migration](#step-by-step-migration)
3. [Usage Examples](#usage-examples)
4. [Testing Guide](#testing-guide)
5. [Troubleshooting](#troubleshooting)
6. [FAQ](#faq)

## Quick Start

### Immediate Benefits (No Code Changes Required)
The new API v2 system provides **full backward compatibility**. Your existing code continues to work unchanged while gaining improved error handling and logging.

```python
# Your existing code still works exactly the same!
requestHandler = RequestHandler(...)
response = requestHandler.handleRequest("login", ["admin", "password"])
# ✅ Works perfectly - no changes needed
```

### Optional: Start Using New Features
```python
# Enhanced router with better error handling
from API.v2.handlers.ModernRequestRouter import RequestRouter

router = RequestRouter()
# Legacy requests work through the new router
response = router.route_request("login", "POST", ["admin", "password"])

# New v2 requests provide type safety  
response = router.route_request("/api/v2/auth/login", "POST", {
    "user_id": "admin",
    "password": "password"
})
```

## Step-by-Step Migration

### Phase 1: Add New Router (Zero Risk)

#### 1.1 Update main.py
```python
# main.py - Add import at the top
from API.v2.handlers.ModernRequestRouter import RequestRouter

# Replace the request handler initialization
# OLD:
from GlueDispensingApplication.communication.NewRequestHandler import RequestHandler
requestHandler = RequestHandler(glueSprayingApplication, settingsController, 
                               cameraSystemController, workpieceController, robotController)

# NEW (but keeping same interface):
from API.v2.handlers.ModernRequestRouter import RequestRouter
requestHandler = RequestRouter()
requestHandler.register_handlers(glueSprayingApplication, settingsController,
                               cameraSystemController, workpieceController, robotController)
```

#### 1.2 Register Handlers
```python
# Add after router initialization in main.py
def setup_api_handlers(router, controllers):
    """Register all API handlers with the new router."""
    
    # Authentication handlers
    from API.v2.handlers.AuthenticationHandler import AuthenticationHandler
    auth_handler = AuthenticationHandler()
    router.register_handler("AUTH_LOGIN", auth_handler.handle_login)
    
    # System handlers  
    def system_start_handler(data):
        result, message = controllers['glue_app'].start()
        return {"success": result, "message": message}
    
    router.register_handler("SYSTEM_START", system_start_handler)
    
    # Robot handlers
    def robot_jog_handler(data):
        # Convert v2 data to controller format
        axis = data.get('axis', 'X')
        direction = data.get('direction', 'positive')
        step = data.get('step_size', 1.0)
        
        legacy_request = f"robot/jog/{axis}/{'Plus' if direction == 'positive' else 'Minus'}"
        return controllers['robot'].handle(legacy_request, [legacy_request.split('/')], step)
    
    router.register_handler("ROBOT_JOG", robot_jog_handler)
    
    # Add more handlers as needed...

# Call setup function
controllers = {
    'glue_app': glueSprayingApplication,
    'settings': settingsController,
    'camera': cameraSystemController, 
    'workpiece': workpieceController,
    'robot': robotController
}
setup_api_handlers(requestHandler, controllers)
```

### Phase 2: Migrate UI Components

#### 2.1 Update Controller Classes
```python
# pl_ui/controller/Controller.py - Update handleLogin method

def handleLogin(self, username, password):
    # OLD way (still works):
    # request = "login"
    # response = self.requestSender.sendRequest(request, data=[username, password])
    
    # NEW way (recommended):
    from API.v2.models.Authentication import LoginRequest
    
    login_request = LoginRequest(
        user_id=username,
        password=password
    )
    
    # Use new router endpoint
    response_dict = self.requestSender.route_request("/api/v2/auth/login", "POST", login_request.to_dict())
    
    # Handle new response format
    if response_dict.get("success"):
        user_data = response_dict.get("data", {}).get("user", {})
        return "1"  # Keep existing return format for compatibility
    else:
        error_type = response_dict.get("errors", {}).get("auth", "unknown")
        if error_type == "user_not_found":
            return "-1"
        elif error_type == "invalid_password":
            return "0"
        return "-1"
```

#### 2.2 Update Robot Operations
```python
# Example: Update robot jog operations
def handleJog(self, axis, direction, step):
    # NEW way with type safety:
    from API.v2.models.Robot import JogRequest, Axis, Direction
    
    jog_request = JogRequest(
        axis=Axis(axis.upper()),
        direction=Direction.POSITIVE if direction == "Plus" else Direction.NEGATIVE,
        step_size=float(step)
    )
    
    response = self.requestSender.route_request("/api/v2/robot/jog", "POST", jog_request.to_dict())
    
    if response.get("success"):
        print(f"Robot jogged {axis} {direction} by {step}")
    else:
        print(f"Jog failed: {response.get('message')}")
```

#### 2.3 Update Workpiece Operations  
```python
def saveWorkpiece(self, data):
    # NEW way with validation:
    from API.v2.models.Workpiece import SaveWorkpieceRequest, Workpiece
    
    try:
        # Convert legacy data to v2 format
        workpiece = Workpiece.from_dict(data)
        
        # Validate before sending
        if not workpiece.validate():
            return False, "Invalid workpiece data"
            
        save_request = SaveWorkpieceRequest(workpiece=workpiece)
        
        response = self.requestSender.route_request("/api/v2/workpieces", "POST", save_request.to_dict())
        
        return response.get("success", False), response.get("message", "Unknown error")
        
    except Exception as e:
        print(f"Workpiece save error: {e}")
        return False, str(e)
```

### Phase 3: Full v2 Adoption

#### 3.1 Replace String Constants

```python
# OLD: Using string constants scattered throughout code
request = "robot/move/home"
path = "/api/v2/robot/jog"

# NEW: Using centralized endpoint constants  
from API.v2.constants.ApiEndpoints import ApiEndpoints

# Type-safe endpoint access
endpoint = ApiEndpoints.ROBOT_MOVE_POSITION
path = ApiEndpoints.ROBOT_JOG.path
method = ApiEndpoints.ROBOT_JOG.method.value

# Or use the registry (built from centralized constants)
from API.v2.endpoints.EndpointRegistry import EndpointRegistry
endpoint = EndpointRegistry.ROBOT_MOVE_POSITION
```

#### 3.2 Use Endpoint Builders for Type Safety

```python
# NEW: Type-safe endpoint builders
from API.v2.utils.EndpointBuilder import create_builder, build_url
from API.v2.constants.ApiEndpoints import ApiEndpoints

# Create authenticated builder
builder = create_builder(user_id="admin", session_token="token123")

# Build complete requests with validation
login_request = builder.login_request("admin", "password")
jog_request = builder.robot_jog_request("X", "positive", 10.0)
workpiece_request = builder.workpiece_get_request("wp_12345")

# Quick URL building
url = build_url(ApiEndpoints.WORKPIECE_GET, id="wp_67890")
# Result: "/api/v2/workpieces/wp_67890"
```

#### 3.2 Use Type-Safe Models Everywhere
```python
# Example: Camera operations
from API.v2.models.Camera import CaptureRequest, CameraResponse

def capture_image(self, settings=None):
    capture_request = CaptureRequest(
        resolution="1920x1080",
        format="jpeg",
        quality=95
    )
    
    response_dict = self.api_client.route_request(
        "/api/v2/camera/capture", 
        "POST", 
        capture_request.to_dict()
    )
    
    if response_dict["success"]:
        return CameraResponse.from_dict(response_dict)
    else:
        raise Exception(response_dict["message"])
```

## Usage Examples

### Authentication Examples

#### Basic Login
```python
from API.v2.models.Authentication import LoginRequest, LoginResponse

# Create request
login_request = LoginRequest(
    user_id="2",
    password="pass"
)

# Send request  
response_dict = router.route_request("/api/v2/auth/login", "POST", login_request.to_dict())
login_response = LoginResponse.from_dict(response_dict)

# Handle response
if login_response.success:
    print(f"Welcome {login_response.user.full_name}")
    session_token = login_response.session_token
else:
    print(f"Login failed: {login_response.message}")
```

#### QR Code Login
```python
from API.v2.models.Authentication import QRLoginRequest

qr_request = QRLoginRequest(qr_data="encoded_user_data")
response = router.route_request("/api/v2/auth/qr-login", "POST", qr_request.to_dict())
```

### Robot Operations Examples

#### Robot Jogging
```python
from API.v2.models.Robot import JogRequest, Axis, Direction

# Jog X axis positive 10mm
jog_request = JogRequest(
    axis=Axis.X,
    direction=Direction.POSITIVE,
    step_size=10.0
)

response = router.route_request("/api/v2/robot/jog", "POST", jog_request.to_dict())
```

#### Move to Predefined Position
```python
from API.v2.models.Robot import MoveToPositionRequest, RobotPosition

move_request = MoveToPositionRequest(
    position=RobotPosition.HOME,
    velocity=50.0  # Optional speed
)

response = router.route_request("/api/v2/robot/move/position", "POST", move_request.to_dict())
```

#### Move to Coordinates
```python
from API.v2.models.Robot import MoveToCoordinatesRequest, Position3D

target_position = Position3D(x=100.0, y=200.0, z=50.0, rx=0, ry=0, rz=90)
move_request = MoveToCoordinatesRequest(
    position=target_position,
    velocity=30.0,
    acceleration=10.0
)

response = router.route_request("/api/v2/robot/move/coordinates", "POST", move_request.to_dict())
```

#### Robot Calibration
```python
from API.v2.models.Robot import CalibrationRequest, CalibrationResponse

calibration_request = CalibrationRequest(calibration_type="robot")
response_dict = router.route_request("/api/v2/robot/calibration", "POST", calibration_request.to_dict())

calibration_response = CalibrationResponse.from_dict(response_dict)
if calibration_response.success:
    print("Calibration completed!")
    if calibration_response.calibration_image:
        # Process calibration image
        image_data = calibration_response.calibration_image
```

### Workpiece Operations Examples

#### Create Workpiece from Camera
```python
from API.v2.models.Workpiece import CreateWorkpieceRequest, WorkpieceCreationResponse

create_request = CreateWorkpieceRequest(
    capture_new_image=True,
    detection_params={
        "threshold": 127,
        "blur_kernel": 5
    }
)

response_dict = router.route_request("/api/v2/workpieces/create/camera", "POST", create_request.to_dict())
creation_response = WorkpieceCreationResponse.from_dict(response_dict)

if creation_response.success:
    print(f"Detected {len(creation_response.detected_contours)} contours")
    captured_image = creation_response.captured_image  # Base64 encoded
```

#### Save Complete Workpiece
```python
from API.v2.models.Workpiece import (
    SaveWorkpieceRequest, Workpiece, WorkpieceMetadata, 
    Contour, SprayPattern, WorkpieceStatus
)

# Define external contour
external_contour = Contour(
    points=[[0, 0], [100, 0], [100, 100], [0, 100]],  # Rectangle
    closed=True
)

# Define spray pattern
spray_pattern = SprayPattern(
    contour_paths=[
        Contour(points=[[10, 10], [90, 10], [90, 90], [10, 90]], closed=True)
    ],
    fill_paths=[],
    spray_speed=2.0,
    spray_pressure=1.5
)

# Create workpiece
workpiece = Workpiece(
    metadata=WorkpieceMetadata(
        name="Test Rectangle",
        description="Simple rectangular workpiece",
        thickness=4.0,
        material_type="Plastic",
        created_by="operator"
    ),
    external_contour=external_contour,
    spray_pattern=spray_pattern,
    status=WorkpieceStatus.READY
)

# Save workpiece
save_request = SaveWorkpieceRequest(workpiece=workpiece)
response = router.route_request("/api/v2/workpieces", "POST", save_request.to_dict())
```

#### List and Filter Workpieces
```python
from API.v2.models.Workpiece import WorkpieceListRequest, WorkpieceStatus

# Get ready workpieces, 20 at a time
list_request = WorkpieceListRequest(
    status_filter=WorkpieceStatus.READY,
    limit=20,
    offset=0
)

response_dict = router.route_request("/api/v2/workpieces", "GET", list_request.to_dict())
workpiece_response = WorkpieceResponse.from_dict(response_dict)

if workpiece_response.success:
    print(f"Found {workpiece_response.total_count} workpieces")
    for wp in workpiece_response.workpieces:
        print(f"- {wp.metadata.name} ({wp.status.value})")
```

#### Execute Workpiece
```python
from API.v2.models.Workpiece import ExecuteWorkpieceRequest

execute_request = ExecuteWorkpieceRequest(
    workpiece_id="wp_123",
    execution_params={
        "dry_run": False,
        "speed_multiplier": 1.0
    }
)

response = router.route_request("/api/v2/workpieces/wp_123/execute", "POST", execute_request.to_dict())
```

### System Operations Examples

#### Start/Stop System
```python
# Start system
response = router.route_request("/api/v2/system/start", "POST", {})

# Stop system  
response = router.route_request("/api/v2/system/stop", "POST", {})

# Get system status
status_response = router.route_request("/api/v2/system/status", "GET", {})
```

### Settings Examples

#### Get/Update Robot Settings
```python
# Get current robot settings
robot_settings = router.route_request("/api/v2/settings/robot", "GET", {})

# Update robot settings
updated_settings = {
    "max_velocity": 100.0,
    "max_acceleration": 50.0,
    "home_position": [0, 0, 100, 180, 0, 0]
}
response = router.route_request("/api/v2/settings/robot", "PUT", updated_settings)
```

## Testing Guide

### Unit Testing API Models
```python
import unittest
from API.v2.models.Robot import JogRequest, Axis, Direction

class TestRobotModels(unittest.TestCase):
    def test_jog_request_validation(self):
        # Valid request
        valid_request = JogRequest(
            axis=Axis.X,
            direction=Direction.POSITIVE, 
            step_size=10.0
        )
        self.assertTrue(valid_request.validate())
        
        # Invalid step size
        invalid_request = JogRequest(
            axis=Axis.X,
            direction=Direction.POSITIVE,
            step_size=-5.0  # Negative step
        )
        self.assertFalse(invalid_request.validate())
    
    def test_serialization(self):
        request = JogRequest(axis=Axis.Y, direction=Direction.NEGATIVE, step_size=5.0)
        
        # Test to_dict
        data = request.to_dict()
        self.assertEqual(data['axis'], 'Y')
        self.assertEqual(data['direction'], 'negative')
        
        # Test from_dict
        restored = JogRequest.from_dict(data)
        self.assertEqual(restored.axis, Axis.Y)
        self.assertEqual(restored.step_size, 5.0)
```

### Integration Testing with Router
```python
class TestApiRouter(unittest.TestCase):
    def setUp(self):
        self.router = RequestRouter()
        # Register mock handlers for testing
        self.router.register_handler("AUTH_LOGIN", self.mock_login_handler)
        
    def mock_login_handler(self, data):
        from API.v2.models.Authentication import LoginResponse, UserInfo
        
        if data.user_id == "admin" and data.password == "pass":
            user = UserInfo(id=1, first_name="Admin", last_name="User", role="Admin")
            return LoginResponse.authenticated(user, "token123", "2024-12-08T10:00:00").to_dict()
        else:
            return LoginResponse.failed("invalid_credentials").to_dict()
    
    def test_successful_login(self):
        response = self.router.route_request("/api/v2/auth/login", "POST", {
            "user_id": "admin",
            "password": "pass"
        })
        
        self.assertTrue(response["success"])
        self.assertIn("user", response["data"])
        self.assertEqual(response["data"]["user"]["role"], "Admin")
    
    def test_failed_login(self):
        response = self.router.route_request("/api/v2/auth/login", "POST", {
            "user_id": "wrong",
            "password": "wrong"
        })
        
        self.assertFalse(response["success"])
        self.assertIn("invalid_credentials", response["errors"]["auth"])
```

### Mock Testing for Development
```python
# Create mock router for UI development
class MockApiRouter:
    def route_request(self, path, method, data):
        if path == "/api/v2/auth/login":
            return {
                "success": True,
                "message": "Mock login successful", 
                "data": {
                    "user": {"id": 1, "first_name": "Mock", "last_name": "User", "role": "Admin"},
                    "session_token": "mock_token_123"
                }
            }
        elif path == "/api/v2/robot/jog":
            return {
                "success": True,
                "message": f"Mock jog {data.get('axis', 'X')} {data.get('direction', 'positive')}"
            }
        else:
            return {"success": False, "message": f"Mock endpoint not implemented: {path}"}

# Use in development
if DEVELOPMENT_MODE:
    router = MockApiRouter()
else:
    router = RequestRouter()
```

## Troubleshooting

### Common Issues and Solutions

#### Issue: "Module not found" errors
```python
# Problem: Import errors when using new API
from API.v2.models.Robot import JogRequest  # ImportError

# Solution: Check Python path and ensure files exist
import sys
print(sys.path)  # Verify API directory is in path

# Alternative: Use relative imports
from .v2.models.Robot import JogRequest
```

#### Issue: Validation failures
```python
# Problem: Request validation always fails
jog_request = JogRequest(axis="X", direction="positive", step_size=10)  # Fails validation

# Solution: Use proper enums
from API.v2.models.Robot import Axis, Direction
jog_request = JogRequest(axis=Axis.X, direction=Direction.POSITIVE, step_size=10)
```

#### Issue: Legacy compatibility not working
```python
# Problem: Old requests returning errors
response = router.route_request("login", "POST", ["user", "pass"])  # Error

# Solution: Check legacy mapping
from API.v2.endpoints.EndpointRegistry import LEGACY_TO_V2_MAPPING
print(LEGACY_TO_V2_MAPPING.get("login"))  # Should show AUTH_LOGIN endpoint

# Ensure handler is registered
print("AUTH_LOGIN" in router.handlers)  # Should be True
```

#### Issue: Response format confusion
```python
# Problem: Expecting old response format
if response == "1":  # Old format
    print("Success")

# Solution: Handle new response format
if response.get("success"):  # New format
    print(f"Success: {response['message']}")
    
# Or create compatibility wrapper
def get_legacy_response(new_response):
    if new_response.get("success"):
        auth_error = new_response.get("errors", {}).get("auth")
        if auth_error == "user_not_found":
            return "-1"
        elif auth_error == "invalid_password":
            return "0"
        return "1"
    return "-1"
```

### Debugging Tips

#### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Router will log all requests and responses
router = RequestRouter()
response = router.route_request("/api/v2/auth/login", "POST", data)
# Will output: "Processing request: /api/v2/auth/login with data: {...}"
```

#### Validate Data Before Sending
```python
from API.v2.models.Robot import JogRequest

# Always validate before sending
jog_request = JogRequest(...)
if not jog_request.validate():
    print("Validation failed!")
    print(f"Request data: {jog_request.to_dict()}")
else:
    response = router.route_request(...)
```

#### Check Handler Registration
```python
# List all registered handlers
router = RequestRouter()
endpoints = router.endpoint_registry.get_all_endpoints()

for name, endpoint in endpoints.items():
    handler_registered = name in router.handlers
    print(f"{name}: {'✓' if handler_registered else '✗'} {endpoint.path}")
```

## FAQ

### Q: Do I need to change my existing code immediately?
**A: No!** The new API is 100% backward compatible. Your existing code continues to work without any changes.

### Q: What's the benefit of migrating to v2?
**A: Type safety, better error handling, autocomplete in IDEs, validation, consistent responses, and easier testing.**

### Q: Can I mix old and new API calls?
**A: Yes!** You can gradually migrate. Some requests can use old format while others use new format.

### Q: How do I handle the different response formats?
**A: Use compatibility wrappers or update response handling to use the new structured format.**

### Q: Will the old API be removed?
**A: Not immediately. We'll provide deprecation warnings and migration period before any removal.**

### Q: How do I add custom validation?
```python
@dataclass
class CustomWorkpieceRequest(ApiRequest):
    name: str
    thickness: float
    
    def validate(self) -> bool:
        return (
            len(self.name.strip()) > 0 and
            0 < self.thickness <= 50 and
            not any(char in self.name for char in ['/', '\\', '<', '>'])  # No special chars
        )
```

### Q: How do I add new endpoints?
```python
# 1. Add to EndpointRegistry
NEW_ENDPOINT = ApiEndpoint("/api/v2/custom/action", HttpMethod.POST, "Custom action")

# 2. Create request/response models
@dataclass
class CustomRequest(ApiRequest):
    action_param: str

# 3. Register handler
def custom_handler(data: CustomRequest):
    # Handle the request
    return {"success": True, "message": "Custom action completed"}

router.register_handler("NEW_ENDPOINT", custom_handler)
```

### Q: How do I test the new API?
**A: Use the included test examples and create unit tests for your models. The type safety makes testing much easier.**

### Q: How do I validate my endpoints and API design?
**A: Use the built-in validation utilities:**

```python
from API.v2.utils.EndpointValidator import EndpointValidator, generate_api_docs

# Validate all endpoints
results = EndpointValidator.validate_all_endpoints()
for name, result in results.items():
    if not result.is_valid:
        print(f"{name}: {result.issues}")

# Check consistency across API
consistency = EndpointValidator.check_consistency()
print(f"Found {len(consistency['path_conflicts'])} path conflicts")

# Generate complete documentation
docs = generate_api_docs()
with open('API_DOCS.md', 'w') as f:
    f.write(docs)

# Export OpenAPI schema
schema = EndpointValidator.export_openapi_schema()
```

### Q: How do I find all available endpoints?
**A: Use the centralized endpoint constants:**

```python
from API.v2.constants.ApiEndpoints import ApiEndpoints, EndpointGroups

# Browse all endpoints by category
print("Authentication endpoints:")
for endpoint in EndpointGroups.AUTHENTICATION:
    print(f"  - {endpoint.path} ({endpoint.method.value})")

# Access specific endpoints
login_endpoint = ApiEndpoints.AUTH_LOGIN
print(f"Login: {login_endpoint.path}")
print(f"Requires auth: {login_endpoint.requires_auth}")
print(f"Rate limited: {login_endpoint.rate_limited}")

# Get all endpoint names
endpoint_names = [name for name in dir(ApiEndpoints) 
                 if not name.startswith('_') and hasattr(getattr(ApiEndpoints, name), 'path')]
print(f"Total endpoints: {len(endpoint_names)}")
```

## Advanced Features

### Endpoint Validation and Documentation

The API v2 system includes comprehensive validation and documentation tools:

#### Automatic Validation
```python
from API.v2.utils.EndpointValidator import EndpointValidator

# Validate REST conventions
validator = EndpointValidator()
result = validator.validate_endpoint("AUTH_LOGIN")
print(f"Valid: {result.is_valid}")
print(f"Issues: {result.issues}")
print(f"Suggestions: {result.suggestions}")

# Check all endpoints at once
all_results = validator.validate_all_endpoints()
valid_count = sum(1 for r in all_results.values() if r.is_valid)
print(f"API Health: {valid_count}/{len(all_results)} endpoints valid")
```

#### Documentation Generation
```python
from API.v2.utils.EndpointValidator import EndpointValidator

# Generate comprehensive docs
docs = EndpointValidator.generate_documentation()
print(docs)  # Markdown-formatted documentation

# Export OpenAPI schema for tools like Swagger
openapi_schema = EndpointValidator.export_openapi_schema()
# Use with API documentation tools, Postman, etc.
```

#### Type-Safe Request Building
```python
from API.v2.utils.EndpointBuilder import create_builder, build_url

# Create authenticated request builder
builder = create_builder(user_id="admin", session_token="abc123")

# Build requests with automatic validation
login_req = builder.login_request("admin", "password")
print(login_req)  # {'url': '/api/v2/auth/login', 'method': 'POST', 'data': {...}}

# Build URLs with parameters
from API.v2.constants.ApiEndpoints import ApiEndpoints
url = build_url(ApiEndpoints.WORKPIECE_GET, id="wp_12345")
print(url)  # "/api/v2/workpieces/wp_12345"

# Build complex requests
workpiece_req = builder.workpiece_execute_request(
    workpiece_id="wp_12345",
    parameters={"dry_run": True, "speed": 0.8}
)
```

This migration guide should help you transition smoothly from the old string-based API to the new type-safe v2 API while maintaining full backward compatibility.