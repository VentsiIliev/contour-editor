# API v2 Testing Guide

## Overview

This guide provides comprehensive testing strategies for the new API v2 system, including unit tests, integration tests, and testing utilities for development.

## Test Structure

```
API/v2/tests/
├── __init__.py
├── test_models.py          # Model validation and serialization tests
├── test_router.py          # Request routing and handler tests
├── test_endpoints.py       # Endpoint registry tests
├── test_integration.py     # Full integration tests
├── conftest.py            # Pytest fixtures
└── utils/
    ├── mock_handlers.py   # Reusable mock handlers
    └── test_data.py       # Test data factories
```

## Running Tests

### Using unittest (Built-in)
```bash
# Run all tests
python -m unittest discover API/v2/tests/ -v

# Run specific test file
python -m unittest API.v2.tests.test_models -v

# Run specific test class
python -m unittest API.v2.tests.test_models.TestAuthenticationModels -v

# Run specific test method
python -m unittest API.v2.tests.test_models.TestAuthenticationModels.test_login_request_validation -v
```

### Using pytest (Recommended)
```bash
# Install pytest if not already installed
pip install pytest pytest-cov

# Run all tests with coverage
pytest API/v2/tests/ --cov=API/v2 --cov-report=html

# Run with verbose output
pytest API/v2/tests/ -v

# Run specific test file
pytest API/v2/tests/test_models.py -v

# Run tests matching pattern
pytest API/v2/tests/ -k "test_login" -v
```

## Test Categories

### 1. Model Tests (`test_models.py`)

Tests for data models, validation, and serialization:

```python
import unittest
from API.v2.models.Authentication import LoginRequest

class TestLoginModel(unittest.TestCase):
    def test_valid_login_request(self):
        """Test valid login request creation and validation."""
        request = LoginRequest(user_id="123", password="pass")
        self.assertTrue(request.validate())
        
    def test_invalid_user_id(self):
        """Test validation fails for non-numeric user ID."""
        request = LoginRequest(user_id="not_numeric", password="pass")
        self.assertFalse(request.validate())
        
    def test_serialization_round_trip(self):
        """Test JSON serialization and deserialization."""
        original = LoginRequest(user_id="456", password="secret")
        json_str = original.to_json()
        restored = LoginRequest.from_json(json_str)
        
        self.assertEqual(restored.user_id, original.user_id)
        self.assertEqual(restored.password, original.password)
```

### 2. Router Tests (`test_router.py`)

Tests for request routing, handler registration, and legacy compatibility:

```python
import unittest
from unittest.mock import Mock
from API.v2.handlers.ModernRequestRouter import RequestRouter

class TestRequestRouter(unittest.TestCase):
    def setUp(self):
        self.router = RequestRouter()
        self.mock_handler = Mock(return_value={"success": True, "message": "Test"})
        self.router.register_handler("AUTH_LOGIN", self.mock_handler)
        
    def test_v2_endpoint_routing(self):
        """Test routing to v2 endpoints."""
        response = self.router.route_request("/api/v2/auth/login", "POST", {
            "user_id": "test", "password": "test"
        })
        
        self.assertTrue(response["success"])
        self.mock_handler.assert_called_once()
        
    def test_legacy_compatibility(self):
        """Test legacy endpoint compatibility."""
        response = self.router.route_request("login", "POST", ["user", "pass"])
        
        # Should convert legacy format and call handler
        self.mock_handler.assert_called_once()
        call_args = self.mock_handler.call_args[0][0]
        self.assertEqual(call_args.user_id, "user")
```

### 3. Integration Tests

Full end-to-end tests with real handlers:

