"""
Grafana MCP Server Log Generator
Generates hyper-realistic Grafana dashboard and panel data
"""
import json
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from utils.realistic_data import realistic_data
from utils.timestamp_utils import TimestampGenerator

class GrafanaLogGenerator:
    """Generate realistic Grafana dashboard and panel data"""
    
    def __init__(self, services_config: Dict[str, Any]):
        self.services = services_config.get('services', {})
        self.infrastructure = services_config.get('infrastructure', {})
        
        # Define dashboards and panels
        self.dashboards = {
            'Infrastructure Overview': [
                'CPU Usage', 'Memory Usage', 'Network Traffic', 'Disk I/O',
                'Pod Count', 'Node Status'
            ],
            'Application Performance': [
                'Request Rate', 'Response Time P95', 'Response Time P99',
                'Error Rate', 'Success Rate', 'Throughput'
            ],
            'Database Metrics': [
                'Query Duration', 'Connection Pool Usage', 'Active Connections',
                'Query Rate', 'Cache Hit Rate', 'Deadlocks'
            ],
            'Cache Performance': [
                'Cache Hit Rate', 'Cache Miss Rate', 'Eviction Rate',
                'Memory Usage', 'Keys Count'
            ],
            'JVM Metrics': [
                'JVM Heap Usage', 'GC Time', 'GC Count', 'Thread Count'
            ]
        }
    
    def generate_panel_query_result(
        self,
        timestamp: datetime,
        dashboard: str,
        panel_name: str,
        service: str,
        value: float,
        unit: str = 'percent',
        anomaly_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a Grafana panel query result"""
        
        return {
            'dashboard': dashboard,
            'panel': {
                'id': self._get_panel_id(panel_name),
                'title': panel_name,
                'type': self._get_panel_type(panel_name),
                'datasource': self._get_datasource(panel_name)
            },
            'target': {
                'expr': self._generate_prometheus_query(panel_name, service),
                'legendFormat': f'{service} - {panel_name}',
                'refId': 'A'
            },
            'datapoints': [[value, int(timestamp.timestamp() * 1000)]],
            'tags': {
                'service': service,
                'environment': 'production',
                'cluster': 'production-us-east-1'
            },
            'meta': {
                'executedQueryString': self._generate_prometheus_query(panel_name, service),
                'preferredVisualisationType': 'graph'
            }
        }
    
    def _get_panel_id(self, panel_name: str) -> int:
        """Generate consistent panel ID from panel name"""
        return hash(panel_name) % 10000
    
    def _get_panel_type(self, panel_name: str) -> str:
        """Determine panel visualization type"""
        if 'rate' in panel_name.lower() or 'count' in panel_name.lower():
            return 'graph'
        elif 'usage' in panel_name.lower() or 'utilization' in panel_name.lower():
            return 'gauge'
        elif 'status' in panel_name.lower():
            return 'stat'
        elif 'distribution' in panel_name.lower():
            return 'heatmap'
        else:
            return 'graph'
    
    def _get_datasource(self, panel_name: str) -> str:
        """Determine data source for panel"""
        if any(keyword in panel_name.lower() for keyword in ['jvm', 'heap', 'gc', 'thread']):
            return 'Prometheus'
        elif 'cloudwatch' in panel_name.lower():
            return 'CloudWatch'
        else:
            return 'Prometheus'
    
    def _generate_prometheus_query(self, panel_name: str, service: str) -> str:
        """Generate realistic Prometheus query"""
        metric_queries = {
            'CPU Usage': f'rate(container_cpu_usage_seconds_total{{pod=~"{service}.*"}}[5m]) * 100',
            'Memory Usage': f'container_memory_usage_bytes{{pod=~"{service}.*"}} / container_spec_memory_limit_bytes * 100',
            'Request Rate': f'rate(http_requests_total{{service="{service}"}}[5m])',
            'Response Time P95': f'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{{service="{service}"}}[5m]))',
            'Response Time P99': f'histogram_quantile(0.99, rate(http_request_duration_seconds_bucket{{service="{service}"}}[5m]))',
            'Error Rate': f'rate(http_requests_total{{service="{service}",status=~"5.."}}[5m]) / rate(http_requests_total{{service="{service}"}}[5m]) * 100',
            'Success Rate': f'rate(http_requests_total{{service="{service}",status=~"2.."}}[5m]) / rate(http_requests_total{{service="{service}"}}[5m]) * 100',
            'Query Duration': f'rate(postgresql_query_duration_seconds_sum[5m]) / rate(postgresql_query_duration_seconds_count[5m])',
            'Connection Pool Usage': f'pgbouncer_pools_cl_active{{database="{service}"}} / pgbouncer_pools_cl_max * 100',
            'Cache Hit Rate': f'redis_keyspace_hits_total / (redis_keyspace_hits_total + redis_keyspace_misses_total) * 100',
            'JVM Heap Usage': f'jvm_memory_used_bytes{{area="heap",service="{service}"}} / jvm_memory_max_bytes{{area="heap"}} * 100',
            'GC Time': f'rate(jvm_gc_collection_seconds_sum{{service="{service}"}}[5m])',
            'Pod Count': f'count(kube_pod_info{{namespace="production",pod=~"{service}.*"}}))',
            'Network Traffic': f'rate(container_network_receive_bytes_total{{pod=~"{service}.*"}}[5m])'
        }
        
        return metric_queries.get(panel_name, f'up{{service="{service}"}}')
    
    def generate_time_series_data(
        self,
        start_time: datetime,
        end_time: datetime,
        panel_name: str,
        service: str,
        interval_seconds: int = 15,
        anomaly_type: Optional[str] = None
    ) -> List[List]:
        """Generate time series data points for a panel"""
        
        datapoints = []
        current_time = start_time
        
        # Determine base value and variation based on panel type
        base_value = self._get_base_value(panel_name, anomaly_type)
        
        while current_time <= end_time:
            # Calculate value with variation
            value = self._calculate_metric_value(
                panel_name, base_value, current_time, start_time, end_time, anomaly_type
            )
            
            # Format as [value, timestamp_ms]
            datapoints.append([value, int(current_time.timestamp() * 1000)])
            
            current_time += timedelta(seconds=interval_seconds)
        
        return datapoints
    
    def _get_base_value(self, panel_name: str, anomaly_type: Optional[str]) -> float:
        """Get base value for a metric"""
        if anomaly_type:
            if 'memory' in anomaly_type and 'memory' in panel_name.lower():
                return 85.0
            elif 'cpu' in anomaly_type and 'cpu' in panel_name.lower():
                return 90.0
            elif 'connection' in anomaly_type and 'connection' in panel_name.lower():
                return 95.0
            elif 'cache' in anomaly_type and 'cache' in panel_name.lower():
                return 15.0  # Low hit rate
        
        # Normal values
        normal_values = {
            'CPU Usage': 35.0,
            'Memory Usage': 50.0,
            'Request Rate': 150.0,
            'Response Time P95': 120.0,
            'Response Time P99': 250.0,
            'Error Rate': 0.5,
            'Success Rate': 99.5,
            'Query Duration': 45.0,
            'Connection Pool Usage': 40.0,
            'Cache Hit Rate': 92.0,
            'JVM Heap Usage': 55.0,
            'GC Time': 0.02,
            'Pod Count': 5.0,
            'Network Traffic': 1024000.0
        }
        
        return normal_values.get(panel_name, 50.0)
    
    def _calculate_metric_value(
        self,
        panel_name: str,
        base_value: float,
        current_time: datetime,
        start_time: datetime,
        end_time: datetime,
        anomaly_type: Optional[str]
    ) -> float:
        """Calculate metric value with realistic variation"""
        
        if anomaly_type:
            # Calculate progress through incident (0.0 to 1.0)
            progress = (current_time - start_time).total_seconds() / (end_time - start_time).total_seconds()
            
            if 'memory' in anomaly_type and 'memory' in panel_name.lower():
                # Gradual increase for memory leak
                value = base_value + (progress * 10)  # Increase from 85% to 95%
            elif 'cpu' in anomaly_type and 'cpu' in panel_name.lower():
                # High CPU sustained
                value = base_value + random.uniform(-2, 5)
            elif 'error' in panel_name.lower():
                # Error rate spike during incident
                value = base_value * (1 + progress * 10)  # 10x increase
            elif 'response' in panel_name.lower() or 'duration' in panel_name.lower():
                # Latency increase
                value = base_value * (1 + progress * 4)  # 4x increase
            else:
                value = base_value + random.uniform(-5, 5)
        else:
            # Normal variation (±10%)
            variation = base_value * random.uniform(-0.1, 0.1)
            value = base_value + variation
        
        # Ensure non-negative
        return max(0, value)
    
    def generate_annotation(
        self,
        timestamp: datetime,
        dashboard: str,
        title: str,
        text: str,
        tags: List[str] = None
    ) -> Dict[str, Any]:
        """Generate a Grafana annotation (event marker)"""
        
        return {
            'id': random.randint(1000, 9999),
            'dashboardId': hash(dashboard) % 10000,
            'panelId': None,  # Applies to whole dashboard
            'time': int(timestamp.timestamp() * 1000),
            'timeEnd': int((timestamp + timedelta(minutes=1)).timestamp() * 1000),
            'title': title,
            'text': text,
            'tags': tags or ['incident', 'production'],
            'type': 'annotation'
        }
    
    def generate_alert(
        self,
        timestamp: datetime,
        panel_name: str,
        service: str,
        state: str,
        value: float,
        threshold: float
    ) -> Dict[str, Any]:
        """Generate a Grafana alert"""
        
        return {
            'id': random.randint(1000, 9999),
            'dashboardId': hash('Application Performance') % 10000,
            'panelId': self._get_panel_id(panel_name),
            'name': f'{panel_name} - {service}',
            'state': state,  # 'alerting', 'ok', 'pending', 'no_data'
            'newStateDate': timestamp.isoformat() + 'Z',
            'evalDate': timestamp.isoformat() + 'Z',
            'executionError': '',
            'url': f'https://grafana.company.com/d/dashboard/app-perf?panelId={self._get_panel_id(panel_name)}',
            'evalData': {
                'evalMatches': [{
                    'value': value,
                    'metric': panel_name,
                    'tags': {
                        'service': service,
                        'environment': 'production'
                    }
                }]
            },
            'evalInfo': {
                'threshold': threshold,
                'condition': 'gt' if value > threshold else 'lt'
            }
        }
    
    def generate_for_incident(
        self,
        incident,
        interval_seconds: int = 15
    ) -> List[Dict[str, Any]]:
        """Generate Grafana panel data for a specific incident"""
        
        logs = []
        
        # Get incident details
        incident_type = incident.incident_type
        start_time = incident.start_time
        end_time = incident.end_time
        services = incident.affected_services
        
        # Determine anomaly type
        if 'memory' in incident_type:
            anomaly_type = 'memory_leak'
            relevant_panels = ['Memory Usage', 'JVM Heap Usage', 'GC Time']
        elif 'cpu' in incident_type:
            anomaly_type = 'high_cpu'
            relevant_panels = ['CPU Usage', 'Response Time P95', 'Throughput']
        elif 'database' in incident_type or 'connection' in incident_type:
            anomaly_type = 'connection_pool_exhaustion'
            relevant_panels = ['Connection Pool Usage', 'Query Duration', 'Active Connections']
        elif 'cache' in incident_type:
            anomaly_type = 'cache_miss_storm'
            relevant_panels = ['Cache Hit Rate', 'Cache Miss Rate', 'Query Rate']
        elif 'deployment' in incident_type:
            anomaly_type = 'deployment_failure'
            relevant_panels = ['Error Rate', 'Pod Count', 'Success Rate']
        else:
            anomaly_type = 'service_degradation'
            relevant_panels = ['Error Rate', 'Response Time P95', 'Success Rate']
        
        # Generate time series for relevant panels
        for service in services:
            for panel_name in relevant_panels:
                # Generate full time series
                datapoints = self.generate_time_series_data(
                    start_time, end_time, panel_name, service,
                    interval_seconds, anomaly_type
                )
                
                # Create panel result for each datapoint
                for value, timestamp_ms in datapoints:
                    timestamp = datetime.fromtimestamp(timestamp_ms / 1000)
                    
                    panel_result = self.generate_panel_query_result(
                        timestamp,
                        self._get_dashboard_for_panel(panel_name),
                        panel_name,
                        service,
                        value,
                        self._get_unit_for_panel(panel_name),
                        anomaly_type
                    )
                    
                    logs.append(panel_result)
        
        # Generate annotation for incident start
        annotation = self.generate_annotation(
            start_time,
            'Application Performance',
            f'Incident: {incident_type}',
            f'Incident {incident.incident_id} started affecting {", ".join(services)}',
            tags=['incident', incident_type, incident.severity]
        )
        logs.append(annotation)
        
        # Generate alerts for threshold breaches
        for service in services:
            for panel_name in relevant_panels[:2]:  # Alert on top 2 panels
                value = self._get_base_value(panel_name, anomaly_type)
                threshold = self._get_threshold_for_panel(panel_name)
                
                if value > threshold:
                    alert = self.generate_alert(
                        start_time + timedelta(minutes=5),
                        panel_name,
                        service,
                        'alerting',
                        value,
                        threshold
                    )
                    logs.append(alert)
        
        return logs
    
    def _get_dashboard_for_panel(self, panel_name: str) -> str:
        """Get dashboard name for a panel"""
        for dashboard, panels in self.dashboards.items():
            if panel_name in panels:
                return dashboard
        return 'Application Performance'
    
    def _get_unit_for_panel(self, panel_name: str) -> str:
        """Get unit for a panel metric"""
        if 'rate' in panel_name.lower():
            return 'reqps'
        elif 'time' in panel_name.lower() or 'duration' in panel_name.lower():
            return 'ms'
        elif 'usage' in panel_name.lower() or 'utilization' in panel_name.lower():
            return 'percent'
        elif 'count' in panel_name.lower():
            return 'count'
        elif 'bytes' in panel_name.lower() or 'traffic' in panel_name.lower():
            return 'bytes'
        else:
            return 'none'
    
    def _get_threshold_for_panel(self, panel_name: str) -> float:
        """Get alert threshold for a panel"""
        thresholds = {
            'CPU Usage': 80.0,
            'Memory Usage': 85.0,
            'Error Rate': 5.0,
            'Response Time P95': 500.0,
            'Response Time P99': 1000.0,
            'Connection Pool Usage': 90.0,
            'Cache Hit Rate': 70.0,  # Alert if BELOW this
            'JVM Heap Usage': 85.0
        }
        return thresholds.get(panel_name, 80.0)
    
    def generate_normal_operation_panels(
        self,
        timestamp: datetime,
        service: str,
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """Generate normal operation panel data"""
        
        logs = []
        
        # Select random panels to generate
        all_panels = []
        for panels in self.dashboards.values():
            all_panels.extend(panels)
        
        selected_panels = random.sample(all_panels, min(count, len(all_panels)))
        
        for panel_name in selected_panels:
            value = self._get_base_value(panel_name, None)
            # Add slight variation
            value += value * random.uniform(-0.05, 0.05)
            
            panel_result = self.generate_panel_query_result(
                timestamp,
                self._get_dashboard_for_panel(panel_name),
                panel_name,
                service,
                value,
                self._get_unit_for_panel(panel_name)
            )
            
            logs.append(panel_result)
        
        return logs
