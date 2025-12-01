#!/bin/bash
###############################################################################
# OpenWrt Local Package Repository Setup
# Downloads packages and firmware images for offline/fast deployment
###############################################################################
# shellcheck disable=SC1090,SC2001,SC2034,SC2086,SC2094,SC2145,SC2155

set -e

# Parse command line arguments
FULL_ARCHIVE=true
if [ "$1" = "--selective" ]; then
    FULL_ARCHIVE=false
    echo "Running in SELECTIVE mode (only .env packages)"
else
    echo "Running in FULL ARCHIVE mode (all packages)"
fi

# Load configuration from .env
# Determine script directory and find .env relative to it
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ENV_FILE="${PROJECT_ROOT}/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: .env file not found at $ENV_FILE"
    echo "Expected location: ${PROJECT_ROOT}/.env"
    exit 1
fi

# Source .env and extract OpenWrt configuration
set -a
source "$ENV_FILE"
set +a

# Configuration from .env (with fallback defaults)
OPENWRT_VERSION="${OPENWRT_VERSION:-24.10.4}"
TARGET="${OPENWRT_TARGET:-ramips/mt7621}"
ARCH="${OPENWRT_ARCH:-mipsel_24kc}"
REPO_DIR="$(pwd)/openwrt-repo"
BASE_URL="https://downloads.openwrt.org/releases/${OPENWRT_VERSION}"

# Discover kernel version directory for kmods
KMODS_BASE_URL="https://downloads.openwrt.org/releases/${OPENWRT_VERSION}/targets/${TARGET}/kmods"
echo "Discovering kernel version directory..."
KERNEL_VERSION=$(curl -s "${KMODS_BASE_URL}/" | grep -oE 'href="[0-9]+\.[0-9]+\.[0-9]+-[0-9]+-[a-f0-9]+/"' | head -1 | sed 's/href="//;s/\/"//')
if [ -z "$KERNEL_VERSION" ]; then
    echo "ERROR: Could not detect kernel version directory"
    echo "Please check ${KMODS_BASE_URL}/"
    exit 1
fi
echo "Detected kernel version: ${KERNEL_VERSION}"
KMODS_URL="${KMODS_BASE_URL}/${KERNEL_VERSION}"

# Logging configuration
LOG_DIR="$(pwd)/logs"
LOG_FILE="${LOG_DIR}/repo-setup-$(date +%Y%m%d-%H%M%S).log"
mkdir -p "${LOG_DIR}"

# Download configuration
MAX_RETRIES=3
RETRY_DELAY=2           # Initial delay in seconds
RATE_LIMIT_DELAY=0.1    # Delay between downloads (seconds) - reduced for speed
MAX_PARALLEL=3          # Max parallel downloads
WGET_TIMEOUT=30         # Connection timeout
CACHE_MAX_AGE=86400     # Skip remote check if local file is newer than this (seconds, 86400=24h)

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Statistics
TOTAL_DOWNLOADS=0
SUCCESSFUL_DOWNLOADS=0
FAILED_DOWNLOADS=0
SKIPPED_DOWNLOADS=0
PLACEHOLDER_FILES=0

# Timing
SCRIPT_START_TIME=$(date +%s)
PHASE_START_TIME=0

# Timing functions
start_phase() {
    PHASE_START_TIME=$(date +%s)
}

end_phase() {
    local phase_name=$1
    local phase_end=$(date +%s)
    local phase_duration=$((phase_end - PHASE_START_TIME))
    local mins=$((phase_duration / 60))
    local secs=$((phase_duration % 60))
    if [ $mins -gt 0 ]; then
        echo -e "  ${YELLOW}⏱ ${phase_name}: ${mins}m ${secs}s${NC}"
    else
        echo -e "  ${YELLOW}⏱ ${phase_name}: ${secs}s${NC}"
    fi
}

format_duration() {
    local duration=$1
    local hours=$((duration / 3600))
    local mins=$(((duration % 3600) / 60))
    local secs=$((duration % 60))
    if [ $hours -gt 0 ]; then
        echo "${hours}h ${mins}m ${secs}s"
    elif [ $mins -gt 0 ]; then
        echo "${mins}m ${secs}s"
    else
        echo "${secs}s"
    fi
}

# Logging functions
log() {
    echo "$@" | tee -a "${LOG_FILE}"
}