```python
import unittest
from API.v2.handlers.ModernRequestRouter import RequestRouter
from API.v2.models.Authentication import LoginRequest, UserInfo

class TestIntegration(unittest.TestCase):
    def setUp(self):
        """Set up integration test environment."""
        self.router = RequestRouter()
        self.setup_real_handlers()
        
    def setup_real_handlers(self):
        """Register real handlers for testing."""
        def login_handler(request):
            # Simplified real login logic
            if request.user_id == "admin" and request.password == "pass":
                user = UserInfo(id=1, first_name="Admin", last_name="User", role="Admin")
                return LoginResponse.authenticated(user, "token", "2024-12-08T18:00:00").to_dict()
            return LoginResponse.failed("invalid_credentials").to_dict()
            
        self.router.register_handler("AUTH_LOGIN", login_handler)
        
    def test_complete_login_flow(self):
        """Test complete login workflow."""
        # Test successful login
        response = self.router.route_request("/api/v2/auth/login", "POST", {
            "user_id": "admin",
            "password": "pass"
        })
        
        self.assertTrue(response["success"])
        self.assertIn("user", response["data"])
        self.assertEqual(response["data"]["user"]["role"], "Admin")
        
        # Test failed login
        response = self.router.route_request("/api/v2/auth/login", "POST", {
            "user_id": "wrong",
            "password": "wrong"
        })
        
        self.assertFalse(response["success"])
        self.assertIn("auth", response["errors"])
```

## Mock Testing Utilities

### Mock Handlers

Create reusable mock handlers for testing:

```python
# tests/utils/mock_handlers.py
from API.v2.models.Authentication import LoginResponse, UserInfo
from API.v2.models.Robot import RobotResponse, RobotStatus, Position3D

class MockHandlers:
    """Collection of mock handlers for testing."""
    
    @staticmethod
    def create_mock_login_handler(success_users=None):
        """Create mock login handler with configurable users."""
        success_users = success_users or {"admin": "pass"}
        
        def handler(request):
            if request.user_id in success_users and success_users[request.user_id] == request.password:
                user = UserInfo(
                    id=1, 
                    first_name="Mock", 
                    last_name="User", 
                    role="Admin"
                )
                return LoginResponse.authenticated(user, "mock_token", "2024-12-08T18:00:00").to_dict()
            return LoginResponse.failed("invalid_credentials").to_dict()
            
        return handler
    
    @staticmethod
    def create_mock_robot_jog_handler():
        """Create mock robot jog handler."""
        def handler(request):
            return RobotResponse.with_status(
                f"Jogged {request.axis} {request.direction} by {request.step_size}mm",
                RobotStatus(
                    position=Position3D(x=100.0, y=200.0, z=50.0),
                    is_moving=False,
                    is_calibrated=True,
                    error_state=False
                )
            ).to_dict()
        return handler
```

### Test Data Factories

Create test data easily:

```python
# tests/utils/test_data.py
from API.v2.models.Authentication import LoginRequest, UserInfo
from API.v2.models.Robot import JogRequest, Axis, Direction
from API.v2.models.Workpiece import Workpiece, WorkpieceMetadata, Contour

class TestDataFactory:
    """Factory for creating test data objects."""
    
    @staticmethod
    def create_login_request(user_id="123", password="password"):
        """Create a valid login request."""
        return LoginRequest(user_id=user_id, password=password)
    
    @staticmethod
    def create_user_info(id=1, first_name="Test", last_name="User", role="Admin"):
        """Create a user info object."""
        return UserInfo(id=id, first_name=first_name, last_name=last_name, role=role)
    
    @staticmethod
    def create_jog_request(axis=Axis.X, direction=Direction.POSITIVE, step_size=10.0):
        """Create a valid jog request."""
        return JogRequest(axis=axis, direction=direction, step_size=step_size)
    
    @staticmethod
    def create_simple_workpiece(name="Test Part"):
        """Create a simple valid workpiece."""
        metadata = WorkpieceMetadata(name=name, thickness=4.0)
        contour = Contour(
            points=[[0, 0], [100, 0], [100, 100], [0, 100]],
            closed=True
        )
        
        return Workpiece(
            metadata=metadata,
            external_contour=contour,
            contour_area=10000.0
        )

# Usage in tests:
class TestWithFactory(unittest.TestCase):
    def test_login_with_factory(self):
        request = TestDataFactory.create_login_request()
        self.assertTrue(request.validate())
```

## Testing Patterns

### 1. Parameterized Tests

