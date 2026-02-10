"""
Kubernetes MCP Server Log Generator
Generates hyper-realistic Kubernetes logs including pod logs, events, and metrics
"""
import json
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import yaml

from utils.realistic_data import realistic_data
from utils.timestamp_utils import TimestampGenerator

class KubernetesLogGenerator:
    """Generate realistic Kubernetes logs and events"""
    
    def __init__(self, services_config: Dict[str, Any]):
        self.services = services_config.get('services', {})
        self.infrastructure = services_config.get('infrastructure', {})
        self.cluster_name = "production-us-east-1"
        self.cluster_version = "v1.27.3"
        
    def generate_pod_log_entry(
        self,
        timestamp: datetime,
        service: str,
        pod_name: str,
        log_level: str,
        message: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate a single pod log entry"""
        
        service_config = self.services.get(service, {})
        
        log_entry = {
            'timestamp': timestamp.isoformat() + 'Z',
            'stream': random.choice(['stdout', 'stderr']),
            'log': self._format_application_log(
                timestamp, log_level, message, context
            ),
            'kubernetes': {
                'pod_name': pod_name,
                'namespace_name': service_config.get('namespace', 'production'),
                'container_name': service,
                'container_id': f"docker://{realistic_data.generate_container_id()}",
                'pod_id': str(uuid.uuid4()),
                'labels': {
                    'app': service,
                    'version': service_config.get('image', '').split(':')[-1] if service_config.get('image') else 'unknown',
                    'environment': 'production',
                    'tier': 'backend'
                },
                'host': realistic_data.generate_node_name(service_config.get('resources', {}).get('limits', {}).get('cpu', 'unknown'))
            }
        }
        
        return log_entry
    
    def _format_application_log(
        self,
        timestamp: datetime,
        log_level: str,
        message: str,
        context: Dict[str, Any] = None
    ) -> str:
        """Format application log in various realistic formats"""
        
        format_type = random.choice(['json', 'logfmt', 'plain', 'structured'])
        
        if format_type == 'json':
            log_data = {
                'timestamp': timestamp.isoformat(),
                'level': log_level.upper(),
                'message': message,
                'logger': random.choice([
                    'com.company.service.Controller',
                    'app.handlers.UserHandler',
                    'service.middleware.RequestLogger',
                    'app.database.ConnectionPool'
                ])
            }
            
            if context:
                log_data.update(context)
            
            # Add common structured fields
            log_data.update({
                'trace_id': context.get('trace_id') if context else realistic_data.generate_trace_id(),
                'span_id': str(uuid.uuid4().hex[:16]),
                'service_name': context.get('service') if context else 'unknown'
            })
            
            return json.dumps(log_data)
        
        elif format_type == 'logfmt':
            parts = [
                f'time="{timestamp.isoformat()}"',
                f'level={log_level}',
                f'msg="{message}"'
            ]
            
            if context:
                for key, value in context.items():
                    if isinstance(value, str):
                        parts.append(f'{key}="{value}"')
                    else:
                        parts.append(f'{key}={value}')
            
            return ' '.join(parts)
        
        elif format_type == 'structured':
            # Python logging style
            logger_name = random.choice([
                'uvicorn.access',
                'gunicorn.error',
                'django.request',
                'flask.app',
                'app.services.user'
            ])
            
            return f"{timestamp.strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]} {log_level.upper():8} [{logger_name}] {message}"
        
        else:  # plain
            return f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')} {log_level.upper()} {message}"
    
    def generate_event(
        self,
        timestamp: datetime,
        event_type: str,
        reason: str,
        message: str,
        service: str,
        pod_name: str,
        severity: str = 'Normal'
    ) -> Dict[str, Any]:
        """Generate a Kubernetes event"""
        
        service_config = self.services.get(service, {})
        
        event = {
            'apiVersion': 'v1',
            'kind': 'Event',
            'metadata': {
                'name': f"{pod_name}.{uuid.uuid4().hex[:16]}",
                'namespace': service_config.get('namespace', 'production'),
                'creationTimestamp': timestamp.isoformat() + 'Z',
                'resourceVersion': str(random.randint(100000, 999999))
            },
            'involvedObject': {
                'kind': 'Pod',
                'namespace': service_config.get('namespace', 'production'),
                'name': pod_name,
                'uid': str(uuid.uuid4()),
                'apiVersion': 'v1',
                'resourceVersion': str(random.randint(100000, 999999)),
                'fieldPath': 'spec.containers{' + service + '}'
            },
            'reason': reason,
            'message': message,
            'source': {
                'component': random.choice(['kubelet', 'default-scheduler', 'controller-manager', 'kube-apiserver']),
                'host': realistic_data.generate_node_name('m5.2xlarge')
            },
            'firstTimestamp': timestamp.isoformat() + 'Z',
            'lastTimestamp': timestamp.isoformat() + 'Z',
            'count': 1,
            'type': severity,
            'eventTime': None,
            'reportingComponent': '',
            'reportingInstance': ''
        }
        
        return event
    
    def generate_normal_operation_logs(
        self,
        timestamp: datetime,
        service: str,
        pod_name: str,
        count: int = 10
    ) -> List[Dict[str, Any]]:
        """Generate normal operation logs"""
        
        logs = []
        service_config = self.services.get(service, {})
        endpoints = service_config.get('endpoints', ['/health'])
        
        for _ in range(count):
            log_type = random.choices(
                ['access', 'info', 'debug', 'query'],
                weights=[0.5, 0.3, 0.15, 0.05]
            )[0]
            
            if log_type == 'access':
                # HTTP access log
                endpoint = random.choice(endpoints)
                status_code = realistic_data.generate_http_status_code()
                latency = realistic_data.generate_latency_ms()
                method = random.choice(['GET', 'POST', 'PUT', 'DELETE'])
                
                message = f'{method} {endpoint} {status_code} {latency:.2f}ms'
                context = {
                    'http_method': method,
                    'http_path': endpoint,
                    'http_status': status_code,
                    'response_time_ms': latency,
                    'ip': realistic_data.generate_ip_address(),
                    'user_agent': realistic_data.generate_user_agent()
                }
                
                log_entry = self.generate_pod_log_entry(
                    timestamp, service, pod_name, 'info', message, context
                )
                logs.append(log_entry)
            
            elif log_type == 'info':
                # General info log
                messages = [
                    'Request processed successfully',
                    'Cache hit for key',
                    'Background task completed',
                    'Health check passed',
                    'Metrics exported successfully'
                ]
                
                log_entry = self.generate_pod_log_entry(
                    timestamp, service, pod_name, 'info',
                    random.choice(messages),
                    realistic_data.generate_log_context()
                )
                logs.append(log_entry)
            
            elif log_type == 'debug':
                # Debug log
                messages = [
                    f'Processing request with ID {realistic_data.generate_request_id()}',
                    f'Database query executed in {random.uniform(10, 100):.2f}ms',
                    f'Cache lookup for key {uuid.uuid4().hex[:8]}',
                    f'Validating user input',
                    f'Serializing response data'
                ]
                
                log_entry = self.generate_pod_log_entry(
                    timestamp, service, pod_name, 'debug',
                    random.choice(messages)
                )
                logs.append(log_entry)
            
            elif log_type == 'query':
                # Database query log
                query = realistic_data.generate_sql_query()
                duration = random.uniform(10, 500)
                
                message = f'Query executed: {query} (duration: {duration:.2f}ms)'
                context = {
                    'query': query,
                    'duration_ms': duration,
                    'rows_affected': random.randint(0, 1000)
                }
                
                log_entry = self.generate_pod_log_entry(
                    timestamp, service, pod_name, 'info', message, context
                )
                logs.append(log_entry)
        
        return logs
    
    def generate_oom_killed_sequence(
        self,
        start_time: datetime,
        service: str,
        pod_name: str
    ) -> List[Dict[str, Any]]:
        """Generate realistic OOMKilled event sequence"""
        
        entries = []
        
        # Warning logs as memory increases
        warning_time = start_time - timedelta(minutes=10)
        for i in range(5):
            timestamp = warning_time + timedelta(minutes=i * 2)
            memory_usage = 85 + (i * 2)
            
            log_entry = self.generate_pod_log_entry(
                timestamp, service, pod_name, 'warning',
                f'High memory usage detected: {memory_usage}%',
                {'memory_usage_percent': memory_usage}
            )
            entries.append(log_entry)
        
        # Critical memory warning
        critical_time = start_time - timedelta(minutes=2)
        entries.append(
            self.generate_event(
                critical_time,
                'Warning',
                'HighMemoryUsage',
                f'Memory usage critical at 95%',
                service,
                pod_name,
                'Warning'
            )
        )
        
        # OOM error in logs
        oom_log_time = start_time - timedelta(seconds=30)
        entries.append(
            self.generate_pod_log_entry(
                oom_log_time, service, pod_name, 'error',
                'java.lang.OutOfMemoryError: Java heap space',
                {
                    'error_type': 'OutOfMemoryError',
                    'heap_size': f'{random.randint(512, 2048)}Mi'
                }
            )
        )
        
        # OOMKilled event
        entries.append(
            self.generate_event(
                start_time,
                'OOMKilled',
                'OOMKilled',
                f'Container {service} in pod {pod_name} was OOMKilled',
                service,
                pod_name,
                'Warning'
            )
        )
        
        # Pod restart event
        restart_time = start_time + timedelta(seconds=5)
        entries.append(
            self.generate_event(
                restart_time,
                'Restarted',
                'ContainerRestarted',
                f'Container {service} restarted with exit code 137 (OOMKilled)',
                service,
                pod_name,
                'Normal'
            )
        )
        
        # Post-restart logs
        startup_time = restart_time + timedelta(seconds=10)
        entries.append(
            self.generate_pod_log_entry(
                startup_time, service, pod_name, 'info',
                'Application starting...',
                {'restart_count': random.randint(1, 5)}
            )
        )
        
        return entries
    
    def generate_crash_loop_backoff_sequence(
        self,
        start_time: datetime,
        service: str,
        pod_name: str,
        crash_count: int = 5
    ) -> List[Dict[str, Any]]:
        """Generate CrashLoopBackOff sequence"""
        
        entries = []
        
        for i in range(crash_count):
            crash_time = start_time + timedelta(minutes=i * 2)
            
            # Application error log
            error_messages = [
                'Failed to connect to database: connection refused',
                'Configuration error: missing required environment variable DATABASE_URL',
                'Import error: module not found',
                'Fatal: unable to bind to port 8080: address already in use',
                'Panic: runtime error: invalid memory address or nil pointer dereference'
            ]
            
            entries.append(
                self.generate_pod_log_entry(
                    crash_time, service, pod_name, 'error',
                    random.choice(error_messages),
                    {'exit_code': 1, 'restart_count': i}
                )
            )
            
            # CrashLoopBackOff event
            backoff_time = crash_time + timedelta(seconds=10)
            entries.append(
                self.generate_event(
                    backoff_time,
                    'BackOff',
                    'CrashLoopBackOff',
                    f'Back-off restarting failed container (restart count: {i+1})',
                    service,
                    pod_name,
                    'Warning'
                )
            )
        
        return entries
    
    def generate_image_pull_backoff(
        self,
        timestamp: datetime,
        service: str,
        pod_name: str,
        image_tag: str = None
    ) -> List[Dict[str, Any]]:
        """Generate ImagePullBackOff events"""
        
        if image_tag is None:
            image_tag = f'v{random.randint(1,5)}.{random.randint(0,20)}.{random.randint(0,50)}'
        
        image_name = realistic_data.generate_image_name(service, image_tag)
        
        entries = []
        
        # Failed pull attempts
        for i in range(3):
            pull_time = timestamp + timedelta(seconds=i * 20)
            
            entries.append(
                self.generate_event(
                    pull_time,
                    'Failed',
                    'Failed',
                    f'Failed to pull image "{image_name}": rpc error: code = Unknown desc = Error response from daemon: manifest for {image_name} not found',
                    service,
                    pod_name,
                    'Warning'
                )
            )
            
            backoff_time = pull_time + timedelta(seconds=10)
            entries.append(
                self.generate_event(
                    backoff_time,
                    'BackOff',
                    'ImagePullBackOff',
                    f'Back-off pulling image "{image_name}"',
                    service,
                    pod_name,
                    'Warning'
                )
            )
        
        return entries
    
    def generate_pod_pending_events(
        self,
        timestamp: datetime,
        service: str,
        pod_name: str,
        reason: str = 'InsufficientResources'
    ) -> List[Dict[str, Any]]:
        """Generate pod pending events"""
        
        service_config = self.services.get(service, {})
        resources = service_config.get('resources', {})
        
        messages = {
            'InsufficientResources': f"0/10 nodes are available: 10 Insufficient memory",
            'InsufficientCPU': f"0/10 nodes are available: 10 Insufficient cpu",
            'NodeAffinity': "0/10 nodes are available: 10 node(s) didn't match pod affinity rules",
            'PodTooBigForNode': "Pod exceeds node capacity"
        }
        
        return [
            self.generate_event(
                timestamp,
                'Pending',
                reason,
                messages.get(reason, 'Pod cannot be scheduled'),
                service,
                pod_name,
                'Warning'
            )
        ]
    
    def generate_node_events(
        self,
        timestamp: datetime,
        node_name: str,
        event_type: str
    ) -> List[Dict[str, Any]]:
        """Generate node-level events"""
        
        events = []
        
        if event_type == 'NodeNotReady':
            events.append({
                'apiVersion': 'v1',
                'kind': 'Event',
                'metadata': {
                    'name': f"{node_name}.{uuid.uuid4().hex[:16]}",
                    'namespace': 'default',
                    'creationTimestamp': timestamp.isoformat() + 'Z'
                },
                'involvedObject': {
                    'kind': 'Node',
                    'name': node_name,
                    'uid': str(uuid.uuid4())
                },
                'reason': 'NodeNotReady',
                'message': 'Node is not ready',
                'type': 'Warning',
                'source': {
                    'component': 'kubelet',
                    'host': node_name
                },
                'firstTimestamp': timestamp.isoformat() + 'Z',
                'lastTimestamp': timestamp.isoformat() + 'Z',
                'count': 1
            })
        
        elif event_type == 'DiskPressure':
            events.append({
                'apiVersion': 'v1',
                'kind': 'Event',
                'metadata': {
                    'name': f"{node_name}.{uuid.uuid4().hex[:16]}",
                    'namespace': 'default',
                    'creationTimestamp': timestamp.isoformat() + 'Z'
                },
                'involvedObject': {
                    'kind': 'Node',
                    'name': node_name,
                    'uid': str(uuid.uuid4())
                },
                'reason': 'NodeHasDiskPressure',
                'message': f'Node {node_name} status is now: NodeHasDiskPressure',
                'type': 'Warning',
                'source': {
                    'component': 'kubelet',
                    'host': node_name
                },
                'firstTimestamp': timestamp.isoformat() + 'Z',
                'lastTimestamp': timestamp.isoformat() + 'Z',
                'count': 1
            })
        
        return events
    
    def generate_metrics(
        self,
        timestamp: datetime,
        service: str,
        pod_name: str,
        anomaly_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate pod metrics"""
        
        service_config = self.services.get(service, {})
        resources = service_config.get('resources', {})
        
        # Base metrics
        cpu_base = 300  # millicores
        memory_base = 256 * 1024 * 1024  # bytes
        
        if anomaly_type == 'high_cpu':
            cpu_usage = cpu_base * random.uniform(2.5, 3.5)
        elif anomaly_type == 'high_memory':
            memory_usage = memory_base * random.uniform(3.0, 4.0)
        else:
            cpu_usage = cpu_base * random.uniform(0.3, 0.8)
            memory_usage = memory_base * random.uniform(0.4, 0.7)
        
        return {
            'timestamp': timestamp.isoformat() + 'Z',
            'pod': pod_name,
            'namespace': service_config.get('namespace', 'production'),
            'containers': [{
                'name': service,
                'usage': {
                    'cpu': f'{int(cpu_usage)}n',
                    'memory': f'{int(memory_usage)}Ki'
                }
            }]
        }

    def generate_for_incident(self, incident) -> List[Dict[str, Any]]:
        """Generate Kubernetes logs for a specific incident"""
        logs = []
        
        incident_type = incident.incident_type
        start_time = incident.start_time
        end_time = incident.end_time
        services = incident.affected_services
        
        for service in services:
            pod_name = realistic_data.generate_pod_name(service)
            
            if 'memory' in incident_type:
                logs.extend(self.generate_oom_killed_sequence(start_time, service, pod_name))
            elif 'deployment' in incident_type:
                logs.extend(self.generate_crash_loop_backoff_sequence(start_time, service, pod_name, crash_count=5))
                logs.extend(self.generate_image_pull_backoff(start_time, service, pod_name))
            else:
                # Generic pod events
                logs.append(self.generate_event(
                    start_time, 'Warning', incident_type,
                    f'Incident detected: {incident_type}',
                    service, pod_name, 'Warning'
                ))
        
        return logs
