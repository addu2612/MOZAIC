# Synthetic Log Generator for MOZAIC

Complete synthetic log generation system that produces hyper-realistic logs across Kubernetes, Sentry, CloudWatch, and Grafana.

## 🎯 Features

- **Hyper-Realistic Logs**: Logs that look identical to real production systems
- **Cross-Source Correlation**: Automatic correlation of incidents across all sources
- **Temporal Patterns**: Realistic time-of-day, weekly, and seasonal patterns
- **Incident Scenarios**: 12+ pre-configured incident types with cascading failures
- **Rich Context**: Full stack traces, breadcrumbs, metrics, and metadata
- **Configurable**: Extensive YAML configuration for customization

## 📁 Project Structure

```
synthetic-log-generator/
├── config/
│   ├── services_config.yaml       # Microservices architecture
│   ├── incident_patterns.yaml     # Incident scenario definitions
│   └── generation_config.yaml     # Generation parameters
├── generators/
│   ├── kubernetes_generator.py    # K8s logs, events, metrics
│   ├── sentry_generator.py        # Error tracking logs
│   ├── cloudwatch_generator.py    # AWS metrics and logs
│   └── grafana_generator.py       # Dashboard and panel data
├── utils/
│   ├── realistic_data.py          # Realistic data generation
│   ├── timestamp_utils.py         # Time pattern generation
│   └── correlation_engine.py      # Cross-source correlation
├── scenarios/
│   ├── incident_scenarios.py      # Incident generation logic
│   └── normal_operations.py       # Normal operation patterns
├── output/                        # Generated logs output directory
└── main.py                        # Main orchestrator script
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd synthetic-log-generator

# Install dependencies
pip install -r requirements.txt
```

### 2. Basic Usage

```bash
# Generate 1 day of logs with default settings
python main.py --days 1

# Generate specific incident types
python main.py --days 7 --incidents memory_leak,deployment_failure

# Generate high volume (10x normal traffic)
python main.py --days 1 --volume-multiplier 10

# Generate with custom date range
python main.py --start-date 2024-01-01 --end-date 2024-12-31
```

### 3. Advanced Usage

```bash
# Generate specific scenario
python main.py --scenario database_outage --duration-minutes 45

# Generate with cascading failures
python main.py --enable-cascading --cascade-probability 0.5

# Output in specific format
python main.py --output-format json --compress

# Generate only specific sources
python main.py --sources kubernetes,sentry --days 1
```

## 📊 Generated Log Examples

### Kubernetes Pod Log
```json
{
  "timestamp": "2024-11-15T14:32:15.123Z",
  "stream": "stdout",
  "log": "{\"timestamp\":\"2024-11-15T14:32:15.123456\",\"level\":\"ERROR\",\"message\":\"Database connection pool exhausted\",\"trace_id\":\"7f3a9b2c-1d4e-4f5a-9c8b-2e1d3c4f5a6b\",\"service_name\":\"user-service\"}",
  "kubernetes": {
    "pod_name": "user-service-3-abc12",
    "namespace_name": "production",
    "container_name": "user-service",
    "labels": {
      "app": "user-service",
      "version": "v1.8.3"
    }
  }
}
```

### Sentry Error Event
```json
{
  "event_id": "a1b2c3d4e5f6g7h8",
  "timestamp": "2024-11-15T14:32:15.456Z",
  "platform": "python",
  "level": "error",
  "exception": {
    "values": [{
      "type": "PoolTimeoutError",
      "value": "QueuePool limit of 20 overflow 10 reached",
      "stacktrace": {
        "frames": [...]
      }
    }]
  },
  "tags": {
    "environment": "production",
    "server_name": "user-service-3-abc12"
  },
  "breadcrumbs": [...]
}
```

### CloudWatch Metric
```json
{
  "Namespace": "AWS/RDS",
  "MetricName": "DatabaseConnections",
  "Timestamp": "2024-11-15T14:32:00Z",
  "Value": 100.0,
  "Unit": "Count",
  "Dimensions": [
    {
      "Name": "DBInstanceIdentifier",
      "Value": "production-postgres"
    }
  ]
}
```

## 🎬 Incident Scenarios

### Available Scenarios

1. **memory_leak** - Gradual memory exhaustion leading to OOMKilled
2. **deployment_failure** - Failed deployment with ImagePullBackOff and CrashLoopBackOff
3. **database_connection_pool_exhaustion** - Connection pool saturation
4. **network_partition** - Network connectivity loss
5. **cpu_throttling** - CPU resource exhaustion
6. **disk_space_exhaustion** - Disk filling up
7. **api_rate_limit_exceeded** - Rate limiting triggered
8. **cache_invalidation_storm** - Cache miss cascade
9. **message_queue_backlog** - Queue depth explosion
10. **certificate_expiration** - SSL/TLS certificate expiry
11. **dns_resolution_failure** - DNS lookup failures
12. **cascading_failure** - Multi-service failure propagation