Test multiple scenarios efficiently:

```python
import unittest
from parameterized import parameterized
from API.v2.models.Robot import JogRequest, Axis, Direction

class TestJogValidation(unittest.TestCase):
    
    @parameterized.expand([
        (Axis.X, Direction.POSITIVE, 1.0, True),
        (Axis.Y, Direction.NEGATIVE, 50.0, True),
        (Axis.Z, Direction.POSITIVE, 100.0, True),
        (Axis.X, Direction.POSITIVE, 0.0, False),     # Zero step
        (Axis.Y, Direction.NEGATIVE, -5.0, False),    # Negative step
    ])
    def test_jog_validation(self, axis, direction, step_size, should_be_valid):
        """Test jog request validation with various parameters."""
        request = JogRequest(axis=axis, direction=direction, step_size=step_size)
        self.assertEqual(request.validate(), should_be_valid)
```

### 2. Exception Testing

Test error handling:

```python
class TestErrorHandling(unittest.TestCase):
    def test_invalid_json_parsing(self):
        """Test handling of malformed JSON."""
        with self.assertRaises(json.JSONDecodeError):
            LoginRequest.from_json("invalid json")
            
    def test_handler_exception_handling(self):
        """Test router handles handler exceptions gracefully."""
        router = RequestRouter()
        
        def failing_handler(request):
            raise Exception("Handler error")
            
        router.register_handler("AUTH_LOGIN", failing_handler)
        
        response = router.route_request("/api/v2/auth/login", "POST", {})
        
        self.assertFalse(response["success"])
        self.assertIn("execution failed", response["message"])
```

### 3. Mock Testing

Use mocks to isolate components:

```python
from unittest.mock import Mock, patch

class TestWithMocks(unittest.TestCase):
    @patch('API.v2.models.Authentication.datetime')
    def test_timestamp_generation(self, mock_datetime):
        """Test that timestamps are generated correctly."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T12:00:00"
        
        request = LoginRequest(user_id="123", password="pass")
        
        # Should use mocked timestamp
        self.assertEqual(request.timestamp, "2024-01-01T12:00:00")
```

## Performance Testing

### Load Testing

Test API performance under load:

```python
import time
import concurrent.futures
from statistics import mean, stdev

class TestPerformance(unittest.TestCase):
    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        router = RequestRouter()
        
        def mock_handler(request):
            time.sleep(0.01)  # Simulate processing time
            return {"success": True, "message": "Processed"}
            
        router.register_handler("AUTH_LOGIN", mock_handler)
        
        def make_request():
            start_time = time.time()
            response = router.route_request("/api/v2/auth/login", "POST", {
                "user_id": "test", "password": "test"
            })
            end_time = time.time()
            return end_time - start_time, response["success"]
        
        # Test with multiple concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(100)]
            results = [future.result() for future in futures]
        
        times, successes = zip(*results)
        
        # All requests should succeed
        self.assertTrue(all(successes))
        
        # Check performance metrics
        avg_time = mean(times)
        max_time = max(times)
        
        print(f"Average response time: {avg_time:.3f}s")
        print(f"Max response time: {max_time:.3f}s")
        
        # Performance assertions
        self.assertLess(avg_time, 0.1)  # Average under 100ms
        self.assertLess(max_time, 0.5)   # Max under 500ms
```

### Memory Testing

Test memory usage:

```python
import tracemalloc

class TestMemoryUsage(unittest.TestCase):
    def test_memory_usage_during_serialization(self):
        """Test memory usage during model serialization."""
        tracemalloc.start()
        
        # Create large workpiece
        large_contour = Contour(
            points=[[i, i+1] for i in range(1000)],  # 1000 points
            closed=True
        )
        
        workpiece = Workpiece(
            metadata=WorkpieceMetadata(name="Large Workpiece", thickness=4.0),
            external_contour=large_contour
        )
        
        # Measure memory before serialization
        snapshot1 = tracemalloc.take_snapshot()
        
        # Perform serialization
        json_str = workpiece.to_json()
        
        # Measure memory after serialization
        snapshot2 = tracemalloc.take_snapshot()
        
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')
        total_size = sum(stat.size for stat in top_stats)
        
        # Memory usage should be reasonable
        self.assertLess(total_size, 1024 * 1024)  # Less than 1MB
        
        tracemalloc.stop()
```

## Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/api_tests.yml
name: API v2 Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
        
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov parameterized
        
    - name: Run API v2 tests
      run: |
        pytest API/v2/tests/ --cov=API/v2 --cov-report=xml --cov-report=term
        
    - name: Upload coverage
      uses: codecov/codecov-action@v1
      with:
        file: ./coverage.xml
        flags: api-v2
        name: API v2 Coverage
```

### Test Configuration

```python
# conftest.py - pytest configuration
import pytest
from API.v2.handlers.ModernRequestRouter import RequestRouter
from API.v2.tests.utils.mock_handlers import MockHandlers

@pytest.fixture
def router():
    """Create a router with mock handlers for testing."""
    router = RequestRouter()
    
    # Register mock handlers
    router.register_handler("AUTH_LOGIN", MockHandlers.create_mock_login_handler())
    router.register_handler("ROBOT_JOG", MockHandlers.create_mock_robot_jog_handler())
    
    return router

@pytest.fixture
def valid_login_request():
    """Create a valid login request for testing."""
    from API.v2.models.Authentication import LoginRequest
    return LoginRequest(user_id="admin", password="pass")

# Usage in tests:
def test_with_fixtures(router, valid_login_request):
    response = router.route_request("/api/v2/auth/login", "POST", valid_login_request.to_dict())
    assert response["success"]
```

## Testing Best Practices

### 1. Test Naming Convention
```python
# Good test names describe what they test
def test_login_request_validates_numeric_user_id(self):
def test_jog_request_rejects_negative_step_size(self):
def test_workpiece_serialization_preserves_nested_objects(self):

# Bad test names
def test_login(self):
def test_validation(self):
def test_stuff(self):
```

### 2. Test Organization
```python
class TestLoginRequest(unittest.TestCase):
    """Test LoginRequest model specifically."""
    
    def setUp(self):
        """Common setup for all login request tests."""
        self.valid_data = {"user_id": "123", "password": "pass"}
    
    def test_valid_request_passes_validation(self):
        """Test that valid requests pass validation."""
        # Arrange
        request = LoginRequest.from_dict(self.valid_data)
        
        # Act
        is_valid = request.validate()
        
        # Assert
        self.assertTrue(is_valid)
```

### 3. Edge Case Testing
```python
def test_edge_cases(self):
    """Test various edge cases."""
    edge_cases = [
        {"user_id": "", "password": "pass"},           # Empty user ID
        {"user_id": "123", "password": ""},            # Empty password
        {"user_id": "abc", "password": "pass"},        # Non-numeric ID
        {"user_id": "999999999999", "password": "x"},  # Very long ID
    ]
    
    for case in edge_cases:
        with self.subTest(case=case):
            request = LoginRequest.from_dict(case)
            self.assertFalse(request.validate())
```

### 4. Test Data Management
```python
# Use class variables for common test data
class TestConstants:
    VALID_USER_ID = "123"
    VALID_PASSWORD = "password"
    INVALID_USER_ID = "not_numeric"
    
    VALID_JOG_DATA = {
        "axis": "X",
        "direction": "positive",
        "step_size": 10.0
    }

# Use in tests
def test_with_constants(self):
    request = LoginRequest(
        user_id=TestConstants.VALID_USER_ID,
        password=TestConstants.VALID_PASSWORD
    )
    self.assertTrue(request.validate())
```

## Testing Centralized Endpoints

### Testing Endpoint Constants

Test the centralized endpoint system:

```python
import unittest
from API.v2.constants.ApiEndpoints import ApiEndpoints, EndpointGroups, HttpMethod

