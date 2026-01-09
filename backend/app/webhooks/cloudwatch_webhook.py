from fastapi import APIRouter, Request, HTTPException
from app.workers.celery_tasks import process_incident

router = APIRouter()

@router.post("/cloudwatch/{project_id}")
async def cloudwatch_webhook(project_id: str, request: Request):
    """Receive SNS notification from CloudWatch"""
    try:
        payload = await request.json()
        
        # Handle SNS subscription confirmation
        if payload.get("Type") == "SubscriptionConfirmation":
            # TODO: Confirm subscription
            return {"status": "confirmed"}
        
        # Trigger async processing
        process_incident.delay(str(project_id), "cloudwatch", payload)
        
        return {"status": "received"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))