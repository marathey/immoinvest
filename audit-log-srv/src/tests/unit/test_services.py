import pytest
from uuid import UUID, uuid4
from datetime import datetime
from app.schemas import AuditLogEntry
from pydantic import ValidationError
from sqlalchemy import inspect


def test_valid_audit_log_entry():
    """Test creating a valid audit log entry"""
    user_id = uuid4()
    entity_id = uuid4()
    
    valid_entry = {
        "service_name": "test-service",
        "service_id": "service-123",
        "user_id": user_id,
        "action_type": "CREATE",
        "entity_type": "user",
        "entity_id": entity_id,
        "previous_data": {"name": "old_name"},
        "new_data": {"name": "new_name"},
        "meta_data": {"ip_address": "127.0.0.1"}
    }
    
    log_entry = AuditLogEntry(**valid_entry)
    
    assert log_entry.service_name == "test-service"
    assert log_entry.service_id == "service-123"
    assert log_entry.user_id == user_id
    assert log_entry.action_type == "CREATE"
    assert log_entry.entity_type == "user"
    assert log_entry.entity_id == entity_id
    assert log_entry.previous_data == {"name": "old_name"}
    assert log_entry.new_data == {"name": "new_name"}
    assert log_entry.meta_data == {"ip_address": "127.0.0.1"}

def test_minimal_valid_audit_log_entry():
    """Test creating a minimal valid audit log entry with only required fields"""
    user_id = uuid4()
    
    minimal_entry = {
        "service_name": "test-service",
        "user_id": user_id,
        "action_type": "READ",
        "entity_type": "document"
    }
    
    log_entry = AuditLogEntry(**minimal_entry)
    
    assert log_entry.service_name == "test-service"
    assert log_entry.user_id == user_id
    assert log_entry.action_type == "READ"
    assert log_entry.entity_type == "document"
    assert log_entry.service_id is None
    assert log_entry.entity_id is None
    assert log_entry.previous_data is None
    assert log_entry.new_data is None
    assert log_entry.meta_data is None

def test_invalid_uuid_fields():
    """Test validation errors for invalid UUID fields"""
    invalid_entry = {
        "service_name": "test-service",
        "user_id": "invalid-uuid",  # Invalid UUID
        "action_type": "CREATE",
        "entity_type": "user",
        "entity_id": "also-invalid-uuid"  # Invalid UUID
    }
    
    with pytest.raises(ValidationError) as exc_info:
        AuditLogEntry(**invalid_entry)
    
    errors = exc_info.value.errors()
    assert len(errors) == 2
    assert any(error["loc"][0] == "user_id" for error in errors)
    assert any(error["loc"][0] == "entity_id" for error in errors)

def test_missing_required_fields():
    """Test validation errors when required fields are missing"""
    invalid_entry = {
        "service_name": "test-service",
        # missing user_id
        "action_type": "DELETE",
        # missing entity_type
    }
    
    with pytest.raises(ValidationError) as exc_info:
        AuditLogEntry(**invalid_entry)
    
    errors = exc_info.value.errors()
    assert len(errors) == 2
    assert any(error["loc"][0] == "user_id" for error in errors)
    assert any(error["loc"][0] == "entity_type" for error in errors)

def test_empty_strings():
    """Test validation with empty strings in required string fields"""
    user_id = uuid4()
    
    invalid_entry = {
        "service_name": "",  # Empty string
        "user_id": user_id,
        "action_type": "",  # Empty string
        "entity_type": ""  # Empty string
    }
    
    log_entry = AuditLogEntry(**invalid_entry)
    assert log_entry.service_name == ""
    assert log_entry.action_type == ""
    assert log_entry.entity_type == ""

def test_invalid_json_data():
    """Test validation for invalid JSON in data fields"""
    user_id = uuid4()
    
    # Create an object that can't be JSON serialized
    class UnserializableObject:
        pass

    invalid_entry = {
        "service_name": "test-service",
        "user_id": user_id,
        "action_type": "UPDATE",
        "entity_type": "user",
        "previous_data": {"key": UnserializableObject()},
        "new_data": {"key": lambda x: x}  # Functions are not JSON serializable
    }
    
    with pytest.raises(ValidationError) as exc_info:
        AuditLogEntry(**invalid_entry)

def test_complex_json_data():
    """Test validation of complex but valid JSON structures"""
    user_id = uuid4()
    
    # Test with nested dictionaries and arrays
    valid_entry = {
        "service_name": "test-service",
        "user_id": user_id,
        "action_type": "UPDATE",
        "entity_type": "user",
        "previous_data": {
            "nested": {
                "array": [1, 2, 3],
                "null": None,
                "number": 42.5,
                "boolean": True,
                "string": "test"
            }
        },
        "new_data": {
            "list": list(range(5)),
            "dict": {"a": 1, "b": 2},
            "mixed": [{"x": 1}, {"y": 2}]
        }
    }
    
    log_entry = AuditLogEntry(**valid_entry)
    assert log_entry.previous_data["nested"]["array"] == [1, 2, 3]
    assert log_entry.new_data["list"] == [0, 1, 2, 3, 4]

def test_invalid_json_types():
    """Test validation with invalid types in JSON fields"""
    user_id = uuid4()
    
    invalid_entries = [
        {
            "service_name": "test-service",
            "user_id": user_id,
            "action_type": "UPDATE",
            "entity_type": "user",
            "previous_data": {"date": datetime.now()},  # datetime is not JSON serializable
        },
        {
            "service_name": "test-service",
            "user_id": user_id,
            "action_type": "UPDATE",
            "entity_type": "user",
            "new_data": {"complex": complex(1, 2)},  # complex numbers are not JSON serializable
        },
        {
            "service_name": "test-service",
            "user_id": user_id,
            "action_type": "UPDATE",
            "entity_type": "user",
            "meta_data": {"bytes": b"binary data"},  # bytes are not JSON serializable
        }
    ]
    
    for invalid_entry in invalid_entries:
        with pytest.raises(ValidationError):
            AuditLogEntry(**invalid_entry)

def test_none_values_in_optional_fields():
    """Test that None is accepted in optional JSON fields"""
    user_id = uuid4()
    
    entry = {
        "service_name": "test-service",
        "user_id": user_id,
        "action_type": "UPDATE",
        "entity_type": "user",
        "previous_data": None,
        "new_data": None,
        "meta_data": None
    }
    
    log_entry = AuditLogEntry(**entry)
    assert log_entry.previous_data is None
    assert log_entry.new_data is None
    assert log_entry.meta_data is None