class TestEndpointConstants(unittest.TestCase):
    def test_all_endpoints_have_required_fields(self):
        """Test that all endpoints have required attributes."""
        for attr_name in dir(ApiEndpoints):
            if attr_name.startswith('_'):
                continue
            
            endpoint = getattr(ApiEndpoints, attr_name)
            if hasattr(endpoint, 'path'):
                # Test required fields
                self.assertIsInstance(endpoint.path, str)
                self.assertIsInstance(endpoint.method, HttpMethod)
                self.assertIsInstance(endpoint.description, str)
                self.assertIsInstance(endpoint.requires_auth, bool)
                self.assertIsInstance(endpoint.rate_limited, bool)
                
                # Test path format
                self.assertTrue(endpoint.path.startswith('/api/v2/'))
                self.assertGreater(len(endpoint.description), 5)
    
    def test_endpoint_groups_consistency(self):
        """Test that endpoint groups contain valid endpoints."""
        for group_name in dir(EndpointGroups):
            if group_name.startswith('_'):
                continue
            
            group = getattr(EndpointGroups, group_name)
            self.assertIsInstance(group, list)
            
            for endpoint in group:
                self.assertHasAttr(endpoint, 'path')
                self.assertHasAttr(endpoint, 'method')
                self.assertTrue(endpoint.path.startswith('/api/v2/'))
    
    def test_no_endpoint_path_duplicates(self):
        """Test that no two endpoints have the same path and method."""
        seen_combinations = set()
        
        for attr_name in dir(ApiEndpoints):
            if attr_name.startswith('_'):
                continue
            
            endpoint = getattr(ApiEndpoints, attr_name)
            if hasattr(endpoint, 'path'):
                combination = (endpoint.path, endpoint.method.value)
                self.assertNotIn(combination, seen_combinations, 
                               f"Duplicate endpoint: {combination}")
                seen_combinations.add(combination)
```

### Testing Endpoint Validation

Test the endpoint validation utilities:

```python
import unittest
from API.v2.utils.EndpointValidator import EndpointValidator, ValidationResult

class TestEndpointValidation(unittest.TestCase):
    def setUp(self):
        self.validator = EndpointValidator()
    
    def test_validate_valid_endpoint(self):
        """Test validation of a valid endpoint."""
        result = self.validator.validate_endpoint("AUTH_LOGIN")
        
        self.assertIsInstance(result, ValidationResult)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.endpoint_name, "AUTH_LOGIN")
        self.assertEqual(len(result.issues), 0)
    
    def test_validate_nonexistent_endpoint(self):
        """Test validation of non-existent endpoint."""
        result = self.validator.validate_endpoint("NONEXISTENT_ENDPOINT")
        
        self.assertFalse(result.is_valid)
        self.assertIn("not found", result.issues[0])
    
    def test_validate_all_endpoints(self):
        """Test validation of all endpoints."""
        results = self.validator.validate_all_endpoints()
        
        self.assertGreater(len(results), 0)
        
        # Count valid endpoints
        valid_count = sum(1 for r in results.values() if r.is_valid)
        total_count = len(results)
        
        # At least 90% should be valid
        self.assertGreaterEqual(valid_count / total_count, 0.9)
    
    def test_consistency_check(self):
        """Test API consistency checking."""
        consistency = self.validator.check_consistency()
        
        # Should have all expected categories
        expected_categories = ['path_conflicts', 'naming_inconsistencies', 
                             'legacy_mapping_issues', 'group_organization']
        for category in expected_categories:
            self.assertIn(category, consistency)
        
        # Should have no path conflicts
        self.assertEqual(len(consistency['path_conflicts']), 0)
    
    def test_documentation_generation(self):
        """Test API documentation generation."""
        docs = self.validator.generate_documentation()
        
        self.assertIsInstance(docs, str)
        self.assertIn("# Industrial Automation API v2", docs)
        self.assertIn("## Authentication Endpoints", docs)
        self.assertIn("## Legacy Compatibility", docs)
    
    def test_openapi_schema_export(self):
        """Test OpenAPI schema export."""
        schema = self.validator.export_openapi_schema()
        
        self.assertIn("openapi", schema)
        self.assertIn("info", schema)
        self.assertIn("paths", schema)
        self.assertEqual(schema["openapi"], "3.0.0")
        self.assertEqual(schema["info"]["version"], "2.0.0")
