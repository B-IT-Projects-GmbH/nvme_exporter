#!/bin/bash
set -e

# Function to check if nvme-cli is working
check_nvme_cli() {
    if command -v nvme >/dev/null 2>&1; then
        echo "nvme-cli is available"
        nvme version || echo "Warning: nvme version command failed"
    else
        echo "Warning: nvme-cli not found in PATH"
    fi
}

# Function to check NVMe devices availability
check_nvme_devices() {
    if [ -d "/dev" ]; then
        NVME_DEVICES=$(ls /dev/nvme* 2>/dev/null | head -5 || true)
        if [ -n "$NVME_DEVICES" ]; then
            echo "Found NVMe devices:"
            echo "$NVME_DEVICES"
        else
            echo "Warning: No NVMe devices found in /dev/"
        fi
    else
        echo "Warning: /dev directory not accessible"
    fi
}

# Print environment info
echo "=== NVMe Exporter Docker Container ==="
echo "Port: ${PORT:-9900}"
echo "Update Period: ${UPDATE_PERIOD:-10} seconds"
echo "======================================="

# Check system components
check_nvme_cli
check_nvme_devices

# Start the application
echo "Starting nvme_exporter..."
exec python nvme_exporter.py "$@" 