### Scenario Example: Memory Leak

```
Timeline of a Memory Leak Incident (60 minutes):

T+0:    Grafana: JVM Heap Usage starts climbing (60% → 75%)
T+10:   CloudWatch: MemoryUtilization increases (65% → 80%)
T+20:   Sentry: First MemoryError warnings appear
T+30:   K8s: Warning event - HighMemoryUsage at 85%
T+40:   Grafana: Heap Usage critical (90%+)
T+45:   Sentry: Frequent OutOfMemoryError events
T+50:   K8s: Warning event - MemoryPressure at 95%
T+54:   Sentry: Fatal OutOfMemoryError
T+55:   K8s: OOMKilled event (exit code 137)
T+55.1: K8s: Pod restart initiated
T+56:   K8s: Container restarted successfully

Correlation ID: corr_a1b2c3d4e5f6g7h8
Affected Services: user-service
Root Cause: Memory leak in user session cache
```

## ⚙️ Configuration

### Services Configuration (services_config.yaml)

Define your microservices architecture:

```yaml
services:
  api-gateway:
    replicas: 3
    image: "company/api-gateway:v2.4.1"
    resources:
      requests:
        cpu: "500m"
        memory: "512Mi"
    endpoints:
      - "/api/v1/users"
      - "/api/v1/orders"
```

### Incident Patterns (incident_patterns.yaml)

Customize incident behavior:

```yaml
incidents:
  memory_leak:
    severity: "critical"
    duration_minutes: [30, 180]
    probability: 0.05
    kubernetes_patterns:
      - type: "OOMKilled"
        frequency: "increasing"
```

### Generation Configuration (generation_config.yaml)

Control generation parameters:

```yaml
generation:
  normal_logs_per_minute: 1000
  incident_logs_multiplier: 3.5
  incidents:
    total_count: 500
    cascade_probability: 0.3
```

## 📈 Realistic Patterns

### Traffic Patterns
- **Peak Hours**: 9 AM - 6 PM (3.5x traffic)
- **Off Hours**: 12 AM - 6 AM (0.2x traffic)
- **Weekend**: 60% of weekday traffic
- **Monday Spike**: 30% increase
- **Black Friday**: 3.5x traffic
- **Holiday Season**: 2.5x traffic

### Log Distribution
- **INFO**: 70%
- **WARNING**: 20%
- **ERROR**: 8%
- **CRITICAL**: 2%

### HTTP Status Codes
- **2xx**: 85-95%
- **4xx**: 5-10%
- **5xx**: 0-5%

## 🔍 Output Structure

```
output/
├── kubernetes/
│   ├── pod_logs_2024-01-01.jsonl.gz
│   ├── events_2024-01-01.jsonl.gz
│   └── metrics_2024-01-01.jsonl.gz
├── sentry/
│   ├── errors_2024-01-01.jsonl.gz
│   └── performance_2024-01-01.jsonl.gz
├── cloudwatch/
│   ├── logs_2024-01-01.jsonl.gz
│   └── metrics_2024-01-01.jsonl.gz
├── grafana/
│   └── panels_2024-01-01.jsonl.gz
└── correlation/
    └── incidents_2024-01-01.json
```

## 🧪 Validation

### Verify Log Quality

```bash
# Check log counts
python validate.py --check-counts

# Verify temporal correlation
python validate.py --check-correlation

# Analyze incident patterns
python validate.py --analyze-incidents

# Generate quality report
python validate.py --full-report
```

### Expected Metrics
- **Silhouette Score**: > 0.85 for incident clusters
- **Temporal Correlation**: 80-95% of related events within 5min window
- **Cross-Source Coverage**: All incidents span 3+ sources
- **Realistic Timestamps**: < 1% timestamp anomalies

## 📚 Advanced Features

### Custom Incident Generation

```python
from generators import KubernetesLogGenerator
from utils.correlation_engine import CorrelationEngine

# Create custom incident
engine = CorrelationEngine()
incident = engine.create_memory_leak_incident(
    start_time=datetime.now(),
    service='user-service',
    pod_name='user-service-3-abc12',
    duration_minutes=60
)

# Generate logs
k8s_gen = KubernetesLogGenerator(services_config)
logs = k8s_gen.generate_oom_killed_sequence(
    incident.start_time,
    incident.affected_services[0],
    'user-service-3-abc12'
)
```