```

### Testing Endpoint Builders

Test the type-safe endpoint builders:

```python
import unittest
from API.v2.utils.EndpointBuilder import EndpointBuilder, TypedEndpointBuilder, create_builder
from API.v2.constants.ApiEndpoints import ApiEndpoints

class TestEndpointBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = EndpointBuilder()
        self.typed_builder = TypedEndpointBuilder()
    
    def test_build_simple_url(self):
        """Test building URL without parameters."""
        url = self.builder.build_url(ApiEndpoints.AUTH_LOGIN)
        self.assertEqual(url, "/api/v2/auth/login")
    
    def test_build_url_with_path_params(self):
        """Test building URL with path parameters."""
        url = self.builder.build_url(
            ApiEndpoints.WORKPIECE_GET,
            path_params={'id': 'wp_12345'}
        )
        self.assertEqual(url, "/api/v2/workpieces/wp_12345")
    
    def test_build_url_with_query_params(self):
        """Test building URL with query parameters."""
        url = self.builder.build_url(
            ApiEndpoints.WORKPIECES_LIST,
            query_params={'status': 'ready', 'limit': 50}
        )
        self.assertIn("/api/v2/workpieces?", url)
        self.assertIn("status=ready", url)
        self.assertIn("limit=50", url)
    
    def test_missing_path_parameter_error(self):
        """Test error handling for missing path parameters."""
        with self.assertRaises(ValueError) as context:
            self.builder.build_url(ApiEndpoints.WORKPIECE_GET)
        
        self.assertIn("Missing required path parameters", str(context.exception))
    
    def test_typed_login_request(self):
        """Test typed login request building."""
        request = self.typed_builder.login_request("admin", "password")
        
        self.assertEqual(request['url'], "/api/v2/auth/login")
        self.assertEqual(request['method'], "POST")
        self.assertIn('data', request)
        self.assertEqual(request['data']['user_id'], "admin")
        self.assertEqual(request['data']['password'], "password")
    
    def test_typed_robot_jog_request(self):
        """Test typed robot jog request building."""
        request = self.typed_builder.robot_jog_request("X", "positive", 10.0)
        
        self.assertEqual(request['url'], "/api/v2/robot/jog")
        self.assertEqual(request['method'], "POST")
        self.assertEqual(request['data']['axis'], "X")
        self.assertEqual(request['data']['direction'], "positive")
        self.assertEqual(request['data']['step_size'], 10.0)
    
    def test_authenticated_builder(self):
        """Test builder with authentication context."""
        auth_builder = create_builder(user_id="admin", session_token="token123")
        request = auth_builder.login_request("admin", "password")
        
        # Should include user context
        self.assertEqual(request['data']['user_id'], "admin")
        self.assertIn('request_id', request['data'])
        self.assertIn('timestamp', request['data'])

class TestEndpointBuilderIntegration(unittest.TestCase):
    def test_builder_with_router(self):
        """Test endpoint builder integration with router."""
        from API.v2.handlers.ModernRequestRouter import RequestRouter
        
        router = RequestRouter()
        builder = create_builder(user_id="admin")
        
        # Mock handler
        def mock_handler(data):
            return {"success": True, "message": "Builder test successful"}
        
        router.register_handler("AUTH_LOGIN", mock_handler)
        
        # Build request with builder
        request = builder.login_request("admin", "password")
        
        # Send through router
        response = router.route_request(request['url'], request['method'], request['data'])
        
        self.assertTrue(response["success"])
        self.assertEqual(response["message"], "Builder test successful")
```

### Testing Legacy Endpoint Mapping

Test legacy endpoint compatibility:

```python
import unittest
from API.v2.constants.ApiEndpoints import LegacyMapping
from API.v2.endpoints.EndpointRegistry import get_v2_endpoint

