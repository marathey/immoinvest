from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime
from pydantic.config import ConfigDict

class CompanyStatusBase(BaseModel):
    status_code: str
    status_description: Optional[str] = None
    is_active: bool = True

class CompanyStatusCreate(CompanyStatusBase):
    pass

class CompanyStatusUpdate(BaseModel):
    status_code: Optional[str] = None
    status_description: Optional[str] = None
    is_active: Optional[bool] = None

class CompanyStatusResponse(CompanyStatusBase):
    status_id: UUID4
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str

    model_config = ConfigDict(from_attributes=True)