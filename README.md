# nvme_exporter for Prometheus

:cyclone: **nvme_exporter** provides comprehensive SMART metrics for NVMe SSDs, including device health, lifetime statistics, temperature monitoring, and I/O operations data. Designed for production environments with Docker support and Prometheus integration.

**Key Features:**
- 🚀 **Docker-ready** with multi-platform support (AMD64/ARM64)
- 📊 **Real-time SMART metrics** from NVMe devices 
- 🔄 **Simulation mode** for testing without real hardware
- 🛠️ **Debug logging** for troubleshooting
- 🔒 **Production-grade** error handling and monitoring
- 📈 **Prometheus integration** with Grafana dashboards
- 🏗️ **CI/CD pipeline** with automated builds

The information is obtained from NVMe Admin Commands using the NVMe CLI tool. Built on the Python Prometheus client and compatible with modern nvme-cli versions.

## Quick Start

The fastest way to get started is with Docker:

```bash
# Run with real NVMe monitoring (requires privileged mode)
docker run -d \
  --name nvme-exporter \
  --privileged \
  -v /dev:/dev \
  -p 9900:9900 \
  ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest

# Check metrics
curl http://localhost:9900/metrics

# View logs
docker logs nvme-exporter
```

Or test without real hardware:

```bash
# Run in simulation mode (no privileged access needed)
docker run -d \
  --name nvme-sim \
  -p 9900:9900 \
  -e SIMULATION=1 \
  ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest
```

> 📚 **Need more details?** See our comprehensive guides:
> - 🚀 **[Deployment Guide](DEPLOYMENT.md)** for production setups and advanced configurations
> - 🔧 **[Troubleshooting Guide](TROUBLESHOOTING.md)** for common issues and debugging  
> - 💡 **[Examples](EXAMPLES.md)** for detailed usage scenarios and recipes

## Installation

### Docker (Recommended)

**Using Pre-built Image:**
```bash
# Latest version
docker run -d --privileged -v /dev:/dev -p 9900:9900 \
  ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest

# Specific version  
docker run -d --privileged -v /dev:/dev -p 9900:9900 \
  ghcr.io/B-IT-Projects-GmbH/nvme_exporter:v1.0
```

**Building from Source:**
```bash
git clone https://github.com/B-IT-Projects-GmbH/nvme_exporter.git
cd nvme_exporter
docker-compose up -d
```

### Traditional Installation

**Requirements:**
- Python 3.6+ with pip
- nvme-cli (must be pre-installed via system package manager)

```bash
git clone https://github.com/B-IT-Projects-GmbH/nvme_exporter.git
cd nvme_exporter
pip install -r requirements.txt

# Install nvme-cli (distribution-specific)
# Ubuntu/Debian: sudo apt-get install nvme-cli
# CentOS/RHEL: sudo yum install nvme-cli
# Alpine: sudo apk add nvme-cli
```

## Usage

### Command Line
```bash
python nvme_exporter.py -p 9900 -u 10
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Port to listen on | `9900` |
| `UPDATE_PERIOD` | Metric update interval (seconds) | `10` |
| `SIMULATION` | Enable simulation mode | `0` |
| `DEBUG` | Enable verbose debug logging | `0` |

### Docker Examples
```bash
# Production monitoring
docker run -d --privileged -v /dev:/dev -p 9900:9900 \
  -e UPDATE_PERIOD=30 ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest

# Development with debug
docker run -d --privileged -v /dev:/dev -p 9900:9900 \
  -e DEBUG=1 ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest

# Testing with simulation
docker run -d -p 9900:9900 -e SIMULATION=1 \
  ghcr.io/B-IT-Projects-GmbH/nvme_exporter:latest
```

## 📖 Documentation

| Guide | Description | What You'll Find |
|-------|-------------|------------------|
| 🚀 **[Deployment Guide](DEPLOYMENT.md)** | Production deployments & Docker architecture | Multi-platform setups, K8s, monitoring stacks, CI/CD |
| 🔧 **[Troubleshooting](TROUBLESHOOTING.md)** | Common issues & debugging | Quick diagnostics, environment fixes, debug commands |
| 💡 **[Examples](EXAMPLES.md)** | Practical usage scenarios | Configuration recipes, integrations, automation |

## Security Considerations

⚠️ **Important**: Production containers require privileged mode to access NVMe devices. This gives full host system access - only use in trusted environments.

For security-conscious deployments:
- Use simulation mode for development/testing
- Run on dedicated monitoring hosts
- Implement proper network segmentation

> 🔒 **Need more security guidance?** Check out the [Deployment Guide](DEPLOYMENT.md#security-best-practices) for advanced security configurations.

## Access URLs

- **NVMe Exporter**: http://localhost:9900/metrics
- **GitHub Container Registry**: https://ghcr.io/B-IT-Projects-GmbH/nvme_exporter

## Acknowledgments

🙏 **Special Thanks to the Original Creator**

This project is based on the excellent work by **yongseokoh** who created the original nvme_exporter:
- **Original Repository**: [https://github.com/yongseokoh/nvme_exporter](https://github.com/yongseokoh/nvme_exporter)
- **Original Author**: [@yongseokoh](https://github.com/yongseokoh)

**What we've added:**
- 🐳 **Complete Docker containerization** with multi-platform support
- 🚀 **Production-ready deployment** with docker-compose
- 🛠️ **Enhanced error handling** and compatibility with modern nvme-cli versions
- 🔧 **Debug logging** and simulation mode improvements
- 📖 **Comprehensive documentation** and troubleshooting guides
- 🏗️ **CI/CD pipeline** with automated builds and publishing

---

## Grafana Sample
<img src="https://github.com/yongseokoh/nvme_exporter/blob/dev-0.1/sample/grafana_nvme_export.png?raw=true" target="_blank" width="800">

## Available Metrics

### NVMe Health & Monitoring Metrics

**Command**: `nvme smart-log /dev/nvme0 -o json`

| Name | Type | Status |
|------|------|--------|
| critical_warning | Gauge | ✅ |
| temperature | Gauge | ✅ |
| avail_spare | Gauge | ✅ |
| spare_thresh | Gauge | ✅ |
| percent_used | Gauge | ✅ |
| data_units_read | Gauge | ✅ |
| data_units_written | Gauge | ✅ |
| host_read_commands | Gauge | ✅ |
| host_write_commands | Gauge | ✅ |
| controller_busy_time | Gauge | ✅ |
| power_cycles | Gauge | ✅ |
| power_on_hours | Gauge | ✅ |
| unsafe_shutdowns | Gauge | ✅ |
| media_errors | Gauge | ✅ |
| num_err_log_entries | Gauge | ✅ |
| warning_temp_time | Gauge | ✅ |
| critical_comp_time | Gauge | ✅ |
| thm_temp1_trans_count | Gauge | ✅ |
| thm_temp2_trans_count | Gauge | ✅ |

**Command**: `nvme show-regs /dev/nvme0 -o json`

| Name | Type | Status |
|------|------|--------|
| controller_configuration | Gauge | ✅ |
| controller_status | Gauge | ✅ |
| other_metrics | Gauge | 🔄 Pending |

---

## 🚀 Getting Started

1. **Quick Start**: Use the Docker commands above to get running in minutes
2. **Production Setup**: Follow the [Deployment Guide](DEPLOYMENT.md) for robust configurations  
3. **Need Help?**: Check [Troubleshooting](TROUBLESHOOTING.md) for common issues
4. **Advanced Usage**: Explore [Examples](EXAMPLES.md) for integration patterns

> 💡 **Tip**: Start with simulation mode (`-e SIMULATION=1`) to test without real hardware!
