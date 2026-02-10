"""
Correlation Engine
Manages cross-source incident correlation and temporal relationships
"""
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field

@dataclass
class IncidentEvent:
    """Represents a single event in an incident"""
    event_id: str
    source: str  # 'kubernetes', 'sentry', 'cloudwatch', 'grafana'
    timestamp: datetime
    event_type: str
    severity: str
    data: Dict[str, Any]
    correlation_id: str = None
    incident_id: str = None

@dataclass
class Incident:
    """Represents a complete incident across multiple sources"""
    incident_id: str
    incident_type: str
    start_time: datetime
    end_time: datetime
    severity: str
    affected_services: List[str]
    events: List[IncidentEvent] = field(default_factory=list)
    correlation_id: str = None
    root_cause_service: str = None
    cascading_failures: List[str] = field(default_factory=list)

class CorrelationEngine:
    """Generates correlated incidents across multiple sources"""
    
    def __init__(self):
        self.incidents: List[Incident] = []
        self.correlation_map: Dict[str, List[str]] = {}
    
    def create_incident(
        self,
        incident_type: str,
        start_time: datetime,
        duration_minutes: int,
        severity: str,
        affected_services: List[str]
    ) -> Incident:
        """Create a new incident"""
        incident_id = f"inc_{uuid.uuid4().hex[:12]}"
        correlation_id = f"corr_{uuid.uuid4().hex[:16]}"
        
        incident = Incident(
            incident_id=incident_id,
            incident_type=incident_type,
            start_time=start_time,
            end_time=start_time + timedelta(minutes=duration_minutes),
            severity=severity,
            affected_services=affected_services,
            correlation_id=correlation_id,
            root_cause_service=affected_services[0] if affected_services else None
        )
        
        self.incidents.append(incident)
        return incident
    
    def add_kubernetes_event(
        self,
        incident: Incident,
        timestamp: datetime,
        event_type: str,
        service: str,
        pod_name: str,
        additional_data: Dict[str, Any] = None
    ) -> IncidentEvent:
        """Add a Kubernetes event to an incident"""
        event_id = f"k8s_{uuid.uuid4().hex[:12]}"
        
        data = {
            'service': service,
            'pod_name': pod_name,
            'namespace': 'production',
            'event_type': event_type,
            **(additional_data or {})
        }
        
        event = IncidentEvent(
            event_id=event_id,
            source='kubernetes',
            timestamp=timestamp,
            event_type=event_type,
            severity=incident.severity,
            data=data,
            correlation_id=incident.correlation_id,
            incident_id=incident.incident_id
        )
        
        incident.events.append(event)
        return event
    
    def add_sentry_event(
        self,
        incident: Incident,
        timestamp: datetime,
        error_type: str,
        service: str,
        error_message: str,
        additional_data: Dict[str, Any] = None
    ) -> IncidentEvent:
        """Add a Sentry error event to an incident"""
        event_id = f"sentry_{uuid.uuid4().hex[:12]}"
        
        data = {
            'service': service,
            'error_type': error_type,
            'error_message': error_message,
            'environment': 'production',
            **(additional_data or {})
        }
        
        event = IncidentEvent(
            event_id=event_id,
            source='sentry',
            timestamp=timestamp,
            event_type=error_type,
            severity=incident.severity,
            data=data,
            correlation_id=incident.correlation_id,
            incident_id=incident.incident_id
        )
        
        incident.events.append(event)
        return event
    
    def add_cloudwatch_event(
        self,
        incident: Incident,
        timestamp: datetime,
        metric_name: str,
        metric_value: float,
        service: str,
        additional_data: Dict[str, Any] = None
    ) -> IncidentEvent:
        """Add a CloudWatch metric event to an incident"""
        event_id = f"cw_{uuid.uuid4().hex[:12]}"
        
        data = {
            'metric_name': metric_name,
            'metric_value': metric_value,
            'service': service,
            'namespace': 'AWS/ECS',
            **(additional_data or {})
        }
        
        event = IncidentEvent(
            event_id=event_id,
            source='cloudwatch',
            timestamp=timestamp,
            event_type=f"metric_anomaly_{metric_name}",
            severity=incident.severity,
            data=data,
            correlation_id=incident.correlation_id,
            incident_id=incident.incident_id
        )
        
        incident.events.append(event)
        return event
    
    def add_grafana_event(
        self,
        incident: Incident,
        timestamp: datetime,
        panel_name: str,
        metric_value: float,
        service: str,
        additional_data: Dict[str, Any] = None
    ) -> IncidentEvent:
        """Add a Grafana panel event to an incident"""
        event_id = f"grafana_{uuid.uuid4().hex[:12]}"
        
        data = {
            'panel_name': panel_name,
            'metric_value': metric_value,
            'service': service,
            'dashboard': 'Production Monitoring',
            **(additional_data or {})
        }
        
        event = IncidentEvent(
            event_id=event_id,
            source='grafana',
            timestamp=timestamp,
            event_type=f"panel_alert_{panel_name}",
            severity=incident.severity,
            data=data,
            correlation_id=incident.correlation_id,
            incident_id=incident.incident_id
        )
        
        incident.events.append(event)
        return event
    
    def generate_temporal_correlation(
        self,
        base_timestamp: datetime,
        num_events: int,
        window_seconds: int = 300
    ) -> List[datetime]:
        """
        Generate temporally correlated timestamps
        Events cluster within a time window
        """
        timestamps = []
        
        for _ in range(num_events):
            # Events cluster near the base timestamp
            offset = random.gauss(0, window_seconds / 6)
            offset = max(-window_seconds, min(window_seconds, offset))
            
            timestamp = base_timestamp + timedelta(seconds=offset)
            timestamps.append(timestamp)
        
        return sorted(timestamps)
    
    def generate_causal_chain(
        self,
        root_cause_time: datetime,
        num_effects: int,
        propagation_delay_seconds: List[Tuple[int, int]] = None
    ) -> List[datetime]:
        """
        Generate causally related timestamps
        Each effect occurs after the previous with some delay
        """
        if propagation_delay_seconds is None:
            propagation_delay_seconds = [(5, 30), (10, 60), (30, 120)]
        
        timestamps = [root_cause_time]
        
        for i in range(min(num_effects, len(propagation_delay_seconds))):
            min_delay, max_delay = propagation_delay_seconds[i]
            delay = random.uniform(min_delay, max_delay)
            
            next_timestamp = timestamps[-1] + timedelta(seconds=delay)
            timestamps.append(next_timestamp)
        
        return timestamps
    
    def create_memory_leak_incident(
        self,
        start_time: datetime,
        service: str,
        pod_name: str,
        duration_minutes: int = 60
    ) -> Incident:
        """Generate a complete memory leak incident with correlated events"""
        incident = self.create_incident(
            incident_type='memory_leak',
            start_time=start_time,
            duration_minutes=duration_minutes,
            severity='critical',
            affected_services=[service]
        )
        
        # Generate degradation timeline
        warning_time = start_time + timedelta(minutes=duration_minutes * 0.3)
        critical_time = start_time + timedelta(minutes=duration_minutes * 0.7)
        oom_time = start_time + timedelta(minutes=duration_minutes * 0.9)
        
        # Grafana: Gradual memory increase detected first
        for i in range(10):
            progress = i / 10
            timestamp = start_time + timedelta(minutes=duration_minutes * progress * 0.7)
            memory_value = 60 + (35 * progress)  # 60% to 95%
            
            self.add_grafana_event(
                incident, timestamp, 'JVM Heap Usage', memory_value, service
            )
        
        # CloudWatch: Memory metrics spike
        for i in range(8):
            progress = i / 8
            timestamp = start_time + timedelta(minutes=duration_minutes * progress * 0.8)
            memory_value = 65 + (33 * progress)  # 65% to 98%
            
            self.add_cloudwatch_event(
                incident, timestamp, 'MemoryUtilization', memory_value, service
            )
        
        # Sentry: Memory allocation errors start appearing
        error_start = warning_time
        for i in range(5):
            timestamp = error_start + timedelta(minutes=i * 5)
            
            self.add_sentry_event(
                incident,
                timestamp,
                'MemoryError',
                service,
                f"Cannot allocate {random.randint(100, 500)}MB of memory",
                {'tags': {'severity': 'warning' if i < 3 else 'error'}}
            )
        
        # Kubernetes: Pod warnings and eventual OOMKilled
        self.add_kubernetes_event(
            incident,
            warning_time,
            'Warning',
            service,
            pod_name,
            {'reason': 'HighMemoryUsage', 'message': 'Memory usage at 85%'}
        )
        
        self.add_kubernetes_event(
            incident,
            critical_time,
            'Warning',
            service,
            pod_name,
            {'reason': 'MemoryPressure', 'message': 'Memory usage critical at 95%'}
        )
        
        self.add_kubernetes_event(
            incident,
            oom_time,
            'OOMKilled',
            service,
            pod_name,
            {'reason': 'OOMKilled', 'message': 'Container killed due to OOM', 'exit_code': 137}
        )
        
        # Pod restart
        restart_time = oom_time + timedelta(seconds=5)
        self.add_kubernetes_event(
            incident,
            restart_time,
            'Restarted',
            service,
            pod_name,
            {'reason': 'PodRestarted', 'message': f'Container restarted, restart count: {random.randint(1, 5)}'}
        )
        
        return incident
    
    def create_deployment_failure_incident(
        self,
        start_time: datetime,
        service: str,
        duration_minutes: int = 15
    ) -> Incident:
        """Generate a complete deployment failure incident"""
        incident = self.create_incident(
            incident_type='deployment_failure',
            start_time=start_time,
            duration_minutes=duration_minutes,
            severity='high',
            affected_services=[service]
        )
        
        new_pod_name = f"{service}-new-{uuid.uuid4().hex[:5]}"
        
        # Kubernetes: ImagePullBackOff
        self.add_kubernetes_event(
            incident,
            start_time,
            'ImagePullBackOff',
            service,
            new_pod_name,
            {
                'reason': 'ImagePullBackOff',
                'message': 'Back-off pulling image "company/service:v2.5.0"',
                'image': 'company/service:v2.5.0'
            }
        )
        
        # Multiple CrashLoopBackOff events
        for i in range(5):
            crash_time = start_time + timedelta(minutes=i * 2)
            self.add_kubernetes_event(
                incident,
                crash_time,
                'CrashLoopBackOff',
                service,
                new_pod_name,
                {
                    'reason': 'CrashLoopBackOff',
                    'message': f'Back-off restarting failed container, restart count: {i+1}',
                    'exit_code': 1
                }
            )
        
        # Sentry: Configuration errors
        config_error_time = start_time + timedelta(seconds=30)
        for i in range(3):
            timestamp = config_error_time + timedelta(minutes=i * 3)
            self.add_sentry_event(
                incident,
                timestamp,
                'ConfigurationError',
                service,
                'Missing required environment variable: DATABASE_URL',
                {'environment': 'production', 'release': 'v2.5.0'}
            )
        
        # CloudWatch: 5XX errors spike
        error_spike_start = start_time + timedelta(minutes=2)
        for i in range(6):
            timestamp = error_spike_start + timedelta(minutes=i)
            error_count = 50 + (i * 100)
            
            self.add_cloudwatch_event(
                incident,
                timestamp,
                'HTTPCode_Target_5XX_Count',
                error_count,
                service,
                {'unit': 'Count', 'statistic': 'Sum'}
            )
        
        # Grafana: Error rate spike
        for i in range(5):
            timestamp = start_time + timedelta(minutes=i * 2)
            error_rate = 0.5 + (i * 2.5)  # 0.5% to 10.5%
            
            self.add_grafana_event(
                incident,
                timestamp,
                'Error Rate',
                error_rate,
                service,
                {'unit': 'percent'}
            )
        
        return incident
    
    def create_database_connection_pool_exhaustion(
        self,
        start_time: datetime,
        service: str,
        duration_minutes: int = 30
    ) -> Incident:
        """Generate database connection pool exhaustion incident"""
        incident = self.create_incident(
            incident_type='database_connection_pool_exhaustion',
            start_time=start_time,
            duration_minutes=duration_minutes,
            severity='critical',
            affected_services=[service, 'postgres-primary']
        )
        
        # Sentry: Connection timeout errors surge
        for i in range(20):
            timestamp = start_time + timedelta(seconds=i * 30)
            self.add_sentry_event(
                incident,
                timestamp,
                'PoolTimeoutError',
                service,
                f'QueuePool limit of 20 overflow 10 reached, connection timed out',
                {'tags': {'database': 'postgresql', 'pool': 'main'}}
            )
        
        # CloudWatch: Database connections at max
        for i in range(10):
            timestamp = start_time + timedelta(minutes=i * 2)
            self.add_cloudwatch_event(
                incident,
                timestamp,
                'DatabaseConnections',
                100.0,  # At maximum
                'postgres-primary',
                {'unit': 'Count', 'dimension': 'DBInstanceIdentifier'}
            )
        
        # CloudWatch: Read/Write latency spike
        for i in range(12):
            timestamp = start_time + timedelta(minutes=i * 2)
            latency = 50 + (i * 200)  # Increasing latency
            
            self.add_cloudwatch_event(
                incident,
                timestamp,
                'ReadLatency',
                latency,
                'postgres-primary',
                {'unit': 'Milliseconds'}
            )
        
        # Kubernetes: Slow response times
        pod_name = f"{service}-0-abc123"
        for i in range(8):
            timestamp = start_time + timedelta(minutes=i * 3)
            self.add_kubernetes_event(
                incident,
                timestamp,
                'SlowResponse',
                service,
                pod_name,
                {
                    'reason': 'HighLatency',
                    'message': f'Response time exceeded threshold: {1000 + i*500}ms',
                    'threshold': '1000ms'
                }
            )
        
        # Grafana: Connection pool visualization
        for i in range(15):
            timestamp = start_time + timedelta(minutes=i * 2)
            pool_usage = min(100, 60 + i * 5)
            
            self.add_grafana_event(
                incident,
                timestamp,
                'Database Connection Pool',
                pool_usage,
                service,
                {'unit': 'percent', 'max_connections': 20}
            )
        
        return incident
    
    def should_cascade(self, probability: float = 0.3) -> bool:
        """Determine if incident should cascade to another service"""
        return random.random() < probability
    
    def get_cascade_targets(self, root_service: str, all_services: List[str]) -> List[str]:
        """Get services that might be affected by cascading failure"""
        # Dependency map (simplified)
        dependencies = {
            'api-gateway': ['user-service', 'order-service', 'product-service'],
            'order-service': ['payment-service', 'user-service', 'product-service'],
            'user-service': ['postgres-primary'],
            'payment-service': ['postgres-primary'],
            'product-service': ['redis-cache', 'postgres-primary']
        }
        
        return dependencies.get(root_service, [])
