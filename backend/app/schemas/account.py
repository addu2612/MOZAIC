from pydantic import BaseModel, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any
from app.models.account_connection import ServiceType, ConnectionStatus

class AccountConnectionCreate(BaseModel):
    project_id: UUID
    service_type: ServiceType
    credentials: Dict[str, Any]
    config: Optional[Dict[str, Any]] = None

    @field_validator('service_type', mode='before')
    def lowercase_service_type(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v

class AccountConnectionResponse(BaseModel):
    id: UUID
    project_id: UUID
    service_type: ServiceType
    status: ConnectionStatus
    last_tested: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True