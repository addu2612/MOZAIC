"""
CloudWatch MCP Server Log Generator
Generates hyper-realistic AWS CloudWatch metrics, logs, and alarms
"""
import json
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from utils.realistic_data import realistic_data
from utils.timestamp_utils import TimestampGenerator

class CloudWatchLogGenerator:
    """Generate realistic CloudWatch logs and metrics"""
    
    def __init__(self, services_config: Dict[str, Any]):
        self.services = services_config.get('services', {})
        self.infrastructure = services_config.get('infrastructure', {})
        self.aws_resources = services_config.get('aws_resources', {})
        self.region = 'us-east-1'
        
    def generate_metric_datapoint(
        self,
        timestamp: datetime,
        namespace: str,
        metric_name: str,
        value: float,
        unit: str,
        dimensions: List[Dict[str, str]] = None,
        statistics: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """Generate a CloudWatch metric datapoint"""
        
        datapoint = {
            'Timestamp': timestamp.isoformat() + 'Z',
            'MetricName': metric_name,
            'Namespace': namespace,
            'Value': value,
            'Unit': unit,
            'Dimensions': dimensions or []
        }
        
        # Add statistics if provided
        if statistics:
            datapoint['Statistics'] = statistics
        else:
            # Generate realistic statistics around the value
            datapoint['Statistics'] = {
                'SampleCount': random.randint(10, 100),
                'Sum': value * random.randint(10, 100),
                'Minimum': value * random.uniform(0.7, 0.9),
                'Maximum': value * random.uniform(1.1, 1.3),
                'Average': value
            }
        
        return datapoint
    
    def generate_log_event(
        self,
        timestamp: datetime,
        log_group: str,
        log_stream: str,
        message: str,
        service: str = None
    ) -> Dict[str, Any]:
        """Generate a CloudWatch Logs event"""
        
        return {
            'logGroupName': log_group,
            'logStreamName': log_stream,
            'timestamp': int(timestamp.timestamp() * 1000),
            'message': message,
            'ingestionTime': int((timestamp + timedelta(seconds=random.randint(1, 5))).timestamp() * 1000),
            'eventId': str(uuid.uuid4())
        }
    
    def generate_alarm(
        self,
        timestamp: datetime,
        alarm_name: str,
        metric_name: str,
        namespace: str,
        state: str,
        reason: str,
        threshold: float,
        comparison_operator: str,
        dimensions: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Generate a CloudWatch Alarm state change"""
        
        return {
            'AlarmName': alarm_name,
            'AlarmDescription': f'Alarm for {metric_name} in {namespace}',
            'StateValue': state,  # 'OK', 'ALARM', 'INSUFFICIENT_DATA'
            'StateReason': reason,
            'StateReasonData': json.dumps({
                'version': '1.0',
                'queryDate': timestamp.isoformat() + 'Z',
                'startDate': (timestamp - timedelta(minutes=5)).isoformat() + 'Z',
                'statistic': 'Average',
                'period': 60,
                'recentDatapoints': [random.uniform(threshold * 0.8, threshold * 1.2) for _ in range(5)],
                'threshold': threshold
            }),
            'StateUpdatedTimestamp': timestamp.isoformat() + 'Z',
            'MetricName': metric_name,
            'Namespace': namespace,
            'Statistic': 'Average',
            'Dimensions': dimensions or [],
            'Period': 60,
            'EvaluationPeriods': 2,
            'DatapointsToAlarm': 2,
            'Threshold': threshold,
            'ComparisonOperator': comparison_operator,  # 'GreaterThanThreshold', 'LessThanThreshold', etc.
            'TreatMissingData': 'notBreaching',
            'ActionsEnabled': True,
            'AlarmActions': [f'arn:aws:sns:{self.region}:123456789012:alarm-notifications']
        }
    
    def generate_ecs_metrics(
        self,
        timestamp: datetime,
        service: str,
        cluster_name: str = 'production',
        anomaly_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Generate ECS service metrics"""
        
        service_config = self.services.get(service, {})
        metrics = []
        
        dimensions = [
            {'Name': 'ServiceName', 'Value': service},
            {'Name': 'ClusterName', 'Value': cluster_name}
        ]
        
        # CPU Utilization
        if anomaly_type == 'high_cpu':
            cpu_value = random.uniform(85, 99)
        elif anomaly_type == 'cpu_throttling':
            cpu_value = random.uniform(95, 100)
        else:
            cpu_value = random.uniform(20, 60)
        
        metrics.append(self.generate_metric_datapoint(
            timestamp, 'AWS/ECS', 'CPUUtilization', cpu_value, 'Percent', dimensions
        ))
        
        # Memory Utilization
        if anomaly_type == 'high_memory' or anomaly_type == 'memory_leak':
            memory_value = random.uniform(85, 98)
        else:
            memory_value = random.uniform(30, 70)
        
        metrics.append(self.generate_metric_datapoint(
            timestamp, 'AWS/ECS', 'MemoryUtilization', memory_value, 'Percent', dimensions
        ))
        
        return metrics
    
    def generate_rds_metrics(
        self,
        timestamp: datetime,
        db_instance_identifier: str,
        anomaly_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Generate RDS database metrics"""
        
        metrics = []
        dimensions = [{'Name': 'DBInstanceIdentifier', 'Value': db_instance_identifier}]
        
        # Database Connections
        if anomaly_type == 'connection_pool_exhaustion':
            connections = 100.0  # At max
        else:
            connections = random.uniform(10, 50)
        
        metrics.append(self.generate_metric_datapoint(
            timestamp, 'AWS/RDS', 'DatabaseConnections', connections, 'Count', dimensions
        ))
        
        # Read Latency
        if anomaly_type == 'high_latency' or anomaly_type == 'connection_pool_exhaustion':
            read_latency = random.uniform(200, 1000)
        else:
            read_latency = random.uniform(5, 50)
        
        metrics.append(self.generate_metric_datapoint(
            timestamp, 'AWS/RDS', 'ReadLatency', read_latency, 'Milliseconds', dimensions
        ))
        
        # Write Latency
        if anomaly_type == 'high_latency' or anomaly_type == 'connection_pool_exhaustion':
            write_latency = random.uniform(200, 1000)
        else:
            write_latency = random.uniform(10, 80)
        
        metrics.append(self.generate_metric_datapoint(
            timestamp, 'AWS/RDS', 'WriteLatency', write_latency, 'Milliseconds', dimensions
        ))
        
        # CPU Utilization
        cpu_value = random.uniform(20, 70) if not anomaly_type else random.uniform(70, 95)
        metrics.append(self.generate_metric_datapoint(
            timestamp, 'AWS/RDS', 'CPUUtilization', cpu_value, 'Percent', dimensions
        ))
        
        # Free Storage Space
        if anomaly_type == 'disk_space_exhaustion':
            storage = random.uniform(0, 5)  # GB
        else:
            storage = random.uniform(20, 80)  # GB
        
        metrics.append(self.generate_metric_datapoint(
            timestamp, 'AWS/RDS', 'FreeStorageSpace', storage * 1024 * 1024 * 1024, 'Bytes', dimensions
        ))
        
        return metrics
    
    def generate_elb_metrics(
        self,
        timestamp: datetime,
        load_balancer_name: str,
        anomaly_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Generate ELB (Elastic Load Balancer) metrics"""
        
        metrics = []
        dimensions = [{'Name': 'LoadBalancerName', 'Value': load_balancer_name}]
        
        # Request Count
        if anomaly_type == 'high_traffic' or anomaly_type == 'rate_limit':
            request_count = random.uniform(5000, 15000)
        else:
            request_count = random.uniform(100, 1000)
        
        metrics.append(self.generate_metric_datapoint(
            timestamp, 'AWS/ELB', 'RequestCount', request_count, 'Count', dimensions
        ))
        
        # Healthy Host Count
        if anomaly_type == 'deployment_failure' or anomaly_type == 'service_degradation':
            healthy_hosts = random.randint(0, 2)
        else:
            healthy_hosts = random.randint(3, 10)
        
        metrics.append(self.generate_metric_datapoint(
            timestamp, 'AWS/ELB', 'HealthyHostCount', healthy_hosts, 'Count', dimensions
        ))
        
        # UnHealthy Host Count
        unhealthy = 10 - healthy_hosts if anomaly_type else random.randint(0, 1)
        metrics.append(self.generate_metric_datapoint(
            timestamp, 'AWS/ELB', 'UnHealthyHostCount', unhealthy, 'Count', dimensions
        ))
        
        # 4XX Errors
        if anomaly_type == 'rate_limit':
            errors_4xx = request_count * random.uniform(0.3, 0.6)
        else:
            errors_4xx = request_count * random.uniform(0.01, 0.05)
        
        metrics.append(self.generate_metric_datapoint(
            timestamp, 'AWS/ELB', 'HTTPCode_ELB_4XX', errors_4xx, 'Count', dimensions
        ))
        
        # 5XX Errors
        if anomaly_type == 'deployment_failure' or anomaly_type == 'service_degradation':
            errors_5xx = request_count * random.uniform(0.2, 0.5)
        else:
            errors_5xx = request_count * random.uniform(0.001, 0.01)
        
        metrics.append(self.generate_metric_datapoint(
            timestamp, 'AWS/ELB', 'HTTPCode_ELB_5XX', errors_5xx, 'Count', dimensions
        ))
        
        # Target Response Time
        if anomaly_type == 'high_latency':
            response_time = random.uniform(2000, 5000)
        else:
            response_time = random.uniform(50, 300)
        
        metrics.append(self.generate_metric_datapoint(
            timestamp, 'AWS/ELB', 'TargetResponseTime', response_time, 'Milliseconds', dimensions
        ))
        
        return metrics
    
    def generate_elasticache_metrics(
        self,
        timestamp: datetime,
        cache_cluster_id: str,
        anomaly_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Generate ElastiCache (Redis) metrics"""
        
        metrics = []
        dimensions = [{'Name': 'CacheClusterId', 'Value': cache_cluster_id}]
        
        # Cache Hit Rate
        if anomaly_type == 'cache_miss_storm':
            hit_rate = random.uniform(5, 20)
        else:
            hit_rate = random.uniform(85, 98)
        
        metrics.append(self.generate_metric_datapoint(
            timestamp, 'AWS/ElastiCache', 'CacheHitRate', hit_rate, 'Percent', dimensions
        ))
        
        # CPU Utilization
        cpu_value = random.uniform(15, 40) if not anomaly_type else random.uniform(70, 95)
        metrics.append(self.generate_metric_datapoint(
            timestamp, 'AWS/ElastiCache', 'CPUUtilization', cpu_value, 'Percent', dimensions
        ))
        
        # Network Bytes In/Out
        network_in = random.uniform(1000000, 10000000) if not anomaly_type else random.uniform(50000000, 100000000)
        metrics.append(self.generate_metric_datapoint(
            timestamp, 'AWS/ElastiCache', 'NetworkBytesIn', network_in, 'Bytes', dimensions
        ))
        
        return metrics
    
    def generate_application_logs(
        self,
        timestamp: datetime,
        service: str,
        log_level: str,
        message: str
    ) -> Dict[str, Any]:
        """Generate application logs in CloudWatch format"""
        
        log_group = f'/ecs/production/{service}'
        task_id = uuid.uuid4().hex[:16]
        log_stream = f'{service}/{service}/{task_id}'
        
        # Format message with timestamp and level
        formatted_message = f"{timestamp.isoformat()} {log_level.upper()} {message}"
        
        return self.generate_log_event(
            timestamp, log_group, log_stream, formatted_message, service
        )
    
    def generate_for_incident(
        self,
        incident,
        metric_frequency_seconds: int = 60
    ) -> List[Dict[str, Any]]:
        """Generate CloudWatch metrics for a specific incident"""
        
        logs = []
        
        # Get incident details
        incident_type = incident.incident_type
        start_time = incident.start_time
        end_time = incident.end_time
        services = incident.affected_services
        
        # Determine anomaly type
        if 'memory' in incident_type:
            anomaly_type = 'memory_leak'
        elif 'cpu' in incident_type:
            anomaly_type = 'high_cpu'
        elif 'database' in incident_type or 'connection' in incident_type:
            anomaly_type = 'connection_pool_exhaustion'
        elif 'deployment' in incident_type:
            anomaly_type = 'deployment_failure'
        elif 'disk' in incident_type:
            anomaly_type = 'disk_space_exhaustion'
        elif 'cache' in incident_type:
            anomaly_type = 'cache_miss_storm'
        else:
            anomaly_type = 'service_degradation'
        
        # Generate metrics throughout incident
        current_time = start_time
        while current_time <= end_time:
            for service in services:
                # ECS metrics
                if service in self.services:
                    ecs_metrics = self.generate_ecs_metrics(
                        current_time, service, anomaly_type=anomaly_type
                    )
                    logs.extend(ecs_metrics)
                
                # Database metrics
                if service == 'postgres-primary' or 'database' in incident_type:
                    rds_metrics = self.generate_rds_metrics(
                        current_time, 'production-postgres', anomaly_type=anomaly_type
                    )
                    logs.extend(rds_metrics)
                
                # Cache metrics
                if service == 'redis-cache' or 'cache' in incident_type:
                    cache_metrics = self.generate_elasticache_metrics(
                        current_time, 'production-redis', anomaly_type=anomaly_type
                    )
                    logs.extend(cache_metrics)
            
            # ELB metrics
            elb_metrics = self.generate_elb_metrics(
                current_time, 'production-alb', anomaly_type=anomaly_type
            )
            logs.extend(elb_metrics)
            
            # Generate alarms when thresholds exceeded
            if random.random() < 0.3:  # 30% chance of alarm
                alarm = self.generate_alarm(
                    timestamp=current_time,
                    alarm_name=f'{services[0]}-{anomaly_type}-alarm',
                    metric_name='CPUUtilization' if 'cpu' in anomaly_type else 'MemoryUtilization',
                    namespace='AWS/ECS',
                    state='ALARM',
                    reason=f'Threshold Crossed: 1 datapoint [95.0] was greater than the threshold (80.0)',
                    threshold=80.0,
                    comparison_operator='GreaterThanThreshold',
                    dimensions=[{'Name': 'ServiceName', 'Value': services[0]}]
                )
                logs.append(alarm)
            
            current_time += timedelta(seconds=metric_frequency_seconds)
        
        return logs
    
    def generate_normal_operation_metrics(
        self,
        timestamp: datetime,
        service: str
    ) -> List[Dict[str, Any]]:
        """Generate normal operation metrics"""
        
        metrics = []
        
        # ECS metrics
        metrics.extend(self.generate_ecs_metrics(timestamp, service))
        
        # Occasionally add RDS metrics
        if random.random() < 0.3:
            metrics.extend(self.generate_rds_metrics(timestamp, 'production-postgres'))
        
        # Occasionally add ELB metrics
        if random.random() < 0.3:
            metrics.extend(self.generate_elb_metrics(timestamp, 'production-alb'))
        
        return metrics
