import pytest
from uuid import UUID, uuid4
from datetime import datetime
from app.schemas import AuditLogEntry
from app.database import AuditLog
from pydantic import ValidationError
from sqlalchemy import inspect

def test_valid_complete_entry():
    """Test creating a valid audit log entry with all fields"""
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

def test_valid_minimal_entry():
    """Test creating a valid audit log entry with only required fields"""
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

def test_missing_required_fields():
    """Test validation errors when required fields are missing"""
    invalid_entry = {
        "service_name": "test-service",
        # missing user_id
        "action_type": "DELETE"
        # missing entity_type
    }
    
    with pytest.raises(ValidationError) as exc_info:
        AuditLogEntry(**invalid_entry)
    
    errors = exc_info.value.errors()
    error_fields = [error["loc"][0] for error in errors]
    assert "user_id" in error_fields
    assert "entity_type" in error_fields

def test_invalid_uuid_fields():
    """Test validation errors for invalid UUID fields"""
    invalid_entry = {
        "service_name": "test-service",
        "user_id": "not-a-uuid",
        "action_type": "CREATE",
        "entity_type": "user",
        "entity_id": "invalid-uuid"
    }
    
    with pytest.raises(ValidationError) as exc_info:
        AuditLogEntry(**invalid_entry)
    
    errors = exc_info.value.errors()
    error_fields = [error["loc"][0] for error in errors]
    assert "user_id" in error_fields
    assert "entity_id" in error_fields

def test_model_columns():
    """Test that the AuditLog model has all expected columns with correct types"""
    mapper = inspect(AuditLog)
    columns = {column.name: column.type.__class__.__name__ for column in mapper.columns}
    
    expected_columns = {
        'id': 'UUID',
        'timestamp': 'TIMESTAMP',
        'service_name': 'String',
        'service_id': 'String',
        'user_id': 'UUID',
        'action_type': 'String',
        'entity_type': 'String',
        'entity_id': 'UUID',
        'previous_data': 'JSON',
        'new_data': 'JSON',
        'meta_data': 'JSON'
    }
    
    assert set(columns.keys()) == set(expected_columns.keys())
    for column_name, expected_type in expected_columns.items():
        assert columns[column_name] == expected_type

def test_nullable_columns():
    """Test that the correct columns are nullable/non-nullable"""
    mapper = inspect(AuditLog)
    nullable_columns = {column.name: column.nullable for column in mapper.columns}
    
    # Required fields (non-nullable)
    assert not nullable_columns['service_name']
    assert not nullable_columns['user_id']
    assert not nullable_columns['action_type']
    assert not nullable_columns['entity_type']
    assert not nullable_columns['timestamp']
    
    # Optional fields (nullable)
    assert nullable_columns['service_id']
    assert nullable_columns['entity_id']
    assert nullable_columns['previous_data']
    assert nullable_columns['new_data']
    assert nullable_columns['meta_data']

def test_string_length_constraints():
    """Test string length constraints on the model"""
    mapper = inspect(AuditLog)
    string_columns = {
        column.name: column.type.length 
        for column in mapper.columns 
        if hasattr(column.type, 'length') and column.type.length is not None
    }
    
    expected_lengths = {
        'service_name': 255,
        'service_id': 255,
        'action_type': 100,
        'entity_type': 100
    }
    
    assert string_columns == expected_lengths

def test_table_name():
    """Test that the model has the correct table name"""
    assert AuditLog.__tablename__ == "audit_logs"

