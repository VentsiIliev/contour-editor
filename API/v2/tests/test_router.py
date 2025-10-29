"""
Test suite for API v2 request router.
Tests routing, handler registration, legacy compatibility, and error handling.
"""
import unittest
from unittest.mock import Mock, patch

from API.v2.handlers.ModernRequestRouter import RequestRouter
from API.v2.endpoints.EndpointRegistry import EndpointRegistry
from API.v2.models.Authentication import LoginRequest, LoginResponse, UserInfo
from API.v2.models.Robot import JogRequest, Axis, Direction
from API.v2.models.BaseModel import ApiResponse


class TestRequestRouter(unittest.TestCase):
    """Test the modern request router functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.router = RequestRouter()
        
        # Setup mock handlers
        self.mock_login_handler = Mock()
        self.mock_jog_handler = Mock()
        
        self.router.register_handler("AUTH_LOGIN", self.mock_login_handler)
        self.router.register_handler("ROBOT_JOG", self.mock_jog_handler)

    def test_handler_registration(self):
        """Test handler registration and retrieval."""
        # Check handlers are registered
        self.assertIn("AUTH_LOGIN", self.router.handlers)
        self.assertIn("ROBOT_JOG", self.router.handlers)
        
        # Test registering new handler
        mock_system_handler = Mock()
        self.router.register_handler("SYSTEM_START", mock_system_handler)
        self.assertIn("SYSTEM_START", self.router.handlers)

    def test_v2_endpoint_routing(self):
        """Test routing to v2 endpoints."""
        # Setup mock response
        expected_response = LoginResponse.authenticated(
            UserInfo(id=1, first_name="Test", last_name="User", role="Admin"),
            "token123",
            "2024-12-08T18:00:00"
        )
        self.mock_login_handler.return_value = expected_response.to_dict()
        
        # Test v2 login request
        login_data = {
            "user_id": "admin",
            "password": "password",
            "request_id": "req_123",
            "timestamp": "2024-12-08T10:00:00"
        }
        
        response = self.router.route_request("/api/v2/auth/login", "POST", login_data)
        
        # Verify handler was called
        self.mock_login_handler.assert_called_once()
        
        # Verify response
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["user"]["first_name"], "Test")

    def test_legacy_endpoint_routing(self):
        """Test routing of legacy endpoints."""
        # Setup mock response
        self.mock_login_handler.return_value = LoginResponse.authenticated(
            UserInfo(id=2, first_name="Legacy", last_name="User", role="Admin"),
            "legacy_token",
            "2024-12-08T18:00:00"
        ).to_dict()
        
        # Test legacy login format
        response = self.router.route_request("login", "POST", ["admin", "password"])
        
        # Verify handler was called
        self.mock_login_handler.assert_called_once()
        
        # Check that legacy data was converted
        call_args = self.mock_login_handler.call_args[0][0]
        self.assertEqual(call_args.user_id, "admin")
        self.assertEqual(call_args.password, "password")

    def test_robot_jog_routing(self):
        """Test robot jog request routing."""
        # Setup mock response
        self.mock_jog_handler.return_value = {"success": True, "message": "Jog completed"}
        
        # Test v2 jog request
        jog_data = {
            "axis": "X",
            "direction": "positive", 
            "step_size": 10.0,
            "request_id": "jog_123",
            "timestamp": "2024-12-08T10:00:00"
        }
        
        response = self.router.route_request("/api/v2/robot/jog", "POST", jog_data)
        
        # Verify handler was called
        self.mock_jog_handler.assert_called_once()
        
        # Verify response
        self.assertTrue(response["success"])

    def test_legacy_robot_jog_conversion(self):
        """Test legacy robot jog request conversion."""
        self.mock_jog_handler.return_value = {"success": True, "message": "Legacy jog completed"}
        
        # Test legacy jog format
        response = self.router.route_request("robot/jog/Y/Minus", "POST", 5.0)
        
        # Verify handler was called
        self.mock_jog_handler.assert_called_once()
        
        # Check converted data
        call_args = self.mock_jog_handler.call_args[0][0]
        self.assertEqual(call_args.axis, "Y")
        self.assertEqual(call_args.direction, "negative") 
        self.assertEqual(call_args.step_size, 5.0)

    def test_endpoint_not_found(self):
        """Test handling of unknown endpoints."""
        response = self.router.route_request("/api/v2/unknown/endpoint", "GET", {})
        
        self.assertFalse(response["success"])
        self.assertIn("Endpoint not found", response["message"])

    def test_handler_not_registered(self):
        """Test handling when endpoint exists but no handler is registered."""
        # This should theoretically not happen in practice, but test edge case
        response = self.router.route_request("/api/v2/system/status", "GET", {})
        
        self.assertFalse(response["success"])
        self.assertIn("No handler registered", response["message"])

    def test_invalid_http_method(self):
        """Test handling of invalid HTTP methods."""
        response = self.router.route_request("/api/v2/auth/login", "INVALID", {})
        
        self.assertFalse(response["success"])
        self.assertIn("Unsupported HTTP method", response["message"])

    def test_handler_exception(self):
        """Test handling of exceptions in handlers."""
        # Setup handler to raise exception
        self.mock_login_handler.side_effect = Exception("Handler error")
        
        response = self.router.route_request("/api/v2/auth/login", "POST", {
            "user_id": "test",
            "password": "test"
        })
        
        self.assertFalse(response["success"])
        self.assertIn("Handler execution failed", response["message"])

    def test_request_validation_success(self):
        """Test successful request validation."""
        self.mock_jog_handler.return_value = {"success": True, "message": "Validated and processed"}
        
        # Valid jog request
        jog_data = {
            "axis": "Z",
            "direction": "positive",
            "step_size": 15.0,
            "request_id": "valid_req",
            "timestamp": "2024-12-08T10:00:00"
        }
        
        response = self.router.route_request("/api/v2/robot/jog", "POST", jog_data)
        
        self.assertTrue(response["success"])
        self.mock_jog_handler.assert_called_once()

    def test_request_validation_failure(self):
        """Test request validation failure."""
        # Invalid jog request (negative step size)
        invalid_jog_data = {
            "axis": "X",
            "direction": "positive",
            "step_size": -5.0,  # Invalid
            "request_id": "invalid_req",
            "timestamp": "2024-12-08T10:00:00"
        }
        
        response = self.router.route_request("/api/v2/robot/jog", "POST", invalid_jog_data)
        
        # Should fail validation
        self.assertFalse(response["success"])
        self.assertIn("validation failed", response["message"].lower())

    def test_legacy_data_conversion_edge_cases(self):
        """Test edge cases in legacy data conversion."""
        # Test with no data
        self.mock_login_handler.return_value = {"success": False, "message": "No data"}
        response = self.router.route_request("login", "POST", None)
        self.assertFalse(response["success"])
        
        # Test with insufficient data
        response = self.router.route_request("login", "POST", ["only_username"])
        self.assertFalse(response["success"])
        
        # Test with extra data (should still work)
        self.mock_login_handler.return_value = {"success": True, "message": "Success"}
        response = self.router.route_request("login", "POST", ["user", "pass", "extra", "data"])
        # Should still call handler with first two parameters
        self.mock_login_handler.assert_called()

    def test_response_format_consistency(self):
        """Test that all responses follow consistent format."""
        # Test successful response
        self.mock_login_handler.return_value = {"success": True, "message": "Login successful"}
        response = self.router.route_request("/api/v2/auth/login", "POST", {
            "user_id": "test", "password": "test"
        })
        
        # Check response structure
        self.assertIn("success", response)
        self.assertIn("message", response)
        self.assertIn("timestamp", response)
        self.assertIsInstance(response["success"], bool)
        self.assertIsInstance(response["message"], str)
        
        # Test error response
        response = self.router.route_request("/api/v2/nonexistent", "POST", {})
        
        # Check error response structure
        self.assertIn("success", response)
        self.assertIn("message", response)
        self.assertIn("timestamp", response)
        self.assertFalse(response["success"])

    def test_endpoint_info_retrieval(self):
        """Test endpoint information retrieval."""
        info = self.router.get_endpoint_info()
        
        self.assertEqual(info["api_version"], "2.0")
        self.assertGreater(info["total_endpoints"], 0)
        self.assertIn("endpoints", info)
        self.assertIsInstance(info["endpoints"], list)
        
        # Check endpoint structure
        if info["endpoints"]:
            endpoint = info["endpoints"][0]
            self.assertIn("name", endpoint)
            self.assertIn("path", endpoint)
            self.assertIn("method", endpoint)
            self.assertIn("description", endpoint)
            self.assertIn("handler_registered", endpoint)


class TestEndpointRegistry(unittest.TestCase):
    """Test the endpoint registry functionality."""

    def test_endpoint_registry_completeness(self):
        """Test that endpoint registry has all expected endpoints."""
        endpoints = EndpointRegistry.get_all_endpoints()
        
        # Check that we have endpoints for all major categories
        endpoint_names = list(endpoints.keys())
        
        # Authentication endpoints
        self.assertIn("AUTH_LOGIN", endpoint_names)
        self.assertIn("AUTH_LOGOUT", endpoint_names)
        
        # System endpoints
        self.assertIn("SYSTEM_START", endpoint_names)
        self.assertIn("SYSTEM_STOP", endpoint_names)
        
        # Robot endpoints
        self.assertIn("ROBOT_JOG", endpoint_names)
        self.assertIn("ROBOT_CALIBRATE", endpoint_names)
        
        # Workpiece endpoints
        self.assertIn("WORKPIECES_LIST", endpoint_names)
        self.assertIn("WORKPIECES_CREATE", endpoint_names)

    def test_endpoint_path_consistency(self):
        """Test that endpoint paths follow consistent patterns."""
        endpoints = EndpointRegistry.get_all_endpoints()
        
        for name, endpoint in endpoints.items():
            # All v2 endpoints should start with /api/v2/
            self.assertTrue(endpoint.path.startswith("/api/v2/"))
            
            # Paths should not end with /
            self.assertFalse(endpoint.path.endswith("/"))
            
            # Paths should use lowercase and hyphens, not underscores
            path_parts = endpoint.path.split("/")
            for part in path_parts[3:]:  # Skip /api/v2/
                if "{" not in part:  # Skip template parameters
                    self.assertNotIn("_", part, f"Path {endpoint.path} contains underscore")

    def test_legacy_mapping_coverage(self):
        """Test that legacy mapping covers important old endpoints."""
        from API.v2.endpoints.EndpointRegistry import LEGACY_TO_V2_MAPPING, get_v2_endpoint
        
        # Test important legacy endpoints are mapped
        important_legacy = [
            "login",
            "start",
            "robot/jog/X/Plus",
            "robot/move/home", 
            "workpiece/create",
            "workpiece/save"
        ]
        
        for legacy_path in important_legacy:
            v2_endpoint = get_v2_endpoint(legacy_path)
            self.assertIsNotNone(v2_endpoint, f"Legacy path '{legacy_path}' not mapped to v2")

    def test_endpoint_method_appropriateness(self):
        """Test that endpoints use appropriate HTTP methods."""
        endpoints = EndpointRegistry.get_all_endpoints()
        
        for name, endpoint in endpoints.items():
            path = endpoint.path
            method = endpoint.method.value
            
            # GET methods should be for retrieving data
            if method == "GET":
                self.assertTrue(
                    any(word in path for word in ["status", "session", "list"]) or
                    path.endswith("settings") or
                    "/workpieces" == path.split("?")[0],  # List endpoint
                    f"GET method may be inappropriate for {path}"
                )
            
            # POST methods should be for creating or actions
            if method == "POST":
                self.assertTrue(
                    any(word in path for word in ["login", "logout", "start", "stop", "jog", "move", "calibration", "capture", "test"]) or
                    path.endswith("/workpieces") or  # Create workpiece
                    "/execute" in path,
                    f"POST method may be inappropriate for {path}"
                )


if __name__ == '__main__':
    # Run all tests with detailed output
    unittest.main(verbosity=2)