log_error() {
    echo -e "${RED}$@${NC}" | tee -a "${LOG_FILE}"
}

log_success() {
    echo -e "${GREEN}$@${NC}" | tee -a "${LOG_FILE}"
}

log_info() {
    echo -e "${BLUE}$@${NC}" | tee -a "${LOG_FILE}"
}

# Start logging
log "=========================================="
log "OpenWrt Local Repository Setup"
log "Started: $(date '+%Y-%m-%d %H:%M:%S')"
log "Log file: ${LOG_FILE}"
log "=========================================="
log ""

# Retry function with exponential backoff
# Returns: 0=success (downloaded), 1=failed, 2=skipped (already up-to-date)
retry_download() {
    local url=$1
    local output=$2
    local attempt=1
    local delay=$RETRY_DELAY
    local output_dir=$(dirname "$output")
    local output_file=$(basename "$output")

    # Fast path: if local file exists, is non-empty, and is recent enough, skip remote check
    if [ -f "$output" ] && [ -s "$output" ]; then
        local file_age=$(($(date +%s) - $(stat -c %Y "$output" 2>/dev/null || echo 0)))
        if [ $file_age -lt $CACHE_MAX_AGE ]; then
            return 2  # File is recent enough, skip
        fi
    fi

    # Change to output directory so wget -N works correctly
    local original_dir=$(pwd)
    mkdir -p "$output_dir"
    cd "$output_dir"

    while [ $attempt -le $MAX_RETRIES ]; do
        # Use wget -N to only download if remote is newer (timestamping mode)
        # Note: -N is incompatible with -O, so we download to current dir
        local wget_output
        if wget_output=$(wget --timeout=$WGET_TIMEOUT --tries=1 -q -N "$url" 2>&1); then
            cd "$original_dir"
            # Check if file was actually downloaded or skipped due to timestamp
            if echo "$wget_output" | grep -q "not retrieving"; then
                return 2  # File exists and is up-to-date
            fi
            return 0  # Successfully downloaded
        else
            if [ $attempt -lt $MAX_RETRIES ]; then
                echo -e "      ${YELLOW}Retry $attempt/$MAX_RETRIES after ${delay}s...${NC}" >&2
                sleep $delay
                delay=$((delay * 2))  # Exponential backoff
                attempt=$((attempt + 1))
            else
                cd "$original_dir"
                return 1
            fi
        fi
    done
    cd "$original_dir"
    return 1
}

# Rate-limited download with retry
download_with_retry() {
    local url=$1
    local output=$2
    local description=${3:-"file"}

    TOTAL_DOWNLOADS=$((TOTAL_DOWNLOADS + 1))

    # Rate limiting - wait before download
    sleep $RATE_LIMIT_DELAY

    # Try to download with retries (wget -N checks if remote is newer)
    retry_download "$url" "$output"
    local result=$?

    if [ $result -eq 0 ]; then
        SUCCESSFUL_DOWNLOADS=$((SUCCESSFUL_DOWNLOADS + 1))
        echo "$(date '+%Y-%m-%d %H:%M:%S') - SUCCESS: $description" >> "${LOG_FILE}"
        return 0
    elif [ $result -eq 2 ]; then
        SKIPPED_DOWNLOADS=$((SKIPPED_DOWNLOADS + 1))
        return 0
    else
        FAILED_DOWNLOADS=$((FAILED_DOWNLOADS + 1))
        echo -e "      ${RED}✗ Failed: $description${NC}" >&2
        echo "$(date '+%Y-%m-%d %H:%M:%S') - FAILED: $description (URL: $url)" >> "${LOG_FILE}"
        return 1
    fi
}

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}OpenWrt Local Repository Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Version: ${OPENWRT_VERSION}"
echo "Target: ${TARGET}"
echo "Architecture: ${ARCH}"
echo "Repository: ${REPO_DIR}"
echo ""
echo "Download Configuration:"
echo "  Max retries: ${MAX_RETRIES}"
echo "  Rate limit: ${RATE_LIMIT_DELAY}s between downloads"
echo "  Timeout: ${WGET_TIMEOUT}s per attempt"
echo ""

# Create directory structure
echo -e "${GREEN}Creating repository directories...${NC}"
mkdir -p "${REPO_DIR}"/{packages,targets,releases}
mkdir -p "${REPO_DIR}/packages/${OPENWRT_VERSION}/${ARCH}"
mkdir -p "${REPO_DIR}/targets/${TARGET}/kmods/${KERNEL_VERSION}"

