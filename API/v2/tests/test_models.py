"""
Test suite for API v2 models.
Tests serialization, validation, and type safety.
"""
import unittest
from datetime import datetime

from API.v2.models.BaseModel import BaseModel, ApiResponse
from API.v2.models.Authentication import LoginRequest, LoginResponse, UserInfo
from API.v2.models.Robot import (
    JogRequest, MoveToPositionRequest, Position3D, CalibrationRequest,
    Axis, Direction, RobotPosition
)
from API.v2.models.Workpiece import (
    Workpiece, WorkpieceMetadata, Contour, SprayPattern,
    SaveWorkpieceRequest, WorkpieceStatus
)


class TestBaseModel(unittest.TestCase):
    """Test base model functionality."""

    def test_api_response_success(self):
        """Test successful API response creation."""
        response = ApiResponse.success_response("Operation completed", {"result": "success"})
        
        self.assertTrue(response.success)
        self.assertEqual(response.message, "Operation completed")
        self.assertEqual(response.data["result"], "success")
        self.assertIsNotNone(response.timestamp)

    def test_api_response_error(self):
        """Test error API response creation."""
        errors = {"field1": "Invalid value", "field2": "Required field missing"}
        response = ApiResponse.error_response("Validation failed", errors)
        
        self.assertFalse(response.success)
        self.assertEqual(response.message, "Validation failed")
        self.assertEqual(response.errors, errors)

    def test_serialization(self):
        """Test model serialization and deserialization."""
        response = ApiResponse.success_response("Test", {"key": "value"})
        
        # Test to_dict
        data_dict = response.to_dict()
        self.assertIsInstance(data_dict, dict)
        self.assertTrue(data_dict["success"])
        
        # Test to_json
        json_str = response.to_json()
        self.assertIsInstance(json_str, str)
        self.assertIn("success", json_str)
        
        # Test from_dict
        restored = ApiResponse.from_dict(data_dict)
        self.assertEqual(restored.success, response.success)
        self.assertEqual(restored.message, response.message)
        
        # Test from_json
        restored_from_json = ApiResponse.from_json(json_str)
        self.assertEqual(restored_from_json.success, response.success)


class TestAuthenticationModels(unittest.TestCase):
    """Test authentication models."""

    def test_login_request_validation(self):
        """Test login request validation."""
        # Valid request
        valid_request = LoginRequest(
            user_id="123",
            password="password",
            request_id="req_1",
            timestamp=datetime.now().isoformat()
        )
        self.assertTrue(valid_request.validate())
        
        # Invalid user_id (not numeric)
        invalid_request = LoginRequest(
            user_id="not_numeric",
            password="password",
            request_id="req_2",
            timestamp=datetime.now().isoformat()
        )
        self.assertFalse(invalid_request.validate())
        
        # Empty password
        empty_password = LoginRequest(
            user_id="123",
            password="",
            request_id="req_3",
            timestamp=datetime.now().isoformat()
        )
        self.assertFalse(empty_password.validate())

    def test_user_info_model(self):
        """Test user info model."""
        user = UserInfo(
            id=1,
            first_name="John",
            last_name="Doe",
            role="Admin"
        )
        
        self.assertEqual(user.full_name, "John Doe")
        
        # Test serialization
        data = user.to_dict()
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["first_name"], "John")
        
        # Test deserialization
        restored = UserInfo.from_dict(data)
        self.assertEqual(restored.full_name, "John Doe")

    def test_login_response_creation(self):
        """Test login response factory methods."""
        user = UserInfo(id=1, first_name="Test", last_name="User", role="Operator")
        
        # Test successful response
        success_response = LoginResponse.authenticated(user, "token123", "2024-12-08T18:00:00")
        self.assertTrue(success_response.success)
        self.assertEqual(success_response.user.id, 1)
        self.assertEqual(success_response.session_token, "token123")
        
        # Test failed response
        failed_response = LoginResponse.failed("invalid_password")
        self.assertFalse(failed_response.success)
        self.assertEqual(failed_response.errors["auth"], "invalid_password")


