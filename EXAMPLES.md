# Usage Examples and Configuration Recipes

This document provides practical examples and configuration recipes for different use scenarios.

## Basic Usage Examples

### 1. Command Line Usage

**Traditional Python Execution:**
```bash
# Basic usage with default settings
python nvme_exporter.py

# Custom port and update interval
python nvme_exporter.py -p 8080 -u 30

# Enable simulation mode for testing
python nvme_exporter.py -s 1 -p 9900 -u 10

# With sudo for device access (if needed)
sudo python nvme_exporter.py -p 9900 -u 10
```

**Using Command Line Arguments:**
```bash
# Show help
python nvme_exporter.py --help

# Specific configuration
python nvme_exporter.py \
  --port 9900 \
  --update 30 \
  --simulation 0
```

### 2. Environment Variable Configuration

**Basic Environment Setup:**
```bash
# Set environment variables
export PORT=9900
export UPDATE_PERIOD=30
export SIMULATION=0
export DEBUG=1

# Run with environment variables
python nvme_exporter.py
```

**Using .env File:**
```bash
# Create .env file
cat > .env << EOF
PORT=9900
UPDATE_PERIOD=30
SIMULATION=0
DEBUG=0
EOF

# Load and run (requires python-dotenv)
python -c "
from dotenv import load_dotenv
load_dotenv()
import nvme_exporter
nvme_exporter.main()
"
```

## Docker Usage Examples

### 1. Simple Docker Runs

**Production Monitoring:**
```bash
# Basic production setup
docker run -d \
  --name nvme-exporter \
  --privileged \
  -v /dev:/dev \
  -p 9900:9900 \
  ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest

# With restart policy
docker run -d \
  --name nvme-exporter \
  --restart unless-stopped \
  --privileged \
  -v /dev:/dev \
  -p 9900:9900 \
  ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest
```

**Development and Testing:**
```bash
# Development with debug output
docker run -d \
  --name nvme-dev \
  --privileged \
  -v /dev:/dev \
  -p 9900:9900 \
  -e DEBUG=1 \
  -e UPDATE_PERIOD=5 \
  ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest

# Simulation mode (no hardware required)
docker run -d \
  --name nvme-sim \
  -p 9900:9900 \
  -e SIMULATION=1 \
  -e DEBUG=1 \
  ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest
```

### 2. Advanced Docker Configurations

**Resource Limited:**
```bash
# Limit CPU and memory usage
docker run -d \
  --name nvme-limited \
  --privileged \
  -v /dev:/dev \
  -p 9900:9900 \
  --cpus="0.5" \
  --memory="128m" \
  --memory-swap="256m" \
  -e UPDATE_PERIOD=60 \
  ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest
```

**Custom Network:**
```bash
# Create custom network
docker network create nvme-monitoring

# Run with custom network
docker run -d \
  --name nvme-exporter \
  --network nvme-monitoring \
  --privileged \
  -v /dev:/dev \
  -p 9900:9900 \
  ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest
```

**With Logging Configuration:**
```bash
# Custom logging driver
docker run -d \
  --name nvme-exporter \
  --privileged \
  -v /dev:/dev \
  -p 9900:9900 \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest
```

### 3. Multi-Container Setups

**Multiple Instances:**
```bash
# Run multiple instances on different ports
for i in {1..3}; do
  docker run -d \
    --name nvme-exporter-$i \
    --privileged \
    -v /dev:/dev \
    -p $((9900+i-1)):9900 \
    -e UPDATE_PERIOD=$((i*10)) \
    ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest
done
```

**Load Balancer Setup:**
```bash
# Create multiple backend instances
for i in {1..3}; do
  docker run -d \
    --name nvme-backend-$i \
    --privileged \
    -v /dev:/dev \
    -e UPDATE_PERIOD=30 \
    ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest
done

# Simple nginx load balancer
docker run -d \
  --name nvme-lb \
  -p 9900:80 \
  -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro \
  nginx:alpine
```

## Docker Compose Examples

### 1. Basic Docker Compose

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  nvme-exporter:
    image: ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest
    container_name: nvme-exporter
    privileged: true
    volumes:
      - /dev:/dev
    ports:
      - "9900:9900"
    environment:
      - UPDATE_PERIOD=30
    restart: unless-stopped
```

**Usage:**
```bash
# Start service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop service
docker-compose down
```

### 2. Development Docker Compose

**docker-compose.dev.yml:**
```yaml
version: '3.8'

