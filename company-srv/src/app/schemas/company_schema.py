from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime

class CompanyBase(BaseModel):
    company_code: str
    company_name: str
    company_country: str
    company_accounting_standards: str

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    company_code: Optional[str] = None
    company_name: Optional[str] = None
    company_country: Optional[str] = None
    company_accounting_standards: Optional[str] = None



class CompanyResponse(CompanyBase):
    company_id: UUID4
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str

    class Config:
        from_attributes = True

class CompanyVersionResponse(CompanyBase):
    version_id: UUID4
    company_id: UUID4
    version_number: int
    changed_at: datetime
    changed_by: str
    change_type: str
    change_reason: Optional[str]

    class Config:
        from_attributes = True

