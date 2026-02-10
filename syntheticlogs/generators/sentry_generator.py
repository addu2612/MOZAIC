"""
Sentry MCP Server Log Generator
Generates hyper-realistic Sentry error tracking logs
"""
import json
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from utils.realistic_data import realistic_data
from utils.timestamp_utils import TimestampGenerator

class SentryLogGenerator:
    """Generate realistic Sentry error tracking logs"""
    
    def __init__(self, services_config: Dict[str, Any]):
        self.services = services_config.get('services', {})
        self.project_name = "production-backend"
        self.organization = "company"
        
    def generate_error_event(
        self,
        timestamp: datetime,
        error_type: str,
        service: str,
        message: str,
        level: str = 'error',
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate a complete Sentry error event"""
        
        service_config = self.services.get(service, {})
        event_id = uuid.uuid4().hex
        
        # Determine platform/language
        platforms = {
            'python': ['CPython', '3.9.16'],
            'node': ['Node.js', '18.17.0'],
            'java': ['Java', '17.0.8']
        }
        platform = random.choice(list(platforms.keys()))
        runtime_name, runtime_version = platforms[platform]
        
        event = {
            'event_id': event_id,
            'timestamp': timestamp.isoformat() + 'Z',
            'received': (timestamp + timedelta(milliseconds=random.randint(10, 100))).isoformat() + 'Z',
            'platform': platform,
            'level': level,
            'logger': self._get_logger_name(service, platform),
            'transaction': self._get_transaction_name(service),
            'server_name': realistic_data.generate_pod_name(service),
            'release': service_config.get('image', '').split(':')[-1] if service_config.get('image') else f'v{random.randint(1,5)}.{random.randint(0,20)}.{random.randint(0,50)}',
            'environment': 'production',
            'message': {
                'formatted': message,
                'message': message
            },
            'exception': {
                'values': [{
                    'type': error_type,
                    'value': message,
                    'module': self._get_module_name(service, platform, error_type),
                    'stacktrace': {
                        'frames': realistic_data.generate_stack_trace(error_type, service)
                    },
                    'mechanism': {
                        'type': 'generic',
                        'handled': random.choice([True, False]),
                        'synthetic': False
                    }
                }]
            },
            'breadcrumbs': {
                'values': realistic_data.generate_breadcrumbs(random.randint(5, 15))
            },
            'user': self._generate_user_context(),
            'request': self._generate_request_context(service),
            'contexts': {
                'runtime': {
                    'name': runtime_name,
                    'version': runtime_version,
                    'type': 'runtime'
                },
                'os': {
                    'name': 'Linux',
                    'version': '5.15.0-1040-aws',
                    'kernel_version': '5.15.0-1040-aws',
                    'type': 'os'
                },
                'trace': {
                    'trace_id': context.get('trace_id') if context else realistic_data.generate_trace_id(),
                    'span_id': uuid.uuid4().hex[:16],
                    'type': 'trace'
                },
                'device': {
                    'family': 'Other',
                    'model': 'Other',
                    'type': 'device'
                }
            },
            'tags': self._generate_tags(service, error_type, context),
            'extra': context if context else {},
            'fingerprint': self._generate_fingerprint(error_type, service),
            'sdk': {
                'name': f'sentry.{platform}',
                'version': '1.31.0',
                'packages': [{
                    'name': f'pypi:sentry-sdk' if platform == 'python' else f'npm:@sentry/node',
                    'version': '1.31.0'
                }]
            },
            'project': self.project_name,
            'culprit': self._get_culprit(service, platform)
        }
        
        return event
    
    def _get_logger_name(self, service: str, platform: str) -> str:
        """Generate realistic logger name"""
        if platform == 'python':
            return random.choice([
                f'{service}.handlers',
                f'{service}.services',
                f'{service}.middleware',
                'uvicorn.error',
                'gunicorn.error',
                'django.request',
                'flask.app'
            ])
        elif platform == 'node':
            return random.choice([
                f'{service}.controller',
                f'{service}.service',
                'express',
                'koa'
            ])
        else:
            return random.choice([
                f'com.company.{service}.controller',
                f'com.company.{service}.service',
                'org.springframework.web'
            ])
    
    def _get_transaction_name(self, service: str) -> str:
        """Generate transaction name"""
        service_config = self.services.get(service, {})
        endpoints = service_config.get('endpoints', ['/'])
        endpoint = random.choice(endpoints)
        method = random.choice(['GET', 'POST', 'PUT', 'DELETE'])
        
        return f'{method} {endpoint}'
    
    def _get_module_name(self, service: str, platform: str, error_type: str) -> str:
        """Generate module name where error occurred"""
        if platform == 'python':
            if 'Database' in error_type or 'SQL' in error_type:
                return 'sqlalchemy.pool'
            elif 'Connection' in error_type or 'Timeout' in error_type:
                return 'urllib3.connectionpool'
            else:
                return f'app.{service}.handlers'
        elif platform == 'node':
            return f'{service}/lib/index'
        else:
            return f'com.company.{service}.Main'
    
    def _generate_user_context(self) -> Dict[str, Any]:
        """Generate user context"""
        if random.random() > 0.3:  # 70% have user context
            return {
                'id': realistic_data.generate_user_id(),
                'ip_address': realistic_data.generate_ip_address(),
                'username': None,  # Usually not logged for privacy
                'email': None
            }
        return {}
    
    def _generate_request_context(self, service: str) -> Dict[str, Any]:
        """Generate HTTP request context"""
        service_config = self.services.get(service, {})
        endpoints = service_config.get('endpoints', ['/'])
        endpoint = random.choice(endpoints)
        method = random.choice(['GET', 'POST', 'PUT', 'DELETE'])
        
        return {
            'url': f'https://api.company.com{endpoint}',
            'method': method,
            'headers': {
                'User-Agent': realistic_data.generate_user_agent(),
                'Accept': 'application/json',
                'Content-Type': 'application/json' if method in ['POST', 'PUT'] else None,
                'X-Request-Id': realistic_data.generate_request_id(),
                'X-Forwarded-For': realistic_data.generate_ip_address()
            },
            'query_string': self._generate_query_string() if method == 'GET' else None,
            'env': {
                'REMOTE_ADDR': realistic_data.generate_ip_address(),
                'SERVER_NAME': f'{service}.company.internal',
                'SERVER_PORT': str(service_config.get('port', 8080))
            }
        }
    
    def _generate_query_string(self) -> str:
        """Generate realistic query string"""
        params = []
        if random.random() > 0.5:
            params.append(f'page={random.randint(1, 100)}')
        if random.random() > 0.5:
            params.append(f'limit={random.choice([10, 20, 50, 100])}')
        if random.random() > 0.7:
            params.append(f'sort={random.choice(["created_at", "updated_at", "name"])}')
        
        return '&'.join(params) if params else ''
    
    def _generate_tags(self, service: str, error_type: str, context: Dict = None) -> Dict[str, str]:
        """Generate event tags"""
        tags = {
            'environment': 'production',
            'server_name': realistic_data.generate_pod_name(service),
            'service': service,
            'error_type': error_type,
            'level': 'error'
        }
        
        # Add error category
        if 'Database' in error_type or 'SQL' in error_type or 'Connection' in error_type:
            tags['category'] = 'database'
        elif 'Memory' in error_type or 'OOM' in error_type:
            tags['category'] = 'memory'
        elif 'Timeout' in error_type:
            tags['category'] = 'performance'
        elif 'HTTP' in error_type or 'Status' in error_type:
            tags['category'] = 'http'
        else:
            tags['category'] = 'application'
        
        if context:
            for key, value in context.items():
                if isinstance(value, (str, int, float, bool)):
                    tags[key] = str(value)
        
        return tags
    
    def _generate_fingerprint(self, error_type: str, service: str) -> List[str]:
        """Generate fingerprint for grouping similar errors"""
        return [
            error_type,
            service,
            random.choice(['handler', 'service', 'middleware'])
        ]
    
    def _get_culprit(self, service: str, platform: str) -> str:
        """Generate culprit (code location)"""
        if platform == 'python':
            return f'{service}.handlers.{random.choice(["user", "order", "payment"])}_handler'
        elif platform == 'node':
            return f'{service}/controllers/{random.choice(["user", "order", "payment"])}.js'
        else:
            return f'com.company.{service}.controller.{random.choice(["User", "Order", "Payment"])}Controller.handle'
    
    def generate_performance_transaction(
        self,
        timestamp: datetime,
        service: str,
        transaction_name: str,
        duration_ms: float,
        status: str = 'ok'
    ) -> Dict[str, Any]:
        """Generate Sentry performance transaction"""
        
        service_config = self.services.get(service, {})
        
        transaction = {
            'event_id': uuid.uuid4().hex,
            'type': 'transaction',
            'timestamp': timestamp.isoformat() + 'Z',
            'start_timestamp': (timestamp - timedelta(milliseconds=duration_ms)).isoformat() + 'Z',
            'level': 'info',
            'platform': 'python',
            'server_name': realistic_data.generate_pod_name(service),
            'release': service_config.get('image', '').split(':')[-1] if service_config.get('image') else 'unknown',
            'environment': 'production',
            'transaction': transaction_name,
            'transaction_info': {
                'source': 'route'
            },
            'contexts': {
                'trace': {
                    'trace_id': realistic_data.generate_trace_id(),
                    'span_id': uuid.uuid4().hex[:16],
                    'op': 'http.server',
                    'status': status,
                    'type': 'trace'
                }
            },
            'spans': self._generate_spans(duration_ms),
            'measurements': {
                'fp': {'value': duration_ms * 0.1, 'unit': 'millisecond'},
                'fcp': {'value': duration_ms * 0.3, 'unit': 'millisecond'},
                'lcp': {'value': duration_ms * 0.8, 'unit': 'millisecond'},
                'fid': {'value': random.uniform(1, 10), 'unit': 'millisecond'}
            },
            'request': {
                'url': f'https://api.company.com{transaction_name.split()[1]}',
                'method': transaction_name.split()[0]
            },
            'tags': {
                'environment': 'production',
                'service': service,
                'http.status_code': '200' if status == 'ok' else '500'
            }
        }
        
        return transaction
    
    def _generate_spans(self, total_duration_ms: float) -> List[Dict[str, Any]]:
        """Generate child spans for transaction"""
        spans = []
        remaining_duration = total_duration_ms
        
        # Database query span
        db_duration = remaining_duration * random.uniform(0.2, 0.4)
        spans.append({
            'span_id': uuid.uuid4().hex[:16],
            'parent_span_id': None,
            'trace_id': realistic_data.generate_trace_id(),
            'op': 'db.query',
            'description': realistic_data.generate_sql_query(),
            'start_timestamp': 0,
            'timestamp': db_duration / 1000,
            'tags': {
                'db.type': 'postgresql'
            }
        })
        remaining_duration -= db_duration
        
        # HTTP request span
        if random.random() > 0.5:
            http_duration = remaining_duration * random.uniform(0.2, 0.5)
            spans.append({
                'span_id': uuid.uuid4().hex[:16],
                'parent_span_id': None,
                'trace_id': realistic_data.generate_trace_id(),
                'op': 'http.client',
                'description': f'GET {random.choice(["/api/v1/users", "/api/v1/products"])}',
                'start_timestamp': db_duration / 1000,
                'timestamp': (db_duration + http_duration) / 1000,
                'tags': {
                    'http.status_code': '200'
                }
            })
            remaining_duration -= http_duration
        
        return spans
    
    def generate_for_incident(
        self,
        incident,
        error_frequency: str = 'high'
    ) -> List[Dict[str, Any]]:
        """Generate Sentry logs for a specific incident"""
        
        logs = []
        
        # Get incident details
        incident_type = incident.incident_type
        start_time = incident.start_time
        end_time = incident.end_time
        services = incident.affected_services
        
        # Frequency mapping
        frequencies = {
            'low': 0.1,      # 1 error per 10 seconds
            'medium': 0.5,   # 1 error per 2 seconds
            'high': 2.0,     # 2 errors per second
            'very_high': 5.0 # 5 errors per second
        }
        
        errors_per_second = frequencies.get(error_frequency, 1.0)
        duration_seconds = (end_time - start_time).total_seconds()
        num_errors = int(duration_seconds * errors_per_second)
        
        # Generate errors throughout incident
        for i in range(num_errors):
            # Distribute errors across incident timeline
            offset_seconds = (duration_seconds / num_errors) * i
            timestamp = start_time + timedelta(seconds=offset_seconds)
            
            # Add some randomness
            timestamp = timestamp + timedelta(seconds=random.uniform(-5, 5))
            
            service = random.choice(services)
            
            # Determine error type based on incident
            if 'memory' in incident_type:
                error_type = random.choice(['MemoryError', 'OutOfMemoryError', 'AllocationFailedException'])
                message = realistic_data.generate_error_message(error_type)
            elif 'database' in incident_type or 'connection' in incident_type:
                error_type = random.choice(['PoolTimeoutError', 'DatabaseConnectionError', 'PSQLException'])
                message = realistic_data.generate_error_message(error_type)
            elif 'deployment' in incident_type:
                error_type = random.choice(['ConfigurationError', 'ImportError', 'ModuleNotFoundError'])
                message = realistic_data.generate_error_message(error_type)
            elif 'timeout' in incident_type or 'network' in incident_type:
                error_type = random.choice(['TimeoutError', 'ConnectionError', 'NetworkError'])
                message = realistic_data.generate_error_message(error_type)
            else:
                error_type = random.choice(['RuntimeError', 'ValueError', 'TypeError'])
                message = realistic_data.generate_error_message(error_type)
            
            # Generate error event
            error_event = self.generate_error_event(
                timestamp=timestamp,
                error_type=error_type,
                service=service,
                message=message,
                level='error' if i < num_errors * 0.8 else 'fatal',
                context={'incident_id': incident.incident_id, 'correlation_id': incident.correlation_id}
            )
            
            logs.append(error_event)
        
        return logs
    
    def generate_normal_operation_logs(
        self,
        timestamp: datetime,
        service: str,
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """Generate normal operation Sentry logs (warnings, info)"""
        
        logs = []
        
        for _ in range(count):
            # Mostly warnings and occasional errors
            if random.random() < 0.8:
                # Warning level
                level = 'warning'
                error_type = random.choice(['DeprecationWarning', 'UserWarning', 'ResourceWarning'])
                messages = [
                    'Slow database query detected',
                    'Cache miss rate above threshold',
                    'High memory usage detected',
                    'Deprecated API endpoint used'
                ]
            else:
                # Occasional transient errors
                level = 'error'
                error_type = random.choice(['TransientError', 'RetryableError'])
                messages = [
                    'Temporary connection error (retrying)',
                    'Request timeout (will retry)',
                    'Service temporarily unavailable'
                ]
            
            event = self.generate_error_event(
                timestamp=timestamp,
                error_type=error_type,
                service=service,
                message=random.choice(messages),
                level=level
            )
            
            logs.append(event)
        
        return logs