# Download package indexes
echo -e "${GREEN}Downloading package indexes...${NC}"
start_phase
cd "${REPO_DIR}/packages/${OPENWRT_VERSION}/${ARCH}"

for feed in base luci packages routing telephony; do
    echo "  Downloading ${feed} index..."
    mkdir -p ${feed}

    download_with_retry \
        "${BASE_URL}/packages/${ARCH}/${feed}/Packages.gz" \
        "${feed}/Packages.gz" \
        "${feed}/Packages.gz"

    download_with_retry \
        "${BASE_URL}/packages/${ARCH}/${feed}/Packages.sig" \
        "${feed}/Packages.sig" \
        "${feed}/Packages.sig"

    download_with_retry \
        "${BASE_URL}/packages/${ARCH}/${feed}/Packages" \
        "${feed}/Packages" \
        "${feed}/Packages"

    # Decompress if needed
    if [ -f "${feed}/Packages.gz" ] && [ ! -f "${feed}/Packages" ]; then
        gunzip -c "${feed}/Packages.gz" > "${feed}/Packages" 2>/dev/null || true
    fi
done

echo "  Package indexes downloaded successfully"
end_phase "Package indexes"

# Download kernel modules index
echo -e "${GREEN}Downloading kernel modules index...${NC}"
start_phase
cd "${REPO_DIR}/targets/${TARGET}/kmods/${KERNEL_VERSION}"

echo "  Downloading kmods index from ${KERNEL_VERSION}..."
download_with_retry \
    "${KMODS_URL}/Packages.gz" \
    "Packages.gz" \
    "kmods/Packages.gz"

download_with_retry \
    "${KMODS_URL}/Packages.sig" \
    "Packages.sig" \
    "kmods/Packages.sig"

download_with_retry \
    "${KMODS_URL}/Packages" \
    "Packages" \
    "kmods/Packages"

# Decompress if needed
if [ -f "Packages.gz" ] && [ ! -f "Packages" ]; then
    gunzip -c "Packages.gz" > "Packages" 2>/dev/null || true
fi

echo "  Kernel modules index downloaded successfully"
end_phase "Kmods index"

# Function to download package
download_package() {
    local package=$1
    local found=false

    # Skip luci-i18n packages (create placeholder)
    if [[ "$package" == luci-i18n-* ]]; then
        for feed in base luci packages routing telephony; do
            if [ -f "${feed}/Packages" ]; then
                if grep -q "^Package: ${package}$" "${feed}/Packages"; then
                    filename=$(awk "/^Package: ${package}$/,/^$/" "${feed}/Packages" | grep "^Filename:" | cut -d' ' -f2)
                    if [ -n "$filename" ]; then
                        local basename_file=$(basename ${filename})
                        local output_file="${feed}/${basename_file}"
                        if [ ! -f "$output_file" ]; then
                            touch "$output_file"
                            PLACEHOLDER_FILES=$((PLACEHOLDER_FILES + 1))
                            echo "    ${package} (${feed}) - placeholder created"
                            echo "$(date '+%Y-%m-%d %H:%M:%S') - PLACEHOLDER: ${package}" >> "${LOG_FILE}"
                        else
                            echo "    ${package} (${feed}) - placeholder exists"
                        fi
                        return
                    fi
                fi
            fi
        done
    fi

    # Check kernel modules feed first (for kmod-* packages)
    if [[ "$package" == kmod-* ]]; then
        local kmods_packages="${REPO_DIR}/targets/${TARGET}/kmods/${KERNEL_VERSION}/Packages"
        if [ -f "$kmods_packages" ]; then
            if grep -q "^Package: ${package}$" "$kmods_packages"; then
                filename=$(awk "/^Package: ${package}$/,/^$/" "$kmods_packages" | grep "^Filename:" | cut -d' ' -f2)
                if [ -n "$filename" ]; then
                    local basename_file=$(basename ${filename})
                    local output_file="${REPO_DIR}/targets/${TARGET}/kmods/${KERNEL_VERSION}/${basename_file}"

                    # Download (wget -N will skip if local file is up-to-date)
                    echo -n "    ${package} (kmods) - "
                    download_with_retry \
                        "${KMODS_URL}/${basename_file}" \
                        "${output_file}" \
                        "${package}"
                    local result=$?
                    if [ $result -eq 0 ]; then
                        echo "ok"
                    else
                        echo "failed"
                    fi
                    found=true
                    return
                fi
            fi
        fi
    fi

    for feed in base luci packages routing telephony; do
        if [ -f "${feed}/Packages" ]; then
            # Check if package exists in this feed
            if grep -q "^Package: ${package}$" "${feed}/Packages"; then
                filename=$(awk "/^Package: ${package}$/,/^$/" "${feed}/Packages" | grep "^Filename:" | cut -d' ' -f2)
                if [ -n "$filename" ]; then
                    local basename_file=$(basename ${filename})
                    local output_file="${feed}/${basename_file}"

                    # Download (wget -N will skip if local file is up-to-date)
                    echo -n "    ${package} (${feed}) - "
                    download_with_retry \
                        "${BASE_URL}/packages/${ARCH}/${feed}/${basename_file}" \
                        "${output_file}" \
                        "${package}"
                    local result=$?
                    if [ $result -eq 0 ]; then
                        echo "ok"
                    else
                        echo "failed"
                    fi
                    found=true
                    break
                fi
            fi
        fi
    done

    if [ "$found" = false ]; then
        echo "    ${package} (not found in any feed)"
        FAILED_DOWNLOADS=$((FAILED_DOWNLOADS + 1))
    fi
}