services:
  nvme-exporter:
    build: .
    container_name: nvme-exporter-dev
    privileged: true
    volumes:
      - /dev:/dev
      - .:/app  # Mount source code for development
    ports:
      - "9900:9900"
    environment:
      - DEBUG=1
      - UPDATE_PERIOD=10
    restart: "no"  # Don't restart in development
```

**Usage:**
```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up --build

# Rebuild after changes
docker-compose -f docker-compose.dev.yml up --build --force-recreate
```

### 3. Complete Monitoring Stack

**docker-compose.monitoring.yml:**
```yaml
version: '3.8'

services:
  nvme-exporter:
    image: ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest
    container_name: nvme-exporter
    privileged: true
    volumes:
      - /dev:/dev
    ports:
      - "9900:9900"
    environment:
      - UPDATE_PERIOD=30
    networks:
      - monitoring
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    networks:
      - monitoring
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    networks:
      - monitoring
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:

networks:
  monitoring:
    driver: bridge
```

**prometheus.yml:**
```yaml
global:
  scrape_interval: 30s

scrape_configs:
  - job_name: 'nvme-exporter'
    static_configs:
      - targets: ['nvme-exporter:9900']
    scrape_interval: 30s
    metrics_path: '/metrics'
```

## Configuration Recipes

### 1. Performance-Focused Configurations

**High-Frequency Monitoring:**
```bash
# Monitor every 5 seconds
docker run -d \
  --name nvme-high-freq \
  --privileged \
  -v /dev:/dev \
  -p 9900:9900 \
  -e UPDATE_PERIOD=5 \
  --cpus="1.0" \
  --memory="256m" \
  ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest
```

**Low-Impact Monitoring:**
```bash
# Monitor every 5 minutes with minimal resources
docker run -d \
  --name nvme-low-impact \
  --privileged \
  -v /dev:/dev \
  -p 9900:9900 \
  -e UPDATE_PERIOD=300 \
  --cpus="0.1" \
  --memory="64m" \
  ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest
```

### 2. Security-Focused Configurations

**Read-Only Root Filesystem:**
```bash
docker run -d \
  --name nvme-readonly \
  --privileged \
  --read-only \
  --tmpfs /tmp \
  -v /dev:/dev:ro \
  -p 9900:9900 \
  ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest
```

**Specific Device Access:**
```bash
# Mount only specific NVMe devices
docker run -d \
  --name nvme-specific \
  --device=/dev/nvme0 \
  --device=/dev/nvme1 \
  --cap-add=SYS_ADMIN \
  -p 9900:9900 \
  ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest
```

### 3. Testing and Development Configurations

**Simulation Mode Development:**
```yaml
# docker-compose.simulation.yml
version: '3.8'

services:
  nvme-sim-1:
    image: ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest
    ports:
      - "9901:9900"
    environment:
      - SIMULATION=1
      - DEBUG=1
      - UPDATE_PERIOD=10

  nvme-sim-2:
    image: ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest
    ports:
      - "9902:9900"
    environment:
      - SIMULATION=1
      - DEBUG=0
      - UPDATE_PERIOD=30

  nvme-sim-3:
    image: ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest
    ports:
      - "9903:9900"
    environment:
      - SIMULATION=1
      - DEBUG=0
      - UPDATE_PERIOD=60
```

**Automated Testing:**
```bash
#!/bin/bash
# test_runner.sh

echo "Starting test instances..."

# Start multiple test instances
docker run -d --name nvme-test-1 -p 9901:9900 -e SIMULATION=1 ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest
docker run -d --name nvme-test-2 -p 9902:9900 -e SIMULATION=1 ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest
docker run -d --name nvme-test-3 -p 9903:9900 -e SIMULATION=1 ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest

# Wait for startup
sleep 10

# Test each instance
for port in 9901 9902 9903; do
  echo "Testing port $port..."
  curl -s http://localhost:$port/metrics | grep -c nvme_smart || echo "FAILED"
done

# Cleanup
docker rm -f nvme-test-1 nvme-test-2 nvme-test-3
```

## Integration Examples

### 1. Prometheus Integration

**Alert Rules (nvme.rules):**
```yaml
groups:
- name: nvme_alerts
  rules:
  - alert: NVMeHighTemperature
    expr: nvme_smart_log_temperature - 273 > 70
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "NVMe {{ $labels.device }} temperature high"
      description: "Temperature: {{ $value }}°C"

  - alert: NVMeHighWearLevel
    expr: nvme_smart_log_percent_used > 80
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "NVMe {{ $labels.device }} wear level high"
      description: "Wear level: {{ $value }}%"
```

**Grafana Dashboard Query Examples:**
```promql
# Temperature in Celsius
nvme_smart_log_temperature - 273