### Cascading Failure Simulation

```python
# Enable cascading failures
incident = engine.create_incident(
    incident_type='database_outage',
    start_time=datetime.now(),
    duration_minutes=30,
    severity='critical',
    affected_services=['postgres-primary']
)

# Will automatically cascade to dependent services
if engine.should_cascade(probability=0.6):
    cascade_targets = engine.get_cascade_targets('postgres-primary', all_services)
    # Generate failures in cascade_targets...
```

## 🎯 Use Cases

### ML Pipeline Development
```bash
# Generate diverse training data
python main.py --days 90 --all-incident-types

# Generate labeled anomalies
python main.py --days 30 --label-anomalies

# Generate test set with rare incidents
python main.py --days 7 --rare-incidents-only
```

### Correlation Testing
```bash
# Test temporal correlation (tight windows)
python main.py --correlation-window 60 --days 1

# Test semantic correlation
python main.py --enable-semantic-variation --days 1

# Test cascading detection
python main.py --max-cascade-depth 5 --days 1
```

### Performance Testing
```bash
# Generate high-volume logs
python main.py --volume-multiplier 100 --duration-hours 1

# Generate burst patterns
python main.py --enable-bursts --burst-intensity 50 --days 1
```

## 🐛 Troubleshooting

### Common Issues

**Issue**: Generated timestamps are not realistic
```bash
# Solution: Check timezone configuration
python main.py --timezone UTC --verify-timestamps
```

**Issue**: Incident correlation is weak
```bash
# Solution: Reduce correlation window and increase correlation strength
python main.py --correlation-window 180 --min-correlation 0.8
```

**Issue**: Too many/few incidents
```bash
# Solution: Adjust incident probability
# Edit config/incident_patterns.yaml
# Set probability values between 0.01 and 0.20
```

## 📖 Examples

See `examples/` directory for:
- `basic_generation.py` - Simple log generation
- `custom_incident.py` - Custom incident creation
- `batch_generation.py` - Large-scale batch generation
- `realtime_streaming.py` - Streaming log generation

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional incident scenarios
- More realistic error messages
- Enhanced metric patterns
- Additional data sources

## 📊 Few-Shot Clustering Notebooks

Complete Jupyter notebook pipeline for clustering and analyzing generated Grafana logs using few-shot learning!

### 🎯 What's Included

Located in the `notebooks/` directory:

- **5 Comprehensive Notebooks**: Data exploration → Feature engineering → Few-shot clustering → Evaluation → Practical usage
- **Complete Documentation**: README, Quick Start Guide, and Index
- **Automated Pipeline**: Run the complete clustering pipeline with one command
- **Production Ready**: Handles 140K+ logs, includes FAISS similarity search, HDBSCAN clustering, and Sentence-BERT embeddings

### 🚀 Quick Start with Notebooks

```bash
# Navigate to notebooks directory
cd notebooks/

# Install dependencies
pip install -r requirements_notebooks.txt

# Run complete clustering pipeline
python run_clustering_pipeline.py

# Or use Jupyter
jupyter notebook  # Open and run 1 → 2 → 3 → 4 → 5
```

### 📚 Learn More

- **Quick Start**: `notebooks/QUICKSTART.md` - Get started in 5 minutes
- **Complete Guide**: `notebooks/README.md` - Comprehensive documentation
- **Overview**: `notebooks/INDEX.md` - Navigate all notebooks
- **Delivery**: `notebooks/DELIVERY_SUMMARY.md` - What was delivered and why

### 🎯 Key Features

- ✅ Few-shot learning with 7 domain categories
- ✅ Sentence-BERT embeddings for semantic understanding
- ✅ HDBSCAN density-based clustering
- ✅ FAISS for fast similarity search (<100ms queries)
- ✅ Comprehensive evaluation metrics (Silhouette > 0.85 achievable)
- ✅ Anomaly detection and alert generation
- ✅ Production-ready pipeline (~30 min for 140K logs)

### 📊 Expected Results

```json
{
  "n_clusters": "10-20 semantic groups",
  "silhouette_score": "0.6-0.8 (good to excellent)",
  "processing_time": "~30 minutes for 140K logs",
  "clustering_rate": "85%+ logs successfully clustered"
}
```

---

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

Built for the MOZAIC project - Multi-Source Orchestrated Zephyr Anomaly Intelligent Coordinator

---

**Need Help?** 
- **Log Generation**: Check documentation in this README
- **Clustering Analysis**: See `notebooks/` directory
- **Configuration**: Review configuration guides in `config/`
