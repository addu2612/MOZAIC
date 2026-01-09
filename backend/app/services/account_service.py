from app.models.account_connection import ServiceType
from typing import Dict, Any

async def test_connection(service_type: ServiceType, credentials: Dict[str, Any]) -> bool:
    """Test connection to external service"""
    try:
        if service_type == ServiceType.kubernetes:
            from app.services.monitoring.kubernetes_client import test_k8s_connection
            return await test_k8s_connection(credentials)
        elif service_type == ServiceType.docker:
            from app.services.monitoring.docker_client import test_docker_connection
            return await test_docker_connection(credentials)
        elif service_type == ServiceType.cloudwatch:
            from app.services.monitoring.cloudwatch_client import test_cloudwatch_connection
            return await test_cloudwatch_connection(credentials)
        elif service_type == ServiceType.grafana:
            from app.services.monitoring.grafana_client import test_grafana_connection
            return await test_grafana_connection(credentials)
        elif service_type == ServiceType.sentry:
            from app.services.monitoring.sentry_client import test_sentry_connection
            return await test_sentry_connection(credentials)
        return False
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False