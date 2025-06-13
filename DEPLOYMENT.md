# Deployment Guide

This guide covers detailed deployment scenarios, Docker architecture, and production setup for nvme_exporter.

## Docker Architecture

The Docker setup provides a production-ready containerized version of the nvme_exporter with:

1. **Multi-stage Build**: Optimized image size with separate build and runtime stages
2. **Multi-platform Support**: Builds for both `linux/amd64` and `linux/arm64`
3. **Automated CI/CD**: GitHub Actions automatically builds and publishes images
4. **Security**: Non-root user execution with minimal runtime dependencies

### Available Tags

- `latest` - Latest stable build from main branch
- `v1.0`, `v1.1`, etc. - Specific version releases
- `main` - Latest development build

### CI/CD Pipeline

The project includes a GitHub Actions workflow that automatically:

- **Builds** the Docker image on every push to main/master
- **Creates multi-platform images** for AMD64 and ARM64
- **Publishes** to GitHub Container Registry (`ghcr.io`)
- **Tags** images appropriately:
  - `latest` for main branch builds
  - Version tags for releases (e.g., `v1.0`, `v1.1`)
  - Branch names for development builds
- **Generates** build attestations for security

## Deployment Scenarios

### 1. Production Deployment

**Basic Production Setup:**
```bash
# Clone the repository
git clone https://github.com/B-IT-Projects-GmbH/nvme_exporter.git
cd nvme_exporter

# Start in production mode
docker-compose up -d

# Verify it's working
curl http://localhost:9900/metrics | grep nvme_smart

# View clean logs
docker-compose logs --tail=50

# Stop
docker-compose down
```

**Production with Custom Configuration:**
```bash
# Create custom docker-compose override
cat > docker-compose.override.yml << EOF
version: '3.8'
services:
  nvme-exporter:
    environment:
      - UPDATE_PERIOD=30
      - PORT=8080
    ports:
      - "8080:8080"
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
EOF

# Deploy with custom settings
docker-compose up -d
```

### 2. Development/Debug Deployment

**Debug Mode with Verbose Logging:**
```yaml
# Edit docker-compose.yml and uncomment:
environment:
  - DEBUG=1  # Enable verbose logging

# Then start with debug output
docker-compose up
```

**Manual Debug Container:**
```bash
# Run with full debug output
docker run -d \
  --name nvme-debug \
  --privileged \
  -v /dev:/dev \
  -p 9900:9900 \
  -e DEBUG=1 \
  -e UPDATE_PERIOD=5 \
  ghcr.io/b-it-projects-gmbh/nvme_exporter:latest

# Follow logs in real-time
docker logs nvme-debug -f
```

### 3. Testing with Simulation

**Quick Simulation Test:**
```bash
# Test without real NVMe devices
docker run -d \
  --name nvme-test \
  -p 9900:9900 \
  -e SIMULATION=1 \
  -e DEBUG=1 \
  ghcr.io/b-it-projects-gmbh/nvme_exporter:latest

# Check simulated metrics
curl http://localhost:9900/metrics | grep nvme_smart_log_temperature
```

**Multi-Instance Simulation:**
```bash
# Run multiple instances for load testing
for i in {1..3}; do
  docker run -d \
    --name nvme-sim-$i \
    -p $((9900+i)):9900 \
    -e SIMULATION=1 \
    -e UPDATE_PERIOD=10 \
    ghcr.io/b-it-projects-gmbh/nvme_exporter:latest
done

# Test all instances
for i in {1..3}; do
  echo "Instance $i:"
  curl -s http://localhost:$((9900+i))/metrics | grep -c nvme_smart
done
```

### 4. Custom Configuration Examples

**High-Frequency Monitoring:**
```bash
# Monitor every 5 seconds with custom port
docker run -d \
  --name nvme-hf \
  --privileged \
  -v /dev:/dev \
  -p 8080:8080 \
  -e PORT=8080 \
  -e UPDATE_PERIOD=5 \
  ghcr.io/b-it-projects-gmbh/nvme_exporter:latest
```

**Resource-Constrained Environment:**
```bash
# Limit CPU and memory usage
docker run -d \
  --name nvme-limited \
  --privileged \
  -v /dev:/dev \
  -p 9900:9900 \
  --cpus="0.5" \
  --memory="128m" \
  -e UPDATE_PERIOD=60 \
  ghcr.io/b-it-projects-gmbh/nvme_exporter:latest
```

## Advanced Deployment

### 1. Docker Compose Production Setup

**Full docker-compose.production.yml:**
```yaml
version: '3.8'

services:
  nvme-exporter:
    image: ghcr.io/b-it-projects-gmbh/nvme_exporter:latest
    container_name: nvme-exporter-prod
    privileged: true
    volumes:
      - /dev:/dev:ro
    ports:
      - "9900:9900"
    environment:
      - UPDATE_PERIOD=30
      - DEBUG=0
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9900/metrics"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "5"
    networks:
      - monitoring

  # Optional: Add Prometheus for scraping
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

volumes:
  prometheus_data:

networks:
  monitoring:
    driver: bridge
```

