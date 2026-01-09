from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
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

async def orchestrate_incident_detection(project_id: str, db: AsyncSession) -> List[Dict[str, Any]]:
    """Main orchestrator for detecting and correlating incidents"""
    
    # Fetch all active connections
    result = await db.execute(
        select(AccountConnection).where(AccountConnection.project_id == project_id)
    )
    connections = result.scalars().all()
    
    all_logs = []
    
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
    
    # Cluster similar logs
    clustered = await cluster_logs(all_logs)
    
    # Correlate across sources
    correlated = await correlate_incidents(clustered)
    
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