# Build a map of filename -> sha256 from Packages file
# Output: filename:sha256 pairs, one per line
parse_packages_checksums() {
    local packages_file=$1
    awk '
    /^Filename:/ { filename = $2 }
    /^SHA256sum:/ { print filename ":" $2; filename = "" }
    ' "$packages_file"
}

# Download all packages from a feed using checksum-based sync
download_all_packages_from_feed() {
    local feed=$1
    local package_count=0
    local download_count=0
    local skip_count=0
    local feed_start_time=$(date +%s)

    if [ ! -f "${feed}/Packages" ]; then
        echo "  ${feed}: No Packages file found"
        echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: ${feed}/Packages not found" >> "${LOG_FILE}"
        return
    fi

    echo "  ${feed}: Analyzing packages..."

    # Parse package checksums from index
    local checksums_file=$(mktemp)
    parse_packages_checksums "${feed}/Packages" > "$checksums_file"
    local total=$(wc -l < "$checksums_file")

    echo "  ${feed}: Found ${total} packages, comparing checksums..."
    echo "$(date '+%Y-%m-%d %H:%M:%S') - FEED: ${feed} - ${total} packages found" >> "${LOG_FILE}"

    # Build list of packages that need downloading
    local to_download_file=$(mktemp)
    while IFS=: read -r filename expected_sha256; do
        if [ -z "$filename" ]; then continue; fi

        local basename_file=$(basename "${filename}")
        local output_file="${feed}/${basename_file}"
        local package_name=$(echo "$basename_file" | sed 's/_.*$//')

        package_count=$((package_count + 1))

        # Check if this is a luci-i18n package (create placeholder instead of downloading)
        if [[ "$package_name" == luci-i18n-* ]]; then
            if [ ! -f "$output_file" ]; then
                touch "$output_file"
                PLACEHOLDER_FILES=$((PLACEHOLDER_FILES + 1))
            fi
            skip_count=$((skip_count + 1))
            continue
        fi

        # Check if file exists and has correct checksum
        if [ -f "$output_file" ]; then
            local local_sha256=$(sha256sum "$output_file" 2>/dev/null | cut -d' ' -f1)
            if [ "$local_sha256" = "$expected_sha256" ]; then
                skip_count=$((skip_count + 1))
                SKIPPED_DOWNLOADS=$((SKIPPED_DOWNLOADS + 1))
                continue
            fi
        fi

        # File needs downloading
        echo "${basename_file}:${expected_sha256}" >> "$to_download_file"
    done < "$checksums_file"
    rm -f "$checksums_file"

    local need_download=$(wc -l < "$to_download_file")
    echo "  ${feed}: ${skip_count} up-to-date, ${need_download} need downloading"

    # Download only the files that need updating
    if [ "$need_download" -gt 0 ]; then
        while IFS=: read -r basename_file expected_sha256; do
            if [ -z "$basename_file" ]; then continue; fi

            local output_file="${feed}/${basename_file}"
            local package_name=$(echo "$basename_file" | sed 's/_.*$//')

            download_count=$((download_count + 1))
            TOTAL_DOWNLOADS=$((TOTAL_DOWNLOADS + 1))

            # Rate limiting
            sleep $RATE_LIMIT_DELAY

            # Download the file
            if wget --timeout=$WGET_TIMEOUT --tries=3 -q -O "$output_file" \
                "${BASE_URL}/packages/${ARCH}/${feed}/${basename_file}"; then
                SUCCESSFUL_DOWNLOADS=$((SUCCESSFUL_DOWNLOADS + 1))
                echo "$(date '+%Y-%m-%d %H:%M:%S') - SUCCESS: ${package_name}" >> "${LOG_FILE}"
            else
                FAILED_DOWNLOADS=$((FAILED_DOWNLOADS + 1))
                echo -e "      ${RED}✗ Failed: ${package_name}${NC}" >&2
                echo "$(date '+%Y-%m-%d %H:%M:%S') - FAILED: ${package_name}" >> "${LOG_FILE}"
            fi

            # Progress every 50 downloads
            if [ $((download_count % 50)) -eq 0 ]; then
                local elapsed=$(($(date +%s) - feed_start_time))
                local rate=0
                local eta="--"
                if [ $elapsed -gt 0 ]; then
                    rate=$((download_count * 100 / elapsed))
                    rate_int=$((rate / 100))
                    if [ $rate_int -gt 0 ]; then
                        local remaining=$(((need_download - download_count) * 100 / rate))
                        eta=$(format_duration $remaining)
                    fi
                fi
                echo "    Downloading: ${download_count}/${need_download} (ETA: ${eta})"
            fi
        done < "$to_download_file"
    fi
    rm -f "$to_download_file"

    local feed_duration=$(($(date +%s) - feed_start_time))
    echo "  ${feed}: Complete - ${skip_count} cached, ${download_count} downloaded - $(format_duration $feed_duration)"
}

