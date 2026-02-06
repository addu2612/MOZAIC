from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.core.database import Base

class ServiceType(str, enum.Enum):
    kubernetes = "kubernetes"
    docker = "docker"
    cloudwatch = "cloudwatch"
    grafana = "grafana"
    sentry = "sentry"

class ConnectionStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    error = "error"

class AccountConnection(Base):
    __tablename__ = "account_connections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    service_type = Column(Enum(ServiceType), nullable=False)
    credentials_encrypted = Column(String, nullable=False)
    config = Column(JSON)
    status = Column(Enum(ConnectionStatus), default=ConnectionStatus.active)
    last_tested = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="accounts")