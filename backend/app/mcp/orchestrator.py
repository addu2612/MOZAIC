from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pathlib import Path
import os
import random
from datetime import datetime, timedelta
import uuid
from app.models.account_connection import AccountConnection, ServiceType
from app.models.incident import Incident, Severity
from app.core.security import decrypt_credentials
from app.services.monitoring import (
    kubernetes_client, docker_client, cloudwatch_client, 
    grafana_client, sentry_client
)
from app.mcp.clustering import cluster_logs
from app.mcp.correlation import correlate_incidents
import json

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BASE = Path(os.environ.get("MOZAIC_BASE_DIR", str(PROJECT_ROOT)))
DEMO_OUTPUT_DIR = Path(os.environ.get("MOZAIC_DEMO_OUTPUT_DIR", str(BASE / "syntheticlogs" / "output_demo")))
DEMO_INCIDENTS_PATH = DEMO_OUTPUT_DIR / "correlation" / "incidents.json"


def _normalize_severity(value: str) -> Severity:
    if not value:
        return Severity.medium
    val = str(value).strip().lower()
    if val in {"p0", "critical"}:
        return Severity.critical
    if val in {"p1", "high"}:
        return Severity.high
    if val in {"p2", "medium"}:
        return Severity.medium
    if val in {"p3", "low"}:
        return Severity.low
    try:
        return Severity(val)
    except Exception:
        return Severity.medium


async def _load_demo_incidents(project_id: str, db: AsyncSession) -> List[Incident]:
    await db.execute(
        delete(Incident).where(Incident.project_id == project_id, Incident.source == "demo")
    )
    if not DEMO_INCIDENTS_PATH.exists():
        return []
    try:
        data = json.loads(DEMO_INCIDENTS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []
    items = data.get("incidents", [])
    if not items:
        return []
    random.shuffle(items)
    sample_size = random.randint(3, min(8, len(items)))
    items = items[:sample_size]
    incidents: List[Incident] = []
    for item in items:
        start_offset = random.randint(5, 180)
        duration = random.randint(5, 90)
        start_time = datetime.utcnow() - timedelta(minutes=start_offset)
        end_time = start_time + timedelta(minutes=duration)
        event_count = random.randint(0, 120)
        correlation_id = f"demo_corr_{uuid.uuid4().hex[:12]}"
        payload = {
            **item,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "event_count": event_count,
            "correlation_id": correlation_id,
        }
        incident = Incident(
            project_id=project_id,
            source="demo",
            severity=_normalize_severity(item.get("severity")),
            title=item.get("incident_type") or "incident",
            logs_json=payload,
            correlation_data={"correlation_id": correlation_id},
        )
        db.add(incident)
        incidents.append(incident)
    if incidents:
        await db.commit()
    return incidents

async def orchestrate_incident_detection(project_id: str, db: AsyncSession) -> List[Dict[str, Any]]:
    """Main orchestrator for detecting and correlating incidents"""
    
    # Fetch all active connections
    result = await db.execute(
        select(AccountConnection).where(AccountConnection.project_id == project_id)
    )
    connections = result.scalars().all()
    
    all_logs = []

    if not connections:
        return await _load_demo_incidents(project_id, db)
    
    for conn in connections:
        credentials = json.loads(decrypt_credentials(conn.credentials_encrypted))
        
        try:
            if conn.service_type == ServiceType.kubernetes:
                events = await kubernetes_client.get_pod_events(credentials, "default")
                all_logs.extend([{"source": "kubernetes", "data": e} for e in events])
                
            elif conn.service_type == ServiceType.cloudwatch:
                alarms = await cloudwatch_client.get_active_alarms(credentials)
                all_logs.extend([{"source": "cloudwatch", "data": a} for a in alarms])
                
            elif conn.service_type == ServiceType.grafana:
                alerts = await grafana_client.fetch_grafana_alerts(credentials)
                all_logs.extend([{"source": "grafana", "data": a} for a in alerts])
                
            elif conn.service_type == ServiceType.sentry:
                issues = await sentry_client.fetch_sentry_issues(credentials, credentials.get("project_slug"))
                all_logs.extend([{"source": "sentry", "data": i} for i in issues])
                
        except Exception as e:
            print(f"Error fetching from {conn.service_type}: {e}")
    
    if not all_logs:
        return await _load_demo_incidents(project_id, db)

    # Cluster similar logs
    clustered = await cluster_logs(all_logs)
    
    # Correlate across sources
    correlated = await correlate_incidents(clustered)
    if not correlated:
        demo = await _load_demo_incidents(project_id, db)
        if demo:
            return demo
    
    # Store incidents
    incidents = []
    for incident_data in correlated:
        incident = Incident(
            project_id=project_id,
            source=incident_data["source"],
            severity=incident_data.get("severity", Severity.medium),
            title=incident_data["title"],
            logs_json=incident_data["logs"],
            correlation_data=incident_data.get("correlation")
        )
        db.add(incident)
        incidents.append(incident)
    
    await db.commit()
    return incidents