"""
Incident Scenario Generator
Orchestrates all 4 generators to create correlated incidents
"""
from datetime import datetime
from typing import Dict, Any, List

from generators.kubernetes_generator import KubernetesLogGenerator
from generators.sentry_generator import SentryLogGenerator
from generators.cloudwatch_generator import CloudWatchLogGenerator
from generators.grafana_generator import GrafanaLogGenerator
from utils.correlation_engine import CorrelationEngine

class IncidentScenarioGenerator:
    """Generate complete incident scenarios across all sources"""
    
    def __init__(
        self,
        k8s_gen: KubernetesLogGenerator,
        sentry_gen: SentryLogGenerator,
        cw_gen: CloudWatchLogGenerator,
        grafana_gen: GrafanaLogGenerator,
        corr_engine: CorrelationEngine
    ):
        self.k8s_gen = k8s_gen
        self.sentry_gen = sentry_gen
        self.cw_gen = cw_gen
        self.grafana_gen = grafana_gen
        self.corr_engine = corr_engine
    
    def generate_memory_leak_incident(
        self,
        start_time: datetime,
        service: str,
        duration_minutes: int = 60
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Generate complete memory leak incident"""
        
        # Create incident in correlation engine
        incident = self.corr_engine.create_memory_leak_incident(
            start_time, service,
            f"{service}-0-abc123",
            duration_minutes
        )
        
        # Generate logs from all sources
        k8s_logs = self.k8s_gen.generate_for_incident(incident)
        sentry_logs = self.sentry_gen.generate_for_incident(incident, error_frequency='high')
        cw_logs = self.cw_gen.generate_for_incident(incident)
        grafana_logs = self.grafana_gen.generate_for_incident(incident)
        
        return {
            'kubernetes': k8s_logs,
            'sentry': sentry_logs,
            'cloudwatch': cw_logs,
            'grafana': grafana_logs,
            'incident': incident
        }
    
    def generate_deployment_failure_incident(
        self,
        start_time: datetime,
        service: str,
        duration_minutes: int = 15
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Generate complete deployment failure incident"""
        
        incident = self.corr_engine.create_deployment_failure_incident(
            start_time, service, duration_minutes
        )
        
        k8s_logs = self.k8s_gen.generate_for_incident(incident)
        sentry_logs = self.sentry_gen.generate_for_incident(incident, error_frequency='very_high')
        cw_logs = self.cw_gen.generate_for_incident(incident)
        grafana_logs = self.grafana_gen.generate_for_incident(incident)
        
        return {
            'kubernetes': k8s_logs,
            'sentry': sentry_logs,
            'cloudwatch': cw_logs,
            'grafana': grafana_logs,
            'incident': incident
        }
    
    def generate_database_connection_pool_exhaustion(
        self,
        start_time: datetime,
        service: str,
        duration_minutes: int = 30
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Generate database connection pool exhaustion incident"""
        
        incident = self.corr_engine.create_database_connection_pool_exhaustion(
            start_time, service, duration_minutes
        )
        
        k8s_logs = self.k8s_gen.generate_for_incident(incident)
        sentry_logs = self.sentry_gen.generate_for_incident(incident, error_frequency='very_high')
        cw_logs = self.cw_gen.generate_for_incident(incident)
        grafana_logs = self.grafana_gen.generate_for_incident(incident)
        
        return {
            'kubernetes': k8s_logs,
            'sentry': sentry_logs,
            'cloudwatch': cw_logs,
            'grafana': grafana_logs,
            'incident': incident
        }
