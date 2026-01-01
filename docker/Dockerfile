# Multi-stage Dockerfile for Ansible mesh network deployment
# Based on Alpine Linux for minimal image size

# Stage 1: Base with Python and system dependencies
FROM python:3.11-alpine AS base

# Install system dependencies
RUN apk add --no-cache \
    openssh-client \
    sshpass \
    git \
    bash \
    curl \
    ca-certificates \
    && rm -rf /var/cache/apk/*

# Stage 2: Python dependencies builder
FROM base AS builder

# Install build dependencies for compiling Python packages (e.g., ruamel-yaml-clibz)
RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev

# Install UV package manager
RUN pip install --no-cache-dir uv

# Copy requirements file
COPY docker/requirements.txt /tmp/requirements.txt

# Install Python dependencies using UV
RUN uv pip install --system -r /tmp/requirements.txt

# Stage 3: Final runtime image
FROM base

# Copy installed Python packages from builder
COPY --from=builder /usr/local /usr/local

# Set working directory
WORKDIR /ansible

# Copy Ansible project files into container
# These serve as the base, bind mounts can override for development
COPY openwrt-mesh-ansible/ansible.cfg /ansible/
COPY openwrt-mesh-ansible/inventory/ /ansible/inventory/
COPY openwrt-mesh-ansible/group_vars/ /ansible/group_vars/
COPY openwrt-mesh-ansible/playbooks/ /ansible/playbooks/
COPY openwrt-mesh-ansible/templates/ /ansible/templates/
COPY openwrt-mesh-ansible/Makefile /ansible/

# Create SSH directory with proper permissions
RUN mkdir -p /root/.ssh && chmod 700 /root/.ssh

# Copy entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set environment variables
ENV ANSIBLE_HOST_KEY_CHECKING=False \
    ANSIBLE_RETRY_FILES_ENABLED=False \
    ANSIBLE_SSH_PIPELINING=True \
    PYTHONUNBUFFERED=1

# Expose volume mount points
VOLUME ["/ansible", "/root/.ssh", "/backups"]

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Default command
CMD ["ansible", "--version"]
