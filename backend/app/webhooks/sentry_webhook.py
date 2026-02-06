from fastapi import APIRouter, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.workers.celery_tasks import process_incident

router = APIRouter()

@router.post("/sentry/{project_id}")
async def sentry_webhook(project_id: str, request: Request):
    """Receive webhook from Sentry"""
    try:
        payload = await request.json()
        
        # Trigger async processing
        process_incident.delay(str(project_id), "sentry", payload)
        
        return {"status": "received"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))