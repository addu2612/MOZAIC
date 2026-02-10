"""
Normal Operations Generator
Generates normal operation logs across all sources
"""
from datetime import datetime
from typing import Dict, Any, List
import random

from generators.kubernetes_generator import KubernetesLogGenerator
from generators.sentry_generator import SentryLogGenerator
from generators.cloudwatch_generator import CloudWatchLogGenerator
from generators.grafana_generator import GrafanaLogGenerator
from utils.realistic_data import realistic_data

class NormalOperationsGenerator:
    """Generate normal operation logs"""
    
    def __init__(
        self,
        k8s_gen: KubernetesLogGenerator,
        sentry_gen: SentryLogGenerator,
        cw_gen: CloudWatchLogGenerator,
        grafana_gen: GrafanaLogGenerator,
        services: List[str]
    ):
        self.k8s_gen = k8s_gen
        self.sentry_gen = sentry_gen
        self.cw_gen = cw_gen
        self.grafana_gen = grafana_gen
        self.services = services
    
    def generate_normal_logs(
        self,
        timestamp: datetime,
        log_count: int = 10
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Generate normal operation logs from all sources"""
        
        k8s_logs = []
        sentry_logs = []
        cw_logs = []
        grafana_logs = []
        
        # Select random services for this batch
        selected_services = random.sample(
            self.services,
            min(random.randint(2, 4), len(self.services))
        )
        
        for service in selected_services:
            # Kubernetes logs
            pod_name = realistic_data.generate_pod_name(service)
            k8s_logs.extend(
                self.k8s_gen.generate_normal_operation_logs(
                    timestamp, service, pod_name, count=log_count // len(selected_services)
                )
            )
            
            # Sentry logs (less frequent)
            if random.random() < 0.2:  # 20% chance
                sentry_logs.extend(
                    self.sentry_gen.generate_normal_operation_logs(
                        timestamp, service, count=2
                    )
                )
            
            # CloudWatch metrics
            cw_logs.extend(
                self.cw_gen.generate_normal_operation_metrics(timestamp, service)
            )
            
            # Grafana panels
            grafana_logs.extend(
                self.grafana_gen.generate_normal_operation_panels(
                    timestamp, service, count=3
                )
            )
        
        return {
            'kubernetes': k8s_logs,
            'sentry': sentry_logs,
            'cloudwatch': cw_logs,
            'grafana': grafana_logs
        }