class TestRobotModels(unittest.TestCase):
    """Test robot operation models."""

    def test_position_3d(self):
        """Test 3D position model."""
        position = Position3D(x=100.0, y=200.0, z=50.0, rx=0.0, ry=0.0, rz=90.0)
        
        # Test to_list conversion
        pos_list = position.to_list()
        expected = [100.0, 200.0, 50.0, 0.0, 0.0, 90.0]
        self.assertEqual(pos_list, expected)
        
        # Test serialization
        data = position.to_dict()
        restored = Position3D.from_dict(data)
        self.assertEqual(restored.x, 100.0)
        self.assertEqual(restored.rz, 90.0)

    def test_jog_request_validation(self):
        """Test jog request validation."""
        # Valid request
        valid_jog = JogRequest(
            axis=Axis.X,
            direction=Direction.POSITIVE,
            step_size=10.0,
            request_id="jog_1",
            timestamp=datetime.now().isoformat()
        )
        self.assertTrue(valid_jog.validate())
        
        # Invalid step size (negative)
        invalid_jog = JogRequest(
            axis=Axis.Y,
            direction=Direction.NEGATIVE,
            step_size=-5.0,
            request_id="jog_2",
            timestamp=datetime.now().isoformat()
        )
        self.assertFalse(invalid_jog.validate())
        
        # Zero step size
        zero_step = JogRequest(
            axis=Axis.Z,
            direction=Direction.POSITIVE,
            step_size=0.0,
            request_id="jog_3",
            timestamp=datetime.now().isoformat()
        )
        self.assertFalse(zero_step.validate())

    def test_move_to_position_request(self):
        """Test move to position request."""
        move_request = MoveToPositionRequest(
            position=RobotPosition.HOME,
            velocity=50.0,
            acceleration=25.0,
            request_id="move_1",
            timestamp=datetime.now().isoformat()
        )
        
        # Test serialization
        data = move_request.to_dict()
        self.assertEqual(data["position"], "home")
        self.assertEqual(data["velocity"], 50.0)
        
        # Test deserialization
        restored = MoveToPositionRequest.from_dict(data)
        self.assertEqual(restored.position, RobotPosition.HOME)

    def test_enum_serialization(self):
        """Test enum serialization in robot models."""
        jog_request = JogRequest(
            axis=Axis.X,
            direction=Direction.POSITIVE,
            step_size=5.0
        )
        
        # Enums should serialize to their string values
        data = jog_request.to_dict()
        self.assertEqual(data["axis"], "X")
        self.assertEqual(data["direction"], "positive")
        
        # Should deserialize back to enums
        restored = JogRequest.from_dict(data)
        self.assertEqual(restored.axis, Axis.X)
        self.assertEqual(restored.direction, Direction.POSITIVE)


