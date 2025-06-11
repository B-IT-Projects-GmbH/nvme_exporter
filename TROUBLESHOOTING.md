# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with nvme_exporter.

## Quick Diagnostics

### Health Check Commands

```bash
# Check if container is running
docker ps | grep nvme

# View recent logs
docker logs nvme-exporter --tail=20

# Test metrics endpoint
curl -s http://localhost:9900/metrics | head -10

# Enable debug mode for detailed output
docker run -e DEBUG=1 -e SIMULATION=1 -p 9900:9900 ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest
```

### Container Status Checks

```bash
# Check container health
docker inspect nvme-exporter | grep -A 5 "Health"

# View container resource usage
docker stats nvme-exporter --no-stream

# Check container logs with timestamps
docker logs nvme-exporter -t --tail=50
```

## Common Issues

### 1. Permission and Access Issues

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **Permission Denied** | `docker: permission denied` | Add user to docker group: `sudo usermod -aG docker $USER` |
| **Port in Use** | `bind: address already in use` | Use different port: `-p 9901:9900` |
| **No NVMe Devices** | `Warning: No NVMe devices found` | Use simulation mode: `-e SIMULATION=1` |
| **Container Exits** | Container stops immediately | Check logs: `docker logs nvme-exporter` |
| **No Metrics** | Empty or error response | Enable debug: `-e DEBUG=1` |

**Detailed Permission Troubleshooting:**
```bash
# Check if user is in docker group
groups $USER

# If not, add user to docker group
sudo usermod -aG docker $USER

# Log out and back in, or restart shell
newgrp docker

# Test docker access
docker run hello-world
```

### 2. Device Access Issues

**Symptoms:**
- Container starts but shows "No NVMe devices found"
- SMART data returns empty or error responses
- nvme-cli commands fail inside container

**Debug Commands:**
```bash
# Test NVMe access inside container
docker exec nvme-exporter nvme list

# Check device permissions
docker exec nvme-exporter ls -la /dev/nvme*

# Test SMART data manually
docker exec nvme-exporter nvme smart-log /dev/nvme0 -o json

# Check if devices are visible from host
ls -la /dev/nvme*
```

**Solutions:**
```bash
# Ensure privileged mode
docker run --privileged -v /dev:/dev -p 9900:9900 [image]

# Alternative: Mount specific devices only
docker run -v /dev:/dev --device=/dev/nvme0 --device=/dev/nvme1 -p 9900:9900 [image]

# Check if nvme-cli works on host
sudo nvme list
sudo nvme smart-log /dev/nvme0 -o json
```

### 3. Network and Port Issues

**Port Already in Use:**
```bash
# Find what's using the port
sudo netstat -tulpn | grep 9900
# or
sudo lsof -i :9900

# Use different port
docker run -p 9901:9900 [other-options] [image]

# Or stop conflicting service
sudo systemctl stop [service-name]
```

**Firewall Issues:**
```bash
# Check if firewall is blocking
sudo ufw status
sudo iptables -L

# Allow port through firewall
sudo ufw allow 9900
```

### 4. Container Runtime Issues

**Container Keeps Restarting:**
```bash
# Check restart count and exit codes
docker ps -a

# View detailed container inspect
docker inspect nvme-exporter | grep -A 10 "State"

# Follow logs in real-time
docker logs nvme-exporter -f

# Check system resources
free -h
df -h
```

**Memory or CPU Issues:**
```bash
# Check resource limits
docker stats nvme-exporter

# Set explicit limits
docker run --memory="256m" --cpus="0.5" [other-options] [image]
```

## Debug Commands

### Container Debugging

```bash
# Start container with debug shell
docker run -it --privileged -v /dev:/dev --entrypoint /bin/sh \
  ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest

# Execute commands inside running container
docker exec -it nvme-exporter /bin/sh

# View container filesystem
docker exec nvme-exporter find /app -type f -name "*.py"

# Check Python dependencies
docker exec nvme-exporter pip list
```

### NVMe-CLI Testing

```bash
# Test nvme-cli installation
docker exec nvme-exporter nvme version

# List all NVMe devices
docker exec nvme-exporter nvme list -o json

# Get SMART data for specific device
docker exec nvme-exporter nvme smart-log /dev/nvme0 -o json

# Check controller registers
docker exec nvme-exporter nvme show-regs /dev/nvme0 -o json

# Test with verbose output
docker exec nvme-exporter nvme list -v
```

### Python Application Debugging

```bash
# Run Python script directly with debug
docker exec nvme-exporter python nvme_exporter.py -p 9900 -u 10

# Test individual modules
docker exec nvme-exporter python -c "import nvme_list; print(nvme_list.get_nvme_list())"
docker exec nvme-exporter python -c "import nvme_smart; print(nvme_smart.get_smart_log('/dev/nvme0'))"

# Check Python path and imports
docker exec nvme-exporter python -c "import sys; print(sys.path)"
```

## Environment-Specific Solutions

### Windows/WSL

**Limitations:**
- NVMe passthrough not supported in WSL2
- Docker Desktop doesn't expose host NVMe devices

