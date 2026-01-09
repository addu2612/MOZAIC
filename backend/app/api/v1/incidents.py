from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.incident import Incident
from app.schemas.incident import IncidentResponse
from app.api.v1.dependencies import get_current_user

router = APIRouter()

@router.get("/project/{project_id}", response_model=List[IncidentResponse])
async def get_project_incidents(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify project ownership
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")
    
    result = await db.execute(
        select(Incident)
        .where(Incident.project_id == project_id)
        .order_by(desc(Incident.timestamp))
    )
    return result.scalars().all()

@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Verify ownership through project
    result = await db.execute(
        select(Project).where(Project.id == incident.project_id, Project.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")
    
    return incident

@router.post("/fetch/{project_id}")
async def manual_fetch(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from app.mcp.orchestrator import orchestrate_incident_detection
    incidents = await orchestrate_incident_detection(str(project_id), db)
    return {"message": "Fetch complete", "incidents_found": len(incidents)}