# Download all kernel modules using checksum-based sync
download_all_kmods() {
    local package_count=0
    local download_count=0
    local skip_count=0
    local kmods_start_time=$(date +%s)

    cd "${REPO_DIR}/targets/${TARGET}/kmods/${KERNEL_VERSION}"

    if [ ! -f "Packages" ]; then
        echo "  ERROR: Packages file not found"
        echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: kmods/Packages not found" >> "${LOG_FILE}"
        return
    fi

    echo "  Analyzing kernel modules..."

    # Parse package checksums from index
    local checksums_file=$(mktemp)
    parse_packages_checksums "Packages" > "$checksums_file"
    local total=$(wc -l < "$checksums_file")

    echo "  Found ${total} kernel modules, comparing checksums..."
    echo "$(date '+%Y-%m-%d %H:%M:%S') - KMODS: ${total} packages found" >> "${LOG_FILE}"

    # Build list of packages that need downloading
    local to_download_file=$(mktemp)
    while IFS=: read -r filename expected_sha256; do
        if [ -z "$filename" ]; then continue; fi

        local basename_file=$(basename "${filename}")
        local output_file="${basename_file}"

        package_count=$((package_count + 1))

        # Check if file exists and has correct checksum
        if [ -f "$output_file" ]; then
            local local_sha256=$(sha256sum "$output_file" 2>/dev/null | cut -d' ' -f1)
            if [ "$local_sha256" = "$expected_sha256" ]; then
                skip_count=$((skip_count + 1))
                SKIPPED_DOWNLOADS=$((SKIPPED_DOWNLOADS + 1))
                continue
            fi
        fi

        # File needs downloading
        echo "${basename_file}:${expected_sha256}" >> "$to_download_file"
    done < "$checksums_file"
    rm -f "$checksums_file"

    local need_download=$(wc -l < "$to_download_file")
    echo "  kmods: ${skip_count} up-to-date, ${need_download} need downloading"

    # Download only the files that need updating
    if [ "$need_download" -gt 0 ]; then
        while IFS=: read -r basename_file expected_sha256; do
            if [ -z "$basename_file" ]; then continue; fi

            local output_file="${basename_file}"
            local package_name=$(echo "$basename_file" | sed 's/_.*$//')

            download_count=$((download_count + 1))
            TOTAL_DOWNLOADS=$((TOTAL_DOWNLOADS + 1))

            # Rate limiting
            sleep $RATE_LIMIT_DELAY

            # Download the file
            if wget --timeout=$WGET_TIMEOUT --tries=3 -q -O "$output_file" \
                "${KMODS_URL}/${basename_file}"; then
                SUCCESSFUL_DOWNLOADS=$((SUCCESSFUL_DOWNLOADS + 1))
                echo "$(date '+%Y-%m-%d %H:%M:%S') - SUCCESS: ${package_name}" >> "${LOG_FILE}"
            else
                FAILED_DOWNLOADS=$((FAILED_DOWNLOADS + 1))
                echo -e "      ${RED}✗ Failed: ${package_name}${NC}" >&2
                echo "$(date '+%Y-%m-%d %H:%M:%S') - FAILED: ${package_name}" >> "${LOG_FILE}"
            fi

            # Progress every 50 downloads
            if [ $((download_count % 50)) -eq 0 ]; then
                local elapsed=$(($(date +%s) - kmods_start_time))
                local eta="--"
                if [ $elapsed -gt 0 ] && [ $download_count -gt 0 ]; then
                    local remaining=$(((need_download - download_count) * elapsed / download_count))
                    eta=$(format_duration $remaining)
                fi
                echo "    Downloading: ${download_count}/${need_download} (ETA: ${eta})"
            fi
        done < "$to_download_file"
    fi
    rm -f "$to_download_file"

    local kmods_duration=$(($(date +%s) - kmods_start_time))
    echo "  Kernel modules: Complete - ${skip_count} cached, ${download_count} downloaded - $(format_duration $kmods_duration)"
}

