# API v2 Troubleshooting and FAQ

## Table of Contents
1. [Common Issues](#common-issues)
2. [Debugging Guide](#debugging-guide)
3. [Frequently Asked Questions](#frequently-asked-questions)
4. [Performance Issues](#performance-issues)
5. [Integration Problems](#integration-problems)
6. [Support Resources](#support-resources)

## Common Issues

### 🚨 Issue 1: "Module not found" when importing API v2

**Error Message:**
```python
ModuleNotFoundError: No module named 'API.v2.models'
```

**Cause:** Python path not configured correctly or files not in expected location.

**Solutions:**

1. **Check file structure:**
   ```
   Your_Project/
   ├── API/
   │   ├── __init__.py
   │   └── v2/
   │       ├── __init__.py
   │       ├── models/
   │       │   ├── __init__.py
   │       │   └── Authentication.py
   │       └── handlers/
   ```

2. **Add to Python path:**
   ```python
   import sys
   import os
   sys.path.append(os.path.dirname(__file__))  # Add current directory
   
   # Or add project root
   sys.path.append('/path/to/your/project')
   ```

3. **Use relative imports:**
   ```python
   # Instead of absolute imports
   from API.v2.models.Authentication import LoginRequest
   
   # Use relative imports
   from .v2.models.Authentication import LoginRequest
   ```

**Verification:**
```python
# Test imports
try:
    from API.v2.models.BaseModel import BaseModel
    from API.v2.handlers.ModernRequestRouter import RequestRouter
    print("✅ API v2 imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
```

---

### 🚨 Issue 2: Validation always fails

**Error Message:**
```python
# Request validation failed
response = {"success": False, "message": "Request validation failed"}
```

**Cause:** Using wrong data types or missing required fields.

**Common Mistakes:**

1. **Using strings instead of enums:**
   ```python
   # ❌ Wrong - strings won't validate
   jog_request = JogRequest(
       axis="X",                    # Should be Axis.X
       direction="positive",        # Should be Direction.POSITIVE
       step_size="10.0"            # Should be float, not string
   )
   
   # ✅ Correct - use proper types
   from API.v2.models.Robot import Axis, Direction
   jog_request = JogRequest(
       axis=Axis.X,
       direction=Direction.POSITIVE,
       step_size=10.0
   )
   ```

2. **Missing required fields:**
   ```python
   # ❌ Wrong - missing required fields
   login_request = LoginRequest(user_id="123")  # Missing password
   
   # ✅ Correct - all required fields
   login_request = LoginRequest(user_id="123", password="pass")
   ```

3. **Invalid field values:**
   ```python
   # ❌ Wrong - negative step size
   jog_request = JogRequest(axis=Axis.X, direction=Direction.POSITIVE, step_size=-5.0)
   
   # ✅ Correct - positive step size
   jog_request = JogRequest(axis=Axis.X, direction=Direction.POSITIVE, step_size=5.0)
   ```

**Debug Validation:**
```python
# Check validation step by step
request = JogRequest(axis=Axis.X, direction=Direction.POSITIVE, step_size=-5.0)

print(f"Request data: {request.to_dict()}")
print(f"Validation result: {request.validate()}")

# Manual validation check
if hasattr(request, 'step_size'):
    print(f"Step size: {request.step_size}, Valid: {request.step_size > 0}")
```

---

### 🚨 Issue 3: Legacy requests not working

**Error Message:**
```python
{"success": False, "message": "Unknown legacy endpoint: robot/jog/X/Plus"}
```

**Cause:** Legacy endpoint not mapped or handler not registered.

**Solutions:**

1. **Check legacy mapping exists:**
   ```python
   from API.v2.endpoints.EndpointRegistry import get_v2_endpoint
   
   legacy_path = "robot/jog/X/Plus"
   v2_endpoint = get_v2_endpoint(legacy_path)
   
   if v2_endpoint:
       print(f"✅ Legacy path '{legacy_path}' maps to '{v2_endpoint.path}'")
   else:
       print(f"❌ No mapping found for '{legacy_path}'")
   ```

2. **Register missing handlers:**
   ```python
   router = RequestRouter()
   
   # Check if handler is registered
   if "ROBOT_JOG" not in router.handlers:
       print("❌ ROBOT_JOG handler not registered")
       
       # Register handler
       def robot_jog_handler(data):
           return {"success": True, "message": f"Jogged {data.axis}"}
       
       router.register_handler("ROBOT_JOG", robot_jog_handler)
       print("✅ Handler registered")
   ```

3. **Add custom legacy mapping:**
   ```python
   # Add to LEGACY_TO_V2_MAPPING
   from API.v2.endpoints.EndpointRegistry import LEGACY_TO_V2_MAPPING, EndpointRegistry
   
   LEGACY_TO_V2_MAPPING["custom/legacy/path"] = EndpointRegistry.CUSTOM_ENDPOINT
   ```

---

### 🚨 Issue 4: Handler exceptions not handled gracefully

**Error Message:**
```python
{"success": False, "message": "Handler execution failed: division by zero"}
```

**Cause:** Unhandled exceptions in handler code.

**Solutions:**

1. **Add proper error handling to handlers:**
   ```python
   def safe_handler(request):
       try:
           # Your handler logic
           result = process_request(request)
           return {"success": True, "data": result}
           
       except ValidationError as e:
           return {"success": False, "message": f"Validation error: {e}"}
           
       except Exception as e:
           print(f"Handler error: {e}")  # Log for debugging
           return {"success": False, "message": "Internal handler error"}
   ```

2. **Use router's safe execution wrapper:**
   ```python
   # In your handler
   return self.safe_execute(
       lambda: risky_operation(),
       "Operation description for error messages"
   )
   ```

3. **Validate input data in handlers:**
   ```python
   def robot_jog_handler(request):
       # Validate request object
       if not request.validate():
           return {"success": False, "message": "Invalid jog parameters"}
       
       # Additional business logic validation
       if request.step_size > 100:
           return {"success": False, "message": "Step size too large (max 100mm)"}
       
       # Proceed with operation
       return perform_jog(request)
   ```

---

### 🚨 Issue 5: Response format inconsistency

**Problem:** Expecting old response format but receiving new format.

**Old Code Expecting:**
```python
response = requestSender.sendRequest("login", ["user", "pass"])
if response.message == "1":  # Old format
    print("Login successful")
```

**New Format Returns:**
```python
{
    "success": True,
    "message": "Welcome, John Doe",
    "timestamp": "2024-12-08T10:00:00",
    "data": {"user": {...}, "session_token": "..."}
}
```

**Solutions:**

1. **Update response handling:**
   ```python
   # ✅ New way - use structured response
   response = router.route_request("/api/v2/auth/login", "POST", login_data)
   if response.get("success"):
       user_data = response.get("data", {}).get("user", {})
       print(f"Login successful: {user_data.get('first_name', 'User')}")
   ```

2. **Create compatibility wrapper:**
   ```python
   def convert_to_legacy_format(new_response):
       """Convert new response format to legacy format."""
       if new_response.get("success"):
           # Check for authentication errors in new format
           auth_error = new_response.get("errors", {}).get("auth")
           if auth_error == "user_not_found":
               return "-1"
           elif auth_error == "invalid_password":
               return "0"
           return "1"  # Success
       return "-1"  # General failure
   
   # Usage
   new_response = router.route_request("login", "POST", ["user", "pass"])
   legacy_response = convert_to_legacy_format(new_response)
   
   if legacy_response == "1":
       print("Login successful (legacy format)")
   ```

3. **Gradual migration approach:**
   ```python
   def handle_login_response(response):
       """Handle both old and new response formats."""
       # Check if it's new format
       if isinstance(response, dict) and "success" in response:
           return response.get("success", False)
       
       # Handle old format
       elif response in ["1", 1]:
           return True
       
       return False
   ```

---

## Debugging Guide

### Enable Debug Logging

```python
import logging

# Enable debug logging for API v2
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create API logger
logger = logging.getLogger('API.v2')
logger.setLevel(logging.DEBUG)

# In your code
logger.debug(f"Processing request: {request_path}")
logger.debug(f"Request data: {request_data}")
logger.debug(f"Response: {response}")
```

### Request/Response Tracing

```python
class DebugRouter(RequestRouter):
    """Router with debug tracing."""
    
    def route_request(self, path, method, data=None):
        print(f"🔍 DEBUG: Routing request")
        print(f"   Path: {path}")
        print(f"   Method: {method}")
        print(f"   Data: {data}")
        
        # Call parent method
        response = super().route_request(path, method, data)
        
        print(f"🔍 DEBUG: Response")
        print(f"   Success: {response.get('success')}")
        print(f"   Message: {response.get('message')}")
        
        return response

# Use debug router
debug_router = DebugRouter()
response = debug_router.route_request("/api/v2/auth/login", "POST", {...})
```

### Model Validation Debugging

```python
def debug_model_validation(model_instance):
    """Debug why model validation is failing."""
    print(f"🔍 Debugging {type(model_instance).__name__} validation")
    
    # Check each field
    for field_name, field_info in model_instance.__dataclass_fields__.items():
        value = getattr(model_instance, field_name)
        print(f"   {field_name}: {value} (type: {type(value).__name__})")
        
        # Check required fields
        if field_info.default is field_info.default_factory is None:
            if value is None:
                print(f"   ❌ {field_name} is required but None")
    
    # Run validation
    is_valid = model_instance.validate()
    print(f"   Validation result: {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    return is_valid

# Usage
login_request = LoginRequest(user_id="123", password="")
debug_model_validation(login_request)
```

### Handler Registration Debugging

```python
def debug_handler_registration(router):
    """Debug handler registration status."""
    endpoints = router.endpoint_registry.get_all_endpoints()
    
    print("🔍 Handler Registration Status:")
    print("-" * 50)
    
    registered_count = 0
    for name, endpoint in endpoints.items():
        is_registered = name in router.handlers
        status = "✅ Registered" if is_registered else "❌ Missing"
        print(f"{status:12} {name:20} {endpoint.path}")
        
        if is_registered:
            registered_count += 1
    
    print("-" * 50)
    print(f"Total: {registered_count}/{len(endpoints)} handlers registered")

# Usage
debug_handler_registration(router)
```

---

## Frequently Asked Questions

### Q1: Do I need to change all my existing code to use API v2?

**A: No!** API v2 is fully backward compatible. Your existing code continues to work unchanged.

```python
# This still works exactly as before
response = requestHandler.handleRequest("login", ["user", "pass"])

# But you can also use the new format when convenient
response = router.route_request("/api/v2/auth/login", "POST", {...})
```

### Q2: Can I mix old and new API calls in the same application?

**A: Yes!** You can gradually migrate endpoints one at a time.

```python
# Some calls use old format
robot_response = requestHandler.handleRequest("robot/jog/X/Plus", 10.0)

# Others use new format
login_response = router.route_request("/api/v2/auth/login", "POST", login_data)
```

### Q3: How do I add validation rules specific to my business logic?

**A: Override the validate() method in your model subclasses:**

```python
@dataclass
class CustomWorkpieceRequest(SaveWorkpieceRequest):
    """Custom workpiece request with business rules."""
    
    def validate(self) -> bool:
        # Call parent validation first
        if not super().validate():
            return False
        
        # Add custom business logic
        if self.workpiece.metadata.name.startswith("TEST_"):
            return False  # No test workpieces allowed
        
        if self.workpiece.metadata.thickness > 10.0:
            return False  # Max thickness limit
        
        return True
```

### Q4: How do I handle different user roles in API validation?

**A: Add role-based validation in your handlers:**

```python
def protected_handler(request, current_user=None):
    """Handler with role-based access control."""
    
    # Check if user has required role
    required_role = "Admin"
    if current_user.role != required_role:
        return {
            "success": False,
            "message": f"Access denied. Required role: {required_role}",
            "errors": {"auth": "insufficient_privileges"}
        }
    
    # Proceed with operation
    return perform_admin_operation(request)
```

### Q5: How do I test my custom handlers?

**A: Use the provided testing utilities:**

```python
import unittest
from API.v2.handlers.ModernRequestRouter import RequestRouter

class TestCustomHandlers(unittest.TestCase):
    def setUp(self):
        self.router = RequestRouter()
        self.router.register_handler("CUSTOM_ENDPOINT", my_custom_handler)
    
    def test_custom_handler(self):
        response = self.router.route_request("/api/v2/custom/endpoint", "POST", {
            "param1": "value1",
            "param2": "value2"
        })
        
        self.assertTrue(response["success"])
        self.assertIn("expected_data", response["data"])
```

### Q6: How do I add custom endpoints not in the standard registry?

**A: Extend the endpoint registry:**

```python
from API.v2.endpoints.EndpointRegistry import EndpointRegistry, ApiEndpoint, HttpMethod

# Add custom endpoint
EndpointRegistry.CUSTOM_OPERATION = ApiEndpoint(
    "/api/v2/custom/operation",
    HttpMethod.POST,
    "My custom operation"
)

# Register handler
def custom_handler(request):
    return {"success": True, "message": "Custom operation completed"}

router.register_handler("CUSTOM_OPERATION", custom_handler)

# Use it
response = router.route_request("/api/v2/custom/operation", "POST", {})
```

### Q7: How do I handle file uploads with the new API?

**A: Create models that handle file data:**

```python
@dataclass
class FileUploadRequest(ApiRequest):
    """Request for file uploads."""
    filename: str
    file_data: str  # Base64 encoded
    file_type: str
    
    def validate(self) -> bool:
        return (
            bool(self.filename) and
            bool(self.file_data) and
            self.file_type in ["image/jpeg", "application/pdf", "text/csv"]
        )

def upload_handler(request: FileUploadRequest):
    # Decode file data
    import base64
    file_bytes = base64.b64decode(request.file_data)
    
    # Save file
    with open(f"uploads/{request.filename}", "wb") as f:
        f.write(file_bytes)
    
    return {"success": True, "message": f"File {request.filename} uploaded"}
```

### Q8: How do I implement rate limiting with the new API?

**A: Add middleware to your router:**

```python
import time
from collections import defaultdict, deque

class RateLimitedRouter(RequestRouter):
    """Router with rate limiting."""
    
    def __init__(self):
        super().__init__()
        self.request_history = defaultdict(deque)
        self.rate_limit = 60  # requests per minute
    
    def route_request(self, path, method, data=None):
        # Check rate limit
        client_id = self.get_client_id(data)  # Implement based on your needs
        current_time = time.time()
        
        # Clean old requests
        minute_ago = current_time - 60
        while (self.request_history[client_id] and 
               self.request_history[client_id][0] < minute_ago):
            self.request_history[client_id].popleft()
        
        # Check if rate limit exceeded
        if len(self.request_history[client_id]) >= self.rate_limit:
            return {
                "success": False,
                "message": "Rate limit exceeded",
                "errors": {"rate_limit": "Too many requests"}
            }
        
        # Record request
        self.request_history[client_id].append(current_time)
        
        # Process normally
        return super().route_request(path, method, data)
```

---

## Performance Issues

### Issue: Slow response times

**Symptoms:**
- API calls taking longer than expected
- Timeouts in UI components

**Debugging:**
```python
import time

def timed_handler(original_handler):
    """Wrapper to time handler execution."""
    def wrapper(request):
        start_time = time.time()
        
        result = original_handler(request)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"Handler execution time: {execution_time:.3f}s")
        
        if execution_time > 1.0:  # Warn if over 1 second
            print(f"⚠️  Slow handler detected: {execution_time:.3f}s")
        
        return result
    
    return wrapper

# Apply to handlers
router.register_handler("SLOW_ENDPOINT", timed_handler(slow_handler))
```

**Solutions:**
1. **Optimize handler logic**
2. **Add caching**
3. **Use async operations for I/O**
4. **Profile bottlenecks**

### Issue: High memory usage

**Debugging:**
```python
import tracemalloc

def memory_profiled_handler(original_handler):
    """Profile memory usage of handlers."""
    def wrapper(request):
        tracemalloc.start()
        
        result = original_handler(request)
        
        current, peak = tracemalloc.get_traced_memory()
        print(f"Memory usage: current={current/1024/1024:.1f}MB, peak={peak/1024/1024:.1f}MB")
        
        tracemalloc.stop()
        return result
    
    return wrapper
```

---

## Integration Problems

### Issue: UI components not receiving expected data

**Check data flow:**
```python
def debug_data_flow(router, endpoint, method, request_data):
    """Debug complete data flow."""
    print("🔍 Data Flow Debug:")
    print(f"1. Input: {request_data}")
    
    # Process request
    response = router.route_request(endpoint, method, request_data)
    print(f"2. Response: {response}")
    
    # Check data extraction
    if response.get("success"):
        data = response.get("data", {})
        print(f"3. Extracted data: {data}")
        
        # Validate expected fields
        expected_fields = ["user", "session_token"]  # Customize per endpoint
        for field in expected_fields:
            if field in data:
                print(f"   ✅ {field}: {data[field]}")
            else:
                print(f"   ❌ Missing field: {field}")
    else:
        print(f"3. Error: {response.get('message')}")
        errors = response.get("errors", {})
        for field, error in errors.items():
            print(f"   ❌ {field}: {error}")
```

---

## Support Resources

### Debug Utilities

```python
# API/v2/debug_utils.py
class ApiDebugger:
    """Utility class for debugging API issues."""
    
    @staticmethod
    def validate_environment():
        """Check if API v2 environment is set up correctly."""
        checks = []
        
        # Check imports
        try:
            from API.v2.models.BaseModel import BaseModel
            checks.append("✅ Models import successfully")
        except ImportError as e:
            checks.append(f"❌ Model import failed: {e}")
        
        # Check router
        try:
            from API.v2.handlers.ModernRequestRouter import RequestRouter
            router = RequestRouter()
            checks.append("✅ Router creates successfully")
        except Exception as e:
            checks.append(f"❌ Router creation failed: {e}")
        
        # Check endpoints
        try:
            from API.v2.endpoints.EndpointRegistry import EndpointRegistry
            endpoints = EndpointRegistry.get_all_endpoints()
            checks.append(f"✅ {len(endpoints)} endpoints registered")
        except Exception as e:
            checks.append(f"❌ Endpoint registry failed: {e}")
        
        return checks
    
    @staticmethod
    def test_basic_functionality():
        """Test basic API functionality."""
        from API.v2.handlers.ModernRequestRouter import RequestRouter
        from API.v2.models.Authentication import LoginRequest
        
        router = RequestRouter()
        
        # Register test handler
        def test_handler(request):
            return {"success": True, "message": "Test successful"}
        
        router.register_handler("AUTH_LOGIN", test_handler)
        
        # Test request
        response = router.route_request("/api/v2/auth/login", "POST", {
            "user_id": "test",
            "password": "test"
        })
        
        return response.get("success", False)

# Usage
if __name__ == "__main__":
    debugger = ApiDebugger()
    
    print("🔧 API v2 Environment Check:")
    for check in debugger.validate_environment():
        print(f"  {check}")
    
    print(f"\n🧪 Basic Functionality Test: {'✅ PASS' if debugger.test_basic_functionality() else '❌ FAIL'}")
```

### Contact Information

For additional support:

1. **Documentation**: See `MIGRATION_GUIDE.md` and `API_DESIGN_GUIDE.md`
2. **Examples**: Check `examples/` directory for usage patterns
3. **Tests**: Run test suite to identify issues
4. **Code Review**: Have experienced developer review your integration

### Useful Commands

```bash
# Run diagnostics
python -c "from API.v2.debug_utils import ApiDebugger; ApiDebugger().validate_environment()"

# Test specific model
python -c "from API.v2.models.Robot import JogRequest, Axis, Direction; print(JogRequest(axis=Axis.X, direction=Direction.POSITIVE, step_size=10).validate())"

# Check endpoint mappings
python API/v2/endpoints/EndpointRegistry.py

# Run all tests
python -m unittest discover API/v2/tests/ -v
```

---

## Centralized Endpoint Issues

### 🚨 Issue 6: Import errors with centralized endpoints

**Error Message:**
```python
ImportError: cannot import name 'ApiEndpoints' from 'API.v2.constants.ApiEndpoints'
```

**Cause:** Missing or incorrect import of centralized endpoint constants.

**Solutions:**

1. **Check file exists:**
   ```bash
   ls API/v2/constants/ApiEndpoints.py
   ```

2. **Verify correct import:**
   ```python
   # ✅ Correct import
   from API.v2.constants.ApiEndpoints import ApiEndpoints, HttpMethod
   
   # Use endpoints
   login_endpoint = ApiEndpoints.AUTH_LOGIN
   print(f"Path: {login_endpoint.path}")
   print(f"Method: {login_endpoint.method.value}")
   ```

3. **Check for circular imports:**
   ```python
   # Avoid circular imports - don't import constants in base models
   # Import constants only where needed
   ```

**Verification:**
```python
try:
    from API.v2.constants.ApiEndpoints import ApiEndpoints, EndpointGroups, HttpMethod
    print(f"✅ Found {len([name for name in dir(ApiEndpoints) if not name.startswith('_')])} endpoints")
    print(f"✅ Found {len([name for name in dir(EndpointGroups) if not name.startswith('_')])} endpoint groups")
except ImportError as e:
    print(f"❌ Import failed: {e}")
```

---

### 🚨 Issue 7: Endpoint validation fails

**Error Message:**
```python
ValidationResult(is_valid=False, endpoint_name='AUTH_LOGIN', issues=['Path format invalid'])
```

**Cause:** Endpoint constants don't follow REST conventions or have validation issues.

**Solutions:**

1. **Check endpoint format:**
   ```python
   from API.v2.utils.EndpointValidator import EndpointValidator
   
   validator = EndpointValidator()
   result = validator.validate_endpoint("AUTH_LOGIN")
   
   print(f"Valid: {result.is_valid}")
   for issue in result.issues:
       print(f"Issue: {issue}")
   for suggestion in result.suggestions:
       print(f"Suggestion: {suggestion}")
   ```

2. **Fix endpoint definition:**
   ```python
   # ❌ Wrong - doesn't follow REST conventions
   INVALID_ENDPOINT = Endpoint(
       path="/api/v2/badPath",  # Should be lowercase with hyphens
       method=HttpMethod.POST,
       description="bad",       # Too short
       requires_auth=True
   )
   
   # ✅ Correct - follows REST conventions
   VALID_ENDPOINT = Endpoint(
       path="/api/v2/auth/login",
       method=HttpMethod.POST,
       description="User login with credentials",
       requires_auth=False,  # Login shouldn't require auth
       rate_limited=True
   )
   ```

3. **Run consistency check:**
   ```python
   consistency = validator.check_consistency()
   for category, issues in consistency.items():
       if issues:
           print(f"{category}: {issues}")
   ```

---

### 🚨 Issue 8: Endpoint builder parameter errors

**Error Message:**
```python
ValueError: Missing required path parameters: ['id']
```

**Cause:** Using endpoint builder without providing required path parameters.

**Solutions:**

1. **Check endpoint path template:**
   ```python
   from API.v2.constants.ApiEndpoints import ApiEndpoints
   
   endpoint = ApiEndpoints.WORKPIECE_GET
   print(f"Path template: {endpoint.path}")  # /api/v2/workpieces/{id}
   print("Requires 'id' parameter")
   ```

2. **Provide required parameters:**
   ```python
   from API.v2.utils.EndpointBuilder import build_url
   
   # ❌ Wrong - missing required parameter
   try:
       url = build_url(ApiEndpoints.WORKPIECE_GET)
   except ValueError as e:
       print(f"Error: {e}")
   
   # ✅ Correct - provide required parameter
   url = build_url(ApiEndpoints.WORKPIECE_GET, id="wp_12345")
   print(f"Built URL: {url}")  # /api/v2/workpieces/wp_12345
   ```

3. **Use typed builders for complex requests:**
   ```python
   from API.v2.utils.EndpointBuilder import create_builder
   
   builder = create_builder(user_id="admin", session_token="token123")
   
   # Builder handles parameter validation automatically
   request = builder.workpiece_get_request("wp_12345")
   print(f"Complete request: {request}")
   ```

---

### 🚨 Issue 9: Legacy endpoint mapping not working

**Error Message:**
```python
{"success": False, "message": "Unknown legacy endpoint: custom/legacy/path"}
```

**Cause:** Custom legacy endpoint not included in centralized mapping.

**Solutions:**

1. **Check if mapping exists:**
   ```python
   from API.v2.constants.ApiEndpoints import LegacyMapping
   
   legacy_path = "custom/legacy/path"
   if legacy_path in LegacyMapping.LEGACY_TO_V2_ENDPOINT_MAPPING:
       v2_endpoint = LegacyMapping.LEGACY_TO_V2_ENDPOINT_MAPPING[legacy_path]
       print(f"✅ Maps to: {v2_endpoint.path}")
   else:
       print(f"❌ No mapping found for: {legacy_path}")
       print("Available mappings:")
       for path in sorted(LegacyMapping.LEGACY_TO_V2_ENDPOINT_MAPPING.keys()):
           print(f"  {path}")
   ```

2. **Add custom mapping to centralized constants:**
   ```python
   # In ApiEndpoints.py, add to LegacyMapping class:
   
   class LegacyMapping:
       LEGACY_TO_V2_ENDPOINT_MAPPING = {
           # ... existing mappings ...
           "custom/legacy/path": ApiEndpoints.CUSTOM_ENDPOINT,
           "another/legacy/path": ApiEndpoints.ANOTHER_ENDPOINT,
       }
   ```

3. **Verify mapping works:**
   ```python
   from API.v2.endpoints.EndpointRegistry import get_v2_endpoint
   
   v2_endpoint = get_v2_endpoint("custom/legacy/path")
   if v2_endpoint:
       print(f"✅ Legacy mapping works: {v2_endpoint.path}")
   else:
       print("❌ Legacy mapping failed")
   ```

---

### 🚨 Issue 10: Endpoint documentation generation fails

**Error Message:**
```python
AttributeError: 'NoneType' object has no attribute 'path'
```

**Cause:** Some endpoints in constants are None or malformed.

**Solutions:**

1. **Debug endpoint definitions:**
   ```python
   from API.v2.constants.ApiEndpoints import ApiEndpoints
   
   print("🔍 Checking all endpoint definitions:")
   for attr_name in sorted(dir(ApiEndpoints)):
       if attr_name.startswith('_'):
           continue
       
       endpoint = getattr(ApiEndpoints, attr_name)
       if endpoint is None:
           print(f"❌ {attr_name}: None")
       elif not hasattr(endpoint, 'path'):
           print(f"❌ {attr_name}: Not an Endpoint object - {type(endpoint)}")
       else:
           print(f"✅ {attr_name}: {endpoint.path}")
   ```

2. **Fix malformed endpoint definitions:**
   ```python
   # ❌ Wrong - endpoint is None
   BROKEN_ENDPOINT = None
   
   # ❌ Wrong - not an Endpoint object
   BROKEN_ENDPOINT = "/api/v2/broken"
   
   # ✅ Correct - proper Endpoint object
   FIXED_ENDPOINT = Endpoint(
       path="/api/v2/fixed/endpoint",
       method=HttpMethod.POST,
       description="Properly defined endpoint",
       requires_auth=True,
       rate_limited=True
   )
   ```

3. **Generate documentation safely:**
   ```python
   from API.v2.utils.EndpointValidator import EndpointValidator
   
   try:
       validator = EndpointValidator()
       docs = validator.generate_documentation()
       print("✅ Documentation generated successfully")
       print(f"Length: {len(docs)} characters")
   except Exception as e:
       print(f"❌ Documentation generation failed: {e}")
       
       # Debug which endpoint is causing the issue
       results = validator.validate_all_endpoints()
       for name, result in results.items():
           if not result.is_valid:
               print(f"Invalid endpoint {name}: {result.issues}")
   ```

---

## Advanced Debugging for Centralized Endpoints

### Endpoint Constants Diagnostics

```python
def diagnose_endpoint_constants():
    """Comprehensive diagnosis of endpoint constants."""
    from API.v2.constants.ApiEndpoints import ApiEndpoints, EndpointGroups, HttpMethod
    
    print("🔧 Endpoint Constants Diagnostics")
    print("=" * 50)
    
    # Check ApiEndpoints class
    endpoint_count = 0
    invalid_endpoints = []
    
    for attr_name in dir(ApiEndpoints):
        if attr_name.startswith('_'):
            continue
        
        endpoint = getattr(ApiEndpoints, attr_name)
        
        if endpoint is None:
            invalid_endpoints.append(f"{attr_name}: None")
        elif not hasattr(endpoint, 'path'):
            invalid_endpoints.append(f"{attr_name}: Not Endpoint object")
        else:
            endpoint_count += 1
            
            # Validate endpoint structure
            required_attrs = ['path', 'method', 'description', 'requires_auth', 'rate_limited']
            missing_attrs = [attr for attr in required_attrs if not hasattr(endpoint, attr)]
            
            if missing_attrs:
                invalid_endpoints.append(f"{attr_name}: Missing {missing_attrs}")
    
    print(f"✅ Valid endpoints: {endpoint_count}")
    
    if invalid_endpoints:
        print(f"❌ Invalid endpoints: {len(invalid_endpoints)}")
        for invalid in invalid_endpoints:
            print(f"   {invalid}")
    
    # Check EndpointGroups
    print(f"\n📁 Endpoint Groups:")
    for group_name in dir(EndpointGroups):
        if group_name.startswith('_'):
            continue
        
        group = getattr(EndpointGroups, group_name)
        if isinstance(group, list):
            print(f"   {group_name}: {len(group)} endpoints")
        else:
            print(f"   ❌ {group_name}: Not a list - {type(group)}")
    
    # Check HttpMethod enum
    print(f"\n🔧 HTTP Methods: {list(HttpMethod)}")
    
    return endpoint_count, invalid_endpoints

# Run diagnostics
if __name__ == "__main__":
    valid_count, invalid_list = diagnose_endpoint_constants()
    if not invalid_list:
        print("\n🎉 All endpoint constants are valid!")
    else:
        print(f"\n⚠️  Found {len(invalid_list)} issues that need fixing.")
```

### Endpoint Builder Testing Utility

```python
def test_endpoint_builder():
    """Test endpoint builder with all endpoints."""
    from API.v2.utils.EndpointBuilder import create_builder
    from API.v2.constants.ApiEndpoints import ApiEndpoints
    
    builder = create_builder(user_id="test", session_token="test_token")
    
    print("🧪 Testing Endpoint Builder")
    print("=" * 40)
    
    # Test endpoints that require path parameters
    parameterized_endpoints = {
        'WORKPIECE_GET': {'id': 'wp_test'},
        'WORKPIECE_UPDATE': {'id': 'wp_test'},
        'WORKPIECE_DELETE': {'id': 'wp_test'},
        'WORKPIECE_EXECUTE': {'id': 'wp_test'},
    }
    
    for endpoint_name, params in parameterized_endpoints.items():
        if hasattr(ApiEndpoints, endpoint_name):
            endpoint = getattr(ApiEndpoints, endpoint_name)
            try:
                url = builder.builder.build_url(endpoint, path_params=params)
                print(f"✅ {endpoint_name}: {url}")
            except Exception as e:
                print(f"❌ {endpoint_name}: {e}")
    
    # Test endpoints without parameters
    simple_endpoints = [
        'AUTH_LOGIN', 'SYSTEM_START', 'ROBOT_STATUS', 
        'CAMERA_STREAM', 'WORKPIECES_LIST', 'SETTINGS_ROBOT_GET'
    ]
    
    for endpoint_name in simple_endpoints:
        if hasattr(ApiEndpoints, endpoint_name):
            endpoint = getattr(ApiEndpoints, endpoint_name)
            try:
                url = builder.builder.build_url(endpoint)
                print(f"✅ {endpoint_name}: {url}")
            except Exception as e:
                print(f"❌ {endpoint_name}: {e}")

# Run builder tests
if __name__ == "__main__":
    test_endpoint_builder()
```

### Legacy Mapping Validator

```python
def validate_legacy_mappings():
    """Validate all legacy endpoint mappings."""
    from API.v2.constants.ApiEndpoints import LegacyMapping, ApiEndpoints
    
    print("🔄 Legacy Mapping Validation")
    print("=" * 35)
    
    valid_mappings = 0
    invalid_mappings = []
    
    for legacy_path, v2_endpoint in LegacyMapping.LEGACY_TO_V2_ENDPOINT_MAPPING.items():
        if v2_endpoint is None:
            invalid_mappings.append(f"{legacy_path}: Maps to None")
        elif not hasattr(v2_endpoint, 'path'):
            invalid_mappings.append(f"{legacy_path}: Invalid v2 endpoint")
        elif not v2_endpoint.path.startswith('/api/v2/'):
            invalid_mappings.append(f"{legacy_path}: v2 path doesn't start with /api/v2/")
        else:
            valid_mappings += 1
            print(f"✅ {legacy_path} → {v2_endpoint.path}")
    
    print(f"\nSummary: {valid_mappings} valid mappings")
    
    if invalid_mappings:
        print(f"❌ {len(invalid_mappings)} invalid mappings:")
        for invalid in invalid_mappings:
            print(f"   {invalid}")
    
    return valid_mappings, invalid_mappings

# Run legacy validation
if __name__ == "__main__":
    validate_legacy_mappings()
```

This troubleshooting guide should help you resolve most common issues when working with the API v2 system, including the new centralized endpoint features. If you encounter issues not covered here, use the debugging utilities provided to gather more information about the specific problem.