# Wear level percentage
nvme_smart_log_percent_used

# Data written in GB
nvme_smart_log_data_units_written * 512 / 1024 / 1024 / 1024

# Power on time in days
nvme_smart_log_power_on_hours / 24
```

### 2. Kubernetes Integration

**Helm Values (values.yaml):**
```yaml
# values.yaml for nvme-exporter helm chart
image:
  repository: ghcr.io/B-IT-Projects-GmbH/nvme_exporter
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 9900

resources:
  limits:
    cpu: 100m
    memory: 128Mi
  requests:
    cpu: 50m
    memory: 64Mi

nodeSelector:
  kubernetes.io/os: linux

tolerations:
  - operator: Exists
    effect: NoSchedule

updatePeriod: 30
debug: false
```

**Kustomization Example:**
```yaml
# kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - deployment.yaml
  - service.yaml
  - servicemonitor.yaml

configMapGenerator:
  - name: nvme-exporter-config
    literals:
      - UPDATE_PERIOD=30
      - DEBUG=0

images:
  - name: nvme-exporter
    newName: ghcr.io/B-IT-Projects-GmbH/nvme_exporter
    newTag: v1.0
```

### 3. CI/CD Integration

**GitHub Actions Testing:**
```yaml
# .github/workflows/test.yml
name: Test NVMe Exporter

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: docker build -t nvme-exporter:test .
    
    - name: Test simulation mode
      run: |
        docker run -d --name test-container -p 9900:9900 -e SIMULATION=1 nvme-exporter:test
        sleep 10
        curl -f http://localhost:9900/metrics | grep nvme_smart
        docker rm -f test-container
```

**Jenkins Pipeline Example:**
```groovy
pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                script {
                    docker.build("nvme-exporter:${env.BUILD_ID}")
                }
            }
        }
        
        stage('Test') {
            steps {
                script {
                    def container = docker.image("nvme-exporter:${env.BUILD_ID}")
                        .run("-d -p 9900:9900 -e SIMULATION=1")
                    
                    sleep 10
                    
                    sh "curl -f http://localhost:9900/metrics | grep nvme_smart"
                    
                    container.stop()
                }
            }
        }
    }
}
```

## Custom Scenarios

### 1. Multi-Environment Setup

**Production Environment:**
```bash
# Production with high availability
docker run -d \
  --name nvme-prod \
  --restart always \
  --privileged \
  -v /dev:/dev:ro \
  -p 9900:9900 \
  -e UPDATE_PERIOD=60 \
  -e DEBUG=0 \
  --log-driver syslog \
  --log-opt syslog-address=udp://log-server:514 \
  ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest
```

**Staging Environment:**
```bash
# Staging with debug enabled
docker run -d \
  --name nvme-staging \
  --privileged \
  -v /dev:/dev \
  -p 9900:9900 \
  -e UPDATE_PERIOD=30 \
  -e DEBUG=1 \
  --log-driver json-file \
  --log-opt max-size=10m \
  ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest
```

**Development Environment:**
```bash
# Development with live reload
docker run -d \
  --name nvme-dev \
  --privileged \
  -v /dev:/dev \
  -v $(pwd):/app \
  -p 9900:9900 \
  -e UPDATE_PERIOD=10 \
  -e DEBUG=1 \
  --entrypoint "python" \
  ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest \
  nvme_exporter.py
```

### 2. Backup and Monitoring

**Metrics Export for Backup:**
```bash
#!/bin/bash
# backup_metrics.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/nvme-metrics"

mkdir -p $BACKUP_DIR

# Export current metrics
curl -s http://localhost:9900/metrics > $BACKUP_DIR/metrics_$TIMESTAMP.txt

# Keep only last 30 days
find $BACKUP_DIR -name "metrics_*.txt" -mtime +30 -delete

echo "Metrics backed up to $BACKUP_DIR/metrics_$TIMESTAMP.txt"
```

**Health Check Script:**
```bash
#!/bin/bash
# health_check.sh

ENDPOINT="http://localhost:9900/metrics"
EXPECTED_METRICS="nvme_smart_log_temperature"

if curl -sf $ENDPOINT | grep -q $EXPECTED_METRICS; then
    echo "✅ NVMe Exporter is healthy"
    exit 0
else
    echo "❌ NVMe Exporter is unhealthy"
    # Send alert or restart service
    docker restart nvme-exporter
    exit 1
fi
```

This examples document provides a comprehensive collection of real-world usage scenarios and configuration patterns for nvme_exporter across different environments and use cases. 