class TestWorkpieceModels(unittest.TestCase):
    """Test workpiece models."""

    def test_contour_validation(self):
        """Test contour validation."""
        # Valid contour
        valid_contour = Contour(
            points=[[0, 0], [100, 0], [100, 100], [0, 100]],
            closed=True
        )
        self.assertTrue(valid_contour.validate())
        
        # Invalid contour (too few points)
        invalid_contour = Contour(
            points=[[0, 0], [100, 0]],  # Only 2 points
            closed=True
        )
        self.assertFalse(invalid_contour.validate())
        
        # Invalid point format
        bad_format = Contour(
            points=[[0, 0, 0], [100, 0], [100, 100]],  # 3D point in 2D contour
            closed=True
        )
        self.assertFalse(bad_format.validate())

    def test_spray_pattern_validation(self):
        """Test spray pattern validation."""
        valid_contour = Contour(points=[[0, 0], [10, 0], [10, 10], [0, 10]], closed=True)
        
        # Valid spray pattern
        valid_pattern = SprayPattern(
            contour_paths=[valid_contour],
            fill_paths=[],
            spray_speed=2.0,
            spray_pressure=1.5
        )
        self.assertTrue(valid_pattern.validate())
        
        # Invalid spray speed
        invalid_speed = SprayPattern(
            contour_paths=[valid_contour],
            spray_speed=0.0,  # Invalid speed
            spray_pressure=1.5
        )
        self.assertFalse(invalid_speed.validate())
        
        # Invalid pressure
        invalid_pressure = SprayPattern(
            contour_paths=[valid_contour],
            spray_speed=2.0,
            spray_pressure=15.0  # Too high pressure
        )
        self.assertFalse(invalid_pressure.validate())

    def test_workpiece_metadata_validation(self):
        """Test workpiece metadata validation."""
        # Valid metadata
        valid_metadata = WorkpieceMetadata(
            name="Test Part",
            description="Test description",
            thickness=4.0,
            material_type="Plastic"
        )
        self.assertTrue(valid_metadata.validate())
        
        # Invalid name (empty)
        invalid_name = WorkpieceMetadata(
            name="",
            thickness=4.0
        )
        self.assertFalse(invalid_name.validate())
        
        # Invalid thickness
        invalid_thickness = WorkpieceMetadata(
            name="Test Part",
            thickness=0.0  # Zero thickness
        )
        self.assertFalse(invalid_thickness.validate())

    def test_complete_workpiece_validation(self):
        """Test complete workpiece validation."""
        # Create valid components
        metadata = WorkpieceMetadata(name="Test Part", thickness=4.0)
        contour = Contour(points=[[0, 0], [100, 0], [100, 100], [0, 100]], closed=True)
        spray_pattern = SprayPattern(
            contour_paths=[contour],
            spray_speed=2.0,
            spray_pressure=1.5
        )
        
        # Valid workpiece
        valid_workpiece = Workpiece(
            metadata=metadata,
            external_contour=contour,
            spray_pattern=spray_pattern,
            status=WorkpieceStatus.READY,
            contour_area=10000.0
        )
        self.assertTrue(valid_workpiece.validate())
        
        # Invalid workpiece (negative area)
        invalid_workpiece = Workpiece(
            metadata=metadata,
            external_contour=contour,
            spray_pattern=spray_pattern,
            status=WorkpieceStatus.READY,
            contour_area=-100.0  # Negative area
        )
        self.assertFalse(invalid_workpiece.validate())

    def test_workpiece_serialization(self):
        """Test workpiece serialization with nested objects."""
        metadata = WorkpieceMetadata(name="Serialization Test", thickness=5.0)
        contour = Contour(points=[[0, 0], [50, 0], [50, 50], [0, 50]], closed=True)
        
        workpiece = Workpiece(
            metadata=metadata,
            external_contour=contour,
            status=WorkpieceStatus.DRAFT
        )
        
        # Test serialization
        json_str = workpiece.to_json()
        self.assertIsInstance(json_str, str)
        self.assertIn("Serialization Test", json_str)
        
        # Test deserialization
        restored = Workpiece.from_json(json_str)
        self.assertEqual(restored.metadata.name, "Serialization Test")
        self.assertEqual(restored.status, WorkpieceStatus.DRAFT)
        self.assertEqual(len(restored.external_contour.points), 4)


class TestModelEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def test_invalid_json_handling(self):
        """Test handling of invalid JSON."""
        with self.assertRaises(Exception):
            LoginRequest.from_json("invalid json")

    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        incomplete_data = {"user_id": "123"}  # Missing password
        
        # This should not raise an exception but create object with defaults
        request = LoginRequest.from_dict(incomplete_data)
        self.assertEqual(request.user_id, "123")
        # password should be None or empty, making validation fail
        self.assertFalse(request.validate())

    def test_extra_fields_ignored(self):
        """Test that extra fields are ignored during deserialization."""
        data_with_extra = {
            "user_id": "123",
            "password": "pass",
            "extra_field": "should_be_ignored",
            "another_extra": 42
        }
        
        request = LoginRequest.from_dict(data_with_extra)
        self.assertEqual(request.user_id, "123")
        self.assertEqual(request.password, "pass")
        # Extra fields should not cause errors

    def test_none_values_handling(self):
        """Test handling of None values."""
        user = UserInfo(id=1, first_name="Test", last_name=None, role="Admin")
        
        # Should handle None values gracefully
        data = user.to_dict()
        self.assertIsNone(data["last_name"])
        
        restored = UserInfo.from_dict(data)
        self.assertIsNone(restored.last_name)


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)