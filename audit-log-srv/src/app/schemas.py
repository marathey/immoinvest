from pydantic import BaseModel
from typing import Optional, Dict
from uuid import UUID
from pydantic.config import ConfigDict

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