# Download packages based on mode
if [ "$FULL_ARCHIVE" = true ]; then
    echo -e "${GREEN}Downloading ALL packages from all feeds...${NC}"
    echo "This will download the complete package archive (~500 MB - 1 GB)"
    echo ""

    # Change to packages directory (we're currently in kmods directory from index download)
    cd "${REPO_DIR}/packages/${OPENWRT_VERSION}/${ARCH}"

    for feed in base luci packages routing telephony; do
        echo -e "${BLUE}=== Feed: ${feed} ===${NC}"
        download_all_packages_from_feed "${feed}"
        echo ""
    done

    # Download kernel modules
    echo -e "${BLUE}=== Kernel Modules (kmods) ===${NC}"
    download_all_kmods
    echo ""
else
    echo -e "${GREEN}Downloading selective packages from .env...${NC}"

    # Change to packages directory where Packages files are located
    cd "${REPO_DIR}/packages/${OPENWRT_VERSION}/${ARCH}"

    # REQUIRED_PACKAGES and OPTIONAL_PACKAGES are already loaded from .env at line 30-32
    if [ -n "$REQUIRED_PACKAGES" ]; then
        # Download required packages
        echo "  Required packages:"
        IFS=',' read -ra PKGS <<< "$REQUIRED_PACKAGES"
        for pkg in "${PKGS[@]}"; do
            download_package "$pkg"
        done
    fi

    if [ -n "$OPTIONAL_PACKAGES" ]; then
        # Download optional packages
        echo "  Optional packages:"
        IFS=',' read -ra PKGS <<< "$OPTIONAL_PACKAGES"
        for pkg in "${PKGS[@]}"; do
            download_package "$pkg"
        done
    fi

    # Download additional monitoring packages
    echo "  Monitoring packages:"
    MONITORING_PKGS="collectd collectd-mod-cpu collectd-mod-memory collectd-mod-load collectd-mod-interface collectd-mod-ping collectd-mod-rrdtool collectd-mod-network collectd-mod-iwinfo luci-app-statistics vnstat2 vnstat2-json"
    for pkg in $MONITORING_PKGS; do
        download_package "$pkg"
    done
fi

# Download firmware images
echo -e "${GREEN}Downloading firmware images...${NC}"
start_phase
cd "${REPO_DIR}/targets/${TARGET}"

echo "  Downloading image manifest..."
download_with_retry \
    "${BASE_URL}/targets/${TARGET}/sha256sums" \
    "sha256sums" \
    "sha256sums"

download_with_retry \
    "${BASE_URL}/targets/${TARGET}/sha256sums.sig" \
    "sha256sums.sig" \
    "sha256sums.sig"