**Solutions:**
```bash
# Use simulation mode for testing
docker run -d -p 9900:9900 -e SIMULATION=1 \
  ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest

# For real monitoring, use native Linux or Windows monitoring tools
```

**WSL2 Specific Issues:**
```bash
# Check WSL version
wsl --list --verbose

# Ensure Docker Desktop is configured for WSL2
# Settings -> General -> Use WSL 2 based engine
```

### macOS

**Limitations:**
- No native NVMe devices in Docker Desktop
- Limited device passthrough support

**Solutions:**
```bash
# Use simulation mode
docker run -d -p 9900:9900 -e SIMULATION=1 \
  ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest

# For development, connect to remote Linux systems
ssh user@linux-host "docker run [options] nvme_exporter"
```

### Linux Server

**Common Issues and Solutions:**
```bash
# Ensure nvme-cli is available on host
nvme version || sudo apt-get install nvme-cli

# Check device permissions
ls -la /dev/nvme*
sudo chmod 644 /dev/nvme*  # If needed

# Use privileged mode
docker run --privileged -v /dev:/dev -p 9900:9900 [image]

# Check SELinux/AppArmor if enabled
sudo setenforce 0  # Temporarily disable SELinux
sudo systemctl status apparmor  # Check AppArmor status
```

**SystemD Integration Issues:**
```bash
# Check systemd service status
sudo systemctl status nvme-exporter

# View service logs
sudo journalctl -u nvme-exporter -f

# Debug service file
sudo systemctl --failed
sudo systemctl list-dependencies nvme-exporter
```

### Kubernetes

**Common Issues:**
```bash
# Check pod status
kubectl get pods -n monitoring | grep nvme

# View pod logs
kubectl logs -n monitoring daemonset/nvme-exporter

# Check node selector and tolerations
kubectl describe ds nvme-exporter -n monitoring

# Test privileged access
kubectl exec -it [pod-name] -n monitoring -- nvme list
```

**Security Context Issues:**
```yaml
# Ensure proper security context
securityContext:
  privileged: true
  runAsUser: 0
```

**Volume Mount Issues:**
```bash
# Check if /dev is properly mounted
kubectl exec -it [pod-name] -n monitoring -- ls -la /dev/nvme*

# Verify hostPath volume
kubectl get pv | grep nvme
```

## Advanced Debugging

### Performance Issues

```bash
# Monitor container performance
docker stats nvme-exporter

# Check update frequency
docker logs nvme-exporter | grep "sleeping"

# Adjust update period
docker run -e UPDATE_PERIOD=60 [other-options] [image]

# Profile memory usage
docker exec nvme-exporter python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"
```

### Network Debugging

```bash
# Test connectivity from different locations
curl -v http://localhost:9900/metrics
curl -v http://container-ip:9900/metrics
curl -v http://host-ip:9900/metrics

# Check if metrics are being generated
curl -s http://localhost:9900/metrics | grep nvme_smart | wc -l

# Monitor network traffic
sudo tcpdump -i any port 9900

# Test with different network modes
docker run --network host [other-options] [image]
```

### Data Integrity Issues

```bash
# Compare container output with host commands
docker exec nvme-exporter nvme list -o json > container_output.json
sudo nvme list -o json > host_output.json
diff container_output.json host_output.json

# Verify SMART data consistency
for i in {1..5}; do
  docker exec nvme-exporter nvme smart-log /dev/nvme0 -o json | jq .temperature
  sleep 2
done

# Check for JSON parsing errors
docker logs nvme-exporter 2>&1 | grep -i "json\|parse\|error"
```

## Getting Help

### Information to Collect

When reporting issues, please provide:

```bash
# System information
uname -a
docker version
docker info

# Container information
docker ps -a | grep nvme
docker logs nvme-exporter --tail=50

# Host NVMe information
sudo nvme list -o json
ls -la /dev/nvme*

# Network information
netstat -tulpn | grep 9900
curl -v http://localhost:9900/metrics | head -20
```

### Useful Log Analysis

```bash
# Extract error messages
docker logs nvme-exporter 2>&1 | grep -i error

# Check for permission issues
docker logs nvme-exporter 2>&1 | grep -i "permission\|denied\|access"

# Monitor metrics generation
docker logs nvme-exporter 2>&1 | grep -i "metrics\|updated\|sleeping"

# Check for device detection
docker logs nvme-exporter 2>&1 | grep -i "device\|nvme\|found"
```

### Creating Minimal Reproduction Cases

```bash
# Test with minimal configuration
docker run --rm -it --privileged -v /dev:/dev -p 9901:9900 \
  -e DEBUG=1 \
  ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest

# Test with simulation mode
docker run --rm -it -p 9902:9900 \
  -e SIMULATION=1 -e DEBUG=1 \
  ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest

# Save debug output
docker run --rm --privileged -v /dev:/dev -p 9903:9900 \
  -e DEBUG=1 \
  ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest \
  2>&1 | tee debug_output.log
```

This troubleshooting guide should help you diagnose and resolve most common issues with nvme_exporter. If you encounter problems not covered here, the debug commands and information collection steps will help you gather the necessary details for further assistance. 