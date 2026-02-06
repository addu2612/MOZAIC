from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.models.incident import Severity

async def correlate_incidents(clusters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Correlate incidents across different sources"""
    
    correlated = []
    
    for cluster in clusters:
        # Simple temporal correlation
        incident = {
            "source": cluster.get("source", "multiple"),
            "title": f"Incident detected from {cluster.get('source', 'multiple sources')}",
            "logs": cluster["logs"],
            "severity": determine_severity(cluster),
            "correlation": {
                "cluster_id": cluster["cluster_id"],
                "log_count": len(cluster["logs"])
            }
        }
        correlated.append(incident)
    
    # Cross-source correlation (temporal window)
    # TODO: Implement semantic + temporal correlation
    
    return correlated

def determine_severity(cluster: Dict[str, Any]) -> Severity:
    """Determine incident severity based on cluster data"""
    log_count = len(cluster.get("logs", []))
    
    if log_count > 10:
        return Severity.critical
    elif log_count > 5:
        return Severity.high
    elif log_count > 2:
        return Severity.medium
    return Severity.low