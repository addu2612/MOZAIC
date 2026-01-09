from app.workers.celery_app  import celery_app
from app.core.database import AsyncSessionLocal
from app.models.incident import Incident, Severity
from app.mcp.orchestrator import orchestrate_incident_detection
from datetime import datetime

@celery_app.task
def process_incident(project_id: str, source: str, payload: dict):
    """Background task to process incoming incident"""
    import asyncio
    
    async def _process():
        async with AsyncSessionLocal() as db:
            incident = Incident(
                project_id=project_id,
                source=source,
                severity=Severity.medium,
                title=f"Incident from {source}",
                logs_json=payload,
                timestamp=datetime.utcnow()
            )
            db.add(incident)
            await db.commit()
            
            # Trigger full orchestration
            await orchestrate_incident_detection(project_id, db)
    
    asyncio.run(_process())

@celery_app.task
def periodic_log_fetch(project_id: str):
    """Periodic task to fetch logs from all sources"""
    import asyncio
    
    async def _fetch():
        async with AsyncSessionLocal() as db:
            await orchestrate_incident_detection(project_id, db)
    
    asyncio.run(_fetch())