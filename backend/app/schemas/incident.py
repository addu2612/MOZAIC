from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any, Union, List
from app.models.incident import Severity

class IncidentResponse(BaseModel):
    id: UUID
    project_id: UUID
    source: str
    severity: Severity
    title: str
    logs_json: Optional[Any] = None
    correlation_data: Optional[Dict[str, Any]]
    timestamp: datetime
    resolved: Optional[datetime]
    
    class Config:
        from_attributes = True