**Corresponding prometheus.yml:**
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

### 2. Kubernetes Deployment

**DaemonSet for Node-Level Monitoring:**
```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: nvme-exporter
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: nvme-exporter
  template:
    metadata:
      labels:
        app: nvme-exporter
    spec:
      hostNetwork: true
      hostPID: true
      containers:
      - name: nvme-exporter
        image: ghcr.io/b-it-projects-gmbh/nvme_exporter:latest
        ports:
        - containerPort: 9900
          hostPort: 9900
        env:
        - name: UPDATE_PERIOD
          value: "30"
        volumeMounts:
        - name: dev
          mountPath: /dev
          readOnly: true
        securityContext:
          privileged: true
        resources:
          limits:
            memory: 128Mi
            cpu: 100m
          requests:
            memory: 64Mi
            cpu: 50m
      volumes:
      - name: dev
        hostPath:
          path: /dev
      tolerations:
      - operator: Exists
        effect: NoSchedule
```

**Service and ServiceMonitor:**
```yaml
---
apiVersion: v1
kind: Service
metadata:
  name: nvme-exporter
  namespace: monitoring
  labels:
    app: nvme-exporter
spec:
  ports:
  - port: 9900
    name: metrics
  selector:
    app: nvme-exporter
  clusterIP: None

---
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: nvme-exporter
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: nvme-exporter
  endpoints:
  - port: metrics
    path: /metrics
    interval: 30s
```

### 3. Systemd Service (Traditional)

**nvme-exporter.service:**
```ini
[Unit]
Description=NVMe Prometheus Exporter
After=docker.service
Requires=docker.service

[Service]
Type=simple
Restart=always
RestartSec=5
ExecStartPre=-/usr/bin/docker stop nvme-exporter
ExecStartPre=-/usr/bin/docker rm nvme-exporter
ExecStart=/usr/bin/docker run \
  --name nvme-exporter \
  --privileged \
  -v /dev:/dev \
  -p 9900:9900 \
  -e UPDATE_PERIOD=30 \
  ghcr.io/b-it-projects-gmbh/nvme_exporter:latest
ExecStop=/usr/bin/docker stop nvme-exporter
TimeoutStartSec=0
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
```

**Install and Enable:**
```bash
# Copy service file
sudo cp nvme-exporter.service /etc/systemd/system/

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable nvme-exporter.service
sudo systemctl start nvme-exporter.service

# Check status
sudo systemctl status nvme-exporter.service
```

## Security Best Practices

### 1. Network Security

**Firewall Configuration:**
```bash
# Allow only specific IPs to access metrics
sudo ufw allow from 192.168.1.0/24 to any port 9900
sudo ufw deny 9900
```

**Reverse Proxy with Authentication:**
```nginx
# /etc/nginx/sites-available/nvme-exporter
server {
    listen 80;
    server_name nvme-metrics.example.com;
    
    location /metrics {
        auth_basic "NVMe Metrics";
        auth_basic_user_file /etc/nginx/.htpasswd;
        proxy_pass http://localhost:9900/metrics;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. Container Security

**Run with Specific Capabilities:**
```bash
# Instead of --privileged, use specific capabilities
docker run -d \
  --name nvme-exporter \
  --cap-add=SYS_ADMIN \
  --device=/dev/nvme0 \
  --device=/dev/nvme1 \
  -p 9900:9900 \
  ghcr.io/b-it-projects-gmbh/nvme_exporter:latest
```

**Read-Only Root Filesystem:**
```bash
docker run -d \
  --name nvme-exporter \
  --privileged \
  --read-only \
  --tmpfs /tmp \
  -v /dev:/dev:ro \
  -p 9900:9900 \
  ghcr.io/b-it-projects-gmbh/nvme_exporter:latest
```

## Monitoring and Alerting

### Sample Prometheus Rules

**nvme-exporter.rules.yml:**
```yaml
groups:
- name: nvme_exporter
  rules:
  - alert: NVMeHighTemperature
    expr: nvme_smart_log_temperature - 273 > 70
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "NVMe device {{ $labels.device }} high temperature"
      description: "Temperature is {{ $value }}°C"

  - alert: NVMeHighWearLevel
    expr: nvme_smart_log_percent_used > 80
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "NVMe device {{ $labels.device }} high wear level"
      description: "Wear level is {{ $value }}%"

  - alert: NVMeMediaErrors
    expr: increase(nvme_smart_log_media_errors[1h]) > 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "NVMe device {{ $labels.device }} media errors detected"
      description: "{{ $value }} media errors in the last hour"
```

This deployment guide provides comprehensive coverage of different deployment scenarios from simple Docker runs to complex Kubernetes deployments, along with security considerations and monitoring setup. 