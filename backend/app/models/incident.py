from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.core.database import Base

class Severity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    source = Column(String, nullable=False)
    severity = Column(Enum(Severity), default=Severity.medium)
    title = Column(String, nullable=False)
    logs_json = Column(JSON)
    correlation_data = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
    resolved = Column(DateTime)
    
    project = relationship("Project", back_populates="incidents")