echo "  Downloading sysupgrade image..."
SYSUPGRADE_IMAGE=$(grep "sysupgrade.bin" sha256sums 2>/dev/null | grep "dlink_dir-1960-a1" | awk '{print $2}' | sed 's/\*//' || true)
if [ -n "$SYSUPGRADE_IMAGE" ]; then
    if download_with_retry \
        "${BASE_URL}/targets/${TARGET}/${SYSUPGRADE_IMAGE}" \
        "${SYSUPGRADE_IMAGE}" \
        "sysupgrade image"; then
        echo "    Downloaded: ${SYSUPGRADE_IMAGE}"
    fi
fi

echo "  Downloading factory image..."
FACTORY_IMAGE=$(grep "factory.bin" sha256sums 2>/dev/null | grep "dlink_dir-1960-a1" | awk '{print $2}' | sed 's/\*//' || true)
if [ -n "$FACTORY_IMAGE" ]; then
    if download_with_retry \
        "${BASE_URL}/targets/${TARGET}/${FACTORY_IMAGE}" \
        "${FACTORY_IMAGE}" \
        "factory image"; then
        echo "    Downloaded: ${FACTORY_IMAGE}"
    fi
fi
end_phase "Firmware images"

# Create repository index
echo -e "${GREEN}Creating repository structure...${NC}"
cd "${REPO_DIR}"

# Calculate sizes and total time
TOTAL_SIZE=$(du -sh . | cut -f1)
PACKAGE_COUNT=$(find packages -name "*.ipk" 2>/dev/null | wc -l)
IMAGE_COUNT=$(find targets -name "*.bin" 2>/dev/null | wc -l)
TOTAL_ELAPSED=$(($(date +%s) - SCRIPT_START_TIME))
TOTAL_TIME=$(format_duration $TOTAL_ELAPSED)

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Repository setup complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Location: ${REPO_DIR}"
echo "Total size: ${TOTAL_SIZE}"
echo "Packages cached: ${PACKAGE_COUNT}"
echo "Images cached: ${IMAGE_COUNT}"
echo -e "${YELLOW}Total time: ${TOTAL_TIME}${NC}"
echo ""
echo -e "${GREEN}Download Statistics:${NC}"
echo "  Total attempted: ${TOTAL_DOWNLOADS}"
echo "  Successful: ${SUCCESSFUL_DOWNLOADS}"
echo "  Skipped (cached): ${SKIPPED_DOWNLOADS}"
echo "  Placeholders (luci-i18n-*): ${PLACEHOLDER_FILES}"
if [ ${FAILED_DOWNLOADS} -gt 0 ]; then
    echo -e "  ${RED}Failed: ${FAILED_DOWNLOADS}${NC}"
else
    echo "  Failed: ${FAILED_DOWNLOADS}"
fi
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Start HTTP server: ./scripts/start-local-repo.sh"
echo "2. Configure nodes: Update opkg configuration"
echo "3. Deploy: make deploy"
echo ""
echo -e "${BLUE}Log file: ${LOG_FILE}${NC}"
echo ""

# Write final summary to log
{
    echo ""
    echo "=========================================="
    echo "Repository Setup Complete"
    echo "Completed: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "Total time: ${TOTAL_TIME}"
    echo "=========================================="
    echo ""
    echo "Location: ${REPO_DIR}"
    echo "Total size: ${TOTAL_SIZE}"
    echo "Packages cached: ${PACKAGE_COUNT}"
    echo "Images cached: ${IMAGE_COUNT}"
    echo ""
    echo "Download Statistics:"
    echo "  Total attempted: ${TOTAL_DOWNLOADS}"
    echo "  Successful: ${SUCCESSFUL_DOWNLOADS}"
    echo "  Skipped (cached): ${SKIPPED_DOWNLOADS}"
    echo "  Placeholders (luci-i18n-*): ${PLACEHOLDER_FILES}"
    echo "  Failed: ${FAILED_DOWNLOADS}"
    echo ""
    if [ ${FAILED_DOWNLOADS} -gt 0 ]; then
        echo "FAILED DOWNLOADS:"
        grep "FAILED:" "${LOG_FILE}" | tail -20
    fi
    echo "=========================================="
} >> "${LOG_FILE}"
