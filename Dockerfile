# Build stage - just for Python dependencies
FROM python:3.9-alpine AS builder

# Create build directory
WORKDIR /build

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/build/python-deps -r requirements.txt

# Runtime stage - minimal image with only runtime dependencies
FROM python:3.9-alpine AS runtime

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/python-deps
ENV PATH="/usr/local/bin:/usr/local/sbin:$PATH"

# Set default environment variables for the application
ENV PORT=9900
ENV UPDATE_PERIOD=10

# Install runtime dependencies including nvme-cli from Alpine packages
RUN apk add --no-cache \
    curl \
    bash \
    nvme-cli

# Create application directory
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /build/python-deps ./python-deps

# Test nvme-cli installation
RUN echo "=== Testing nvme-cli installation ===" && \
    which nvme && \
    nvme version && \
    nvme --help | head -5

# Copy application files
COPY *.py ./
COPY docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

# Create a non-root user (though the container may need to run privileged for NVMe access)
RUN addgroup -S nvme && adduser -S -G nvme nvme && \
    chown -R nvme:nvme /app

# Expose the metrics port
EXPOSE 9900

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/metrics || exit 1

# Note: Running as root is required for NVMe device access
# USER nvme

# Set the entrypoint
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["-p", "9900", "-u", "10"]

# Export stage - for creating exportable images
FROM runtime AS export
LABEL maintainer="B.IT Projects GmbH"
LABEL version="1.0"
LABEL description="NVMe Prometheus Exporter - Docker optimized version" 