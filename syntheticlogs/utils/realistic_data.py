"""
Realistic Data Generation Utilities
Provides realistic data for synthetic log generation
"""
import random
import hashlib
import uuid
from datetime import datetime, timedelta
from faker import Faker
from typing import List, Dict, Any

fake = Faker()

class RealisticDataGenerator:
    """Generate realistic data for logs"""
    
    def __init__(self):
        self.fake = Faker()
        self.user_cache = {}
        self.ip_cache = {}
        self.request_id_counter = 0
        
    def generate_ip_address(self, region: str = None) -> str:
        """Generate realistic IP addresses by region"""
        ip_ranges = {
            'us-east': ['54.', '52.', '34.', '3.'],
            'us-west': ['44.', '54.', '35.', '50.'],
            'eu-west': ['18.', '52.', '35.', '54.'],
            'ap-southeast': ['13.', '52.', '54.', '3.'],
            'other': ['20.', '40.', '51.', '13.']
        }
        
        region = region or random.choice(list(ip_ranges.keys()))
        prefix = random.choice(ip_ranges[region])
        
        return f"{prefix}{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
    
    def generate_user_id(self) -> str:
        """Generate consistent user IDs"""
        return f"user_{hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:12]}"
    
    def generate_session_id(self) -> str:
        """Generate session ID"""
        return f"sess_{hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:16]}"
    
    def generate_trace_id(self) -> str:
        """Generate distributed tracing ID"""
        return f"{uuid.uuid4().hex[:8]}-{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:12]}"
    
    def generate_request_id(self) -> str:
        """Generate unique request ID"""
        self.request_id_counter += 1
        return f"req_{int(datetime.now().timestamp())}_{self.request_id_counter:06d}"
    
    def generate_correlation_id(self) -> str:
        """Generate correlation ID for related events"""
        return f"corr-{uuid.uuid4().hex[:16]}"
    
    def generate_pod_name(self, service: str, replica_index: int = None) -> str:
        """Generate realistic Kubernetes pod name"""
        if replica_index is None:
            replica_index = random.randint(0, 10)
        
        random_suffix = hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:5]
        return f"{service}-{replica_index}-{random_suffix}"
    
    def generate_container_id(self) -> str:
        """Generate realistic container ID"""
        return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:12]
    
    def generate_node_name(self, node_type: str) -> str:
        """Generate realistic Kubernetes node name"""
        az = random.choice(['a', 'b', 'c'])
        instance_id = f"i-{uuid.uuid4().hex[:17]}"
        return f"ip-{self.generate_ip_address().replace('.', '-')}.{az}.compute.internal"
    
    def generate_image_name(self, service: str, tag: str = None) -> str:
        """Generate Docker image name"""
        registry = "012345678910.dkr.ecr.us-east-1.amazonaws.com"
        if tag is None:
            major = random.randint(1, 5)
            minor = random.randint(0, 20)
            patch = random.randint(0, 50)
            tag = f"v{major}.{minor}.{patch}"
        
        return f"{registry}/company/{service}:{tag}"
    
    def generate_error_message(self, error_type: str) -> str:
        """Generate realistic error messages"""
        messages = {
            'ConnectionError': [
                f"Failed to establish connection to database at {self.generate_ip_address()}:5432",
                f"Connection refused by {self.generate_ip_address()}:6379",
                f"Unable to connect to host {self.fake.domain_name()}",
                "Connection timeout after 30 seconds",
                "Max retries exceeded with url"
            ],
            'TimeoutError': [
                f"Request timeout after {random.randint(30, 120)} seconds",
                f"Database query timeout: exceeded {random.randint(5, 30)}s limit",
                "Read timeout on socket",
                "Connection timeout in pool"
            ],
            'MemoryError': [
                f"Cannot allocate {random.randint(100, 500)}MB of memory",
                "Out of memory: Failed to allocate native memory",
                "Java heap space exceeded",
                f"Memory limit of {random.randint(512, 2048)}Mi exceeded"
            ],
            'ValueError': [
                f"Invalid value for parameter '{random.choice(['user_id', 'order_id', 'product_id'])}': {random.choice(['null', 'empty', 'invalid format'])}",
                "Expected integer, got string",
                "Value out of range"
            ],
            'KeyError': [
                f"Key '{random.choice(['user_id', 'session_id', 'auth_token'])}' not found",
                "Missing required field in request",
                "Dictionary key does not exist"
            ],
            'DatabaseConnectionError': [
                "FATAL: remaining connection slots reserved for replication",
                "FATAL: too many connections for role",
                f"could not connect to server: Connection refused (host={self.generate_ip_address()})",
                "connection pool exhausted"
            ],
            'PoolTimeoutError': [
                f"QueuePool limit of {random.randint(10, 50)} overflow {random.randint(5, 20)} reached",
                "Connection pool timeout: unable to acquire connection within timeout period",
                "All connections in use"
            ]
        }
        
        if error_type in messages:
            return random.choice(messages[error_type])
        else:
            return f"{error_type}: An unexpected error occurred"
    
    def generate_http_status_code(self, success_rate: float = 0.95) -> int:
        """Generate HTTP status codes with realistic distribution"""
        if random.random() < success_rate:
            return random.choices(
                [200, 201, 204, 304],
                weights=[0.85, 0.08, 0.05, 0.02]
            )[0]
        else:
            return random.choices(
                [400, 401, 403, 404, 429, 500, 502, 503, 504],
                weights=[0.15, 0.10, 0.08, 0.25, 0.07, 0.15, 0.08, 0.07, 0.05]
            )[0]
    
    def generate_latency_ms(self, percentile: int = 50) -> float:
        """Generate realistic latency values"""
        if percentile <= 50:
            # P50: 20-100ms
            return random.uniform(20, 100)
        elif percentile <= 90:
            # P90: 100-300ms
            return random.uniform(100, 300)
        elif percentile <= 95:
            # P95: 300-800ms
            return random.uniform(300, 800)
        elif percentile <= 99:
            # P99: 800-2000ms
            return random.uniform(800, 2000)
        else:
            # P99.9: 2000-10000ms
            return random.uniform(2000, 10000)
    
    def generate_user_agent(self) -> str:
        """Generate realistic user agent strings"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        ]
        return random.choice(user_agents)
    
    def generate_sql_query(self, query_type: str = None) -> str:
        """Generate realistic SQL queries"""
        if query_type is None:
            query_type = random.choice(['SELECT', 'INSERT', 'UPDATE', 'DELETE'])
        
        tables = ['users', 'orders', 'products', 'payments', 'sessions']
        table = random.choice(tables)
        
        if query_type == 'SELECT':
            return f"SELECT * FROM {table} WHERE id = ${random.randint(1, 5)} LIMIT {random.randint(1, 100)}"
        elif query_type == 'INSERT':
            return f"INSERT INTO {table} (id, created_at, data) VALUES (${random.randint(1, 5)}, ${random.randint(1, 5)}, ${random.randint(1, 5)})"
        elif query_type == 'UPDATE':
            return f"UPDATE {table} SET status = ${random.randint(1, 5)} WHERE id = ${random.randint(1, 5)}"
        elif query_type == 'DELETE':
            return f"DELETE FROM {table} WHERE id = ${random.randint(1, 5)}"
    
    def generate_log_context(self) -> Dict[str, Any]:
        """Generate common log context"""
        return {
            'trace_id': self.generate_trace_id(),
            'span_id': uuid.uuid4().hex[:16],
            'request_id': self.generate_request_id(),
            'user_id': self.generate_user_id() if random.random() > 0.2 else None,
            'session_id': self.generate_session_id() if random.random() > 0.3 else None,
            'ip_address': self.generate_ip_address(),
            'user_agent': self.generate_user_agent() if random.random() > 0.4 else None
        }
    
    def generate_stack_trace(self, error_type: str, service: str) -> List[Dict[str, Any]]:
        """Generate realistic stack traces"""
        frameworks = {
            'python': ['flask', 'django', 'fastapi', 'sqlalchemy', 'celery'],
            'java': ['spring', 'hibernate', 'tomcat', 'netty'],
            'node': ['express', 'koa', 'sequelize', 'axios']
        }
        
        language = random.choice(['python', 'java', 'node'])
        framework = random.choice(frameworks[language])
        
        stack_depth = random.randint(5, 15)
        stack = []
        
        # Application frames
        for i in range(stack_depth // 3):
            if language == 'python':
                filename = f"/app/src/{service}/{random.choice(['handlers', 'services', 'models', 'utils'])}/{random.choice(['user', 'order', 'payment', 'product'])}.py"
                function = random.choice(['process_request', 'handle_user', 'create_order', 'validate_payment', 'fetch_product'])
            elif language == 'java':
                filename = f"com/company/{service}/{random.choice(['controller', 'service', 'repository'])}/{random.choice(['User', 'Order', 'Payment'])}.java"
                function = random.choice(['processRequest', 'handleUser', 'createOrder', 'validatePayment'])
            else:
                filename = f"/app/src/{service}/{random.choice(['routes', 'controllers', 'services'])}/{random.choice(['user', 'order', 'payment'])}.js"
                function = random.choice(['handleRequest', 'processUser', 'createOrder', 'validatePayment'])
            
            stack.append({
                'filename': filename,
                'function': function,
                'lineno': random.randint(10, 500),
                'context_line': f"    {random.choice(['return', 'await', 'const', 'if', 'throw'])} ...",
                'in_app': True
            })
        
        # Framework frames
        for i in range(stack_depth // 3):
            if language == 'python':
                filename = f"/usr/local/lib/python3.9/site-packages/{framework}/{random.choice(['app', 'routing', 'middleware', 'orm'])}.py"
                function = random.choice(['__call__', 'dispatch_request', 'handle', 'execute'])
            elif language == 'java':
                filename = f"org/{framework}/{random.choice(['web', 'servlet', 'core'])}/{random.choice(['Dispatcher', 'Handler', 'Filter'])}.java"
                function = random.choice(['doDispatch', 'handle', 'doFilter'])
            else:
                filename = f"/app/node_modules/{framework}/lib/{random.choice(['application', 'router', 'middleware'])}.js"
                function = random.choice(['handle', 'dispatch', 'next'])
            
            stack.append({
                'filename': filename,
                'function': function,
                'lineno': random.randint(10, 1000),
                'context_line': f"    {random.choice(['return', 'call', 'invoke'])} ...",
                'in_app': False
            })
        
        # System frames
        for i in range(stack_depth // 3):
            if language == 'python':
                filename = f"/usr/lib/python3.9/{random.choice(['threading', 'socket', 'ssl', 'urllib'])}.py"
                function = random.choice(['run', 'connect', 'send', 'recv'])
            elif language == 'java':
                filename = f"java/{random.choice(['util', 'io', 'net', 'sql'])}/{random.choice(['Thread', 'Socket', 'Connection'])}.java"
                function = random.choice(['run', 'connect', 'execute'])
            else:
                filename = f"internal/{random.choice(['http', 'stream', 'net'])}.js"
                function = random.choice(['onread', 'emit', 'write'])
            
            stack.append({
                'filename': filename,
                'function': function,
                'lineno': random.randint(10, 2000),
                'context_line': None,
                'in_app': False
            })
        
        return stack[::-1]  # Reverse to show deepest call first
    
    def generate_breadcrumbs(self, count: int = None) -> List[Dict[str, Any]]:
        """Generate Sentry-style breadcrumbs"""
        if count is None:
            count = random.randint(3, 15)
        
        breadcrumb_types = ['http', 'navigation', 'query', 'user', 'error']
        breadcrumbs = []
        
        current_time = datetime.now()
        
        for i in range(count):
            breadcrumb_time = current_time - timedelta(seconds=random.randint(1, 300))
            breadcrumb_type = random.choice(breadcrumb_types)
            
            breadcrumb = {
                'timestamp': breadcrumb_time.isoformat(),
                'type': breadcrumb_type,
                'level': random.choice(['info', 'warning', 'error']),
            }
            
            if breadcrumb_type == 'http':
                breadcrumb['data'] = {
                    'url': f"https://api.company.com{random.choice(['/api/v1/users', '/api/v1/orders', '/api/v1/products'])}",
                    'method': random.choice(['GET', 'POST', 'PUT', 'DELETE']),
                    'status_code': self.generate_http_status_code(),
                    'duration': self.generate_latency_ms()
                }
            elif breadcrumb_type == 'navigation':
                breadcrumb['data'] = {
                    'from': random.choice(['/home', '/products', '/cart', '/checkout']),
                    'to': random.choice(['/products', '/cart', '/checkout', '/orders'])
                }
            elif breadcrumb_type == 'query':
                breadcrumb['data'] = {
                    'query': self.generate_sql_query(),
                    'duration': random.uniform(10, 500)
                }
            elif breadcrumb_type == 'user':
                breadcrumb['data'] = {
                    'action': random.choice(['click', 'input', 'scroll', 'submit']),
                    'target': random.choice(['button', 'input', 'link', 'form'])
                }
            
            breadcrumbs.append(breadcrumb)
        
        return sorted(breadcrumbs, key=lambda x: x['timestamp'])

# Global instance
realistic_data = RealisticDataGenerator()