class TestLegacyMapping(unittest.TestCase):
    def test_all_legacy_paths_mapped(self):
        """Test that all legacy paths have valid v2 mappings."""
        for legacy_path, v2_endpoint in LegacyMapping.LEGACY_TO_V2_ENDPOINT_MAPPING.items():
            self.assertIsNotNone(v2_endpoint)
            self.assertTrue(v2_endpoint.path.startswith('/api/v2/'))
            self.assertIn(v2_endpoint.method.value, ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
    
    def test_common_legacy_mappings(self):
        """Test common legacy endpoint mappings."""
        test_cases = [
            ("login", "/api/v2/auth/login"),
            ("robot/jog/X/Plus", "/api/v2/robot/jog"),
            ("camera/getLatestFrame", "/api/v2/camera/stream"),
            ("workpiece/getall", "/api/v2/workpieces"),
            ("settings/robot/get", "/api/v2/settings/robot"),
        ]
        
        for legacy_path, expected_v2_path in test_cases:
            v2_endpoint = get_v2_endpoint(legacy_path)
            self.assertIsNotNone(v2_endpoint, f"No mapping for {legacy_path}")
            self.assertEqual(v2_endpoint.path, expected_v2_path)
    
    def test_legacy_path_coverage(self):
        """Test that legacy mappings cover all expected paths."""
        expected_legacy_categories = [
            "login", "robot/", "camera/", "workpiece/", "settings/", "start", "test_run"
        ]
        
        legacy_paths = list(LegacyMapping.LEGACY_TO_V2_ENDPOINT_MAPPING.keys())
        
        for category in expected_legacy_categories:
            matching_paths = [path for path in legacy_paths if category in path]
            self.assertGreater(len(matching_paths), 0, 
                             f"No legacy paths found for category: {category}")
```

## Performance Testing for Endpoints

### Endpoint Performance Tests

```python
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from API.v2.utils.EndpointBuilder import create_builder
from API.v2.utils.EndpointValidator import EndpointValidator

class TestEndpointPerformance(unittest.TestCase):
    def test_endpoint_validation_performance(self):
        """Test endpoint validation performance."""
        validator = EndpointValidator()
        
        start_time = time.time()
        results = validator.validate_all_endpoints()
        end_time = time.time()
        
        validation_time = end_time - start_time
        
        # Should validate all endpoints quickly
        self.assertLess(validation_time, 1.0)  # Less than 1 second
        self.assertGreater(len(results), 50)   # Should have many endpoints
    
    def test_endpoint_builder_performance(self):
        """Test endpoint builder performance."""
        builder = create_builder(user_id="admin", session_token="token123")
        
        start_time = time.time()
        
        # Build many requests
        for i in range(1000):
            request = builder.login_request(f"user_{i}", f"pass_{i}")
            self.assertIn('url', request)
            self.assertIn('method', request)
            self.assertIn('data', request)
        
        end_time = time.time()
        build_time = end_time - start_time
        
        # Should build requests quickly
        self.assertLess(build_time, 0.5)  # Less than 500ms for 1000 requests
        
        # Performance metrics
        requests_per_second = 1000 / build_time
        self.assertGreater(requests_per_second, 2000)  # At least 2000 req/sec
    
    def test_concurrent_endpoint_access(self):
        """Test concurrent access to endpoint constants."""
        from API.v2.constants.ApiEndpoints import ApiEndpoints
        
        def access_endpoints():
            endpoints_accessed = []
            for _ in range(100):
                endpoints_accessed.append(ApiEndpoints.AUTH_LOGIN.path)
                endpoints_accessed.append(ApiEndpoints.ROBOT_JOG.method.value)
                endpoints_accessed.append(ApiEndpoints.WORKPIECE_GET.description)
            return len(endpoints_accessed)
        
        # Test concurrent access
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(access_endpoints) for _ in range(10)]
            results = [future.result() for future in futures]
        
        # All should succeed
        self.assertEqual(len(results), 10)
        self.assertTrue(all(result == 300 for result in results))
```

This testing guide provides comprehensive coverage for testing the API v2 system at all levels, from individual model validation to full integration testing. The new sections specifically cover testing the centralized endpoint system, validation utilities, and builders. The examples can be adapted and extended for your specific testing needs.