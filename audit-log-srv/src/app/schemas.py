from pydantic import BaseModel, field_validator
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic.config import ConfigDict
import json
import datetime

class AuditLogEntry(BaseModel):
    service_name: str
    service_id: Optional[str] = None  # Optional service-specific ID
    user_id: UUID  # Required UUID for the user
    action_type: str
    entity_type: str
    entity_id: Optional[UUID] = None  # Optional UUID for the entity
    previous_data: Optional[Dict] = None  # Previous state of the entity
    new_data: Optional[Dict] = None  # New state of the entity
    meta_data: Optional[Dict] = None  # Additional metadata

    model_config = ConfigDict(from_attributes=True)
        
    @field_validator('previous_data', 'new_data', 'meta_data')
    @classmethod
    def validate_json_serializable(cls, value: Optional[Dict]) -> Optional[Dict]:
        if value is None:
            return value
        try:
            # Test if the data is JSON serializable
            json.dumps(value)
            return value
        except (TypeError, ValueError) as e:
            raise ValueError(f"Value must be JSON serializable: {str(e)}")

    def model_dump_json(self, **kwargs):
        def custom_encoder(obj):
            if isinstance(obj, (UUID, datetime)):
                return str(obj)
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
            
        return json.dumps(self.model_dump(), default=custom_encoder, **kwargs)

