# OpenWrt Image Builder Docker Container
# Builds custom firmware images for D-Link DIR-1960 A1 mesh nodes
#
# Usage:
#   docker-compose build
#   docker-compose run --rm imagebuilder /scripts/build-image.sh node3

FROM ubuntu:22.04

LABEL maintainer="OpenWrt Mesh Project"
LABEL description="OpenWrt Image Builder for ramips/mt7621 (D-Link DIR-1960 A1)"

ENV DEBIAN_FRONTEND=noninteractive
ENV IMAGEBUILDER_VERSION=24.10.4
ENV TARGET=ramips
ENV SUBTARGET=mt7621

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    file \
    gawk \
    gettext \
    git \
    libncurses5-dev \
    libssl-dev \
    python3 \
    python3-distutils \
    rsync \
    unzip \
    wget \
    xsltproc \
    zlib1g-dev \
    zstd \
    && rm -rf /var/lib/apt/lists/*

# Download and extract Image Builder
WORKDIR /builder
RUN wget -q "https://downloads.openwrt.org/releases/${IMAGEBUILDER_VERSION}/targets/${TARGET}/${SUBTARGET}/openwrt-imagebuilder-${IMAGEBUILDER_VERSION}-${TARGET}-${SUBTARGET}.Linux-x86_64.tar.zst" \
    && tar --zstd -xf openwrt-imagebuilder-*.tar.zst --strip-components=1 \
    && rm -f openwrt-imagebuilder-*.tar.zst \
    && chown -R 1000:1000 /builder

# Create output directory
RUN mkdir -p /output && chown 1000:1000 /output

WORKDIR /builder

# Default command shows available profiles
CMD ["make", "info"]
