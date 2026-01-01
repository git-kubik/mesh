# Makefile for OpenWrt Mesh Network Ansible

# Source .env file if it exists to load environment variables
-include ../.env
export

# Command prefix to source .env for ansible-playbook commands
ENV_FILE := ../.env
TIMESTAMP := $(shell date +%Y%m%d_%H%M%S)

# Dynamic log naming based on action and node
# Format: logs/ACTION_nodeN_TIMESTAMP.log or logs/ACTION_TIMESTAMP.log
ifdef NODE
  LOG_PREFIX := $(MAKECMDGOALS)_node$(NODE)
else
  LOG_PREFIX := $(MAKECMDGOALS)
endif

ANSIBLE_LOG := logs/$(LOG_PREFIX)_$(TIMESTAMP).log
ANSIBLE_CMD := $(if $(wildcard $(ENV_FILE)),set -a && source $(ENV_FILE) && set +a &&,) ANSIBLE_LOG_PATH=$(ANSIBLE_LOG) ansible-playbook

# Node-specific variables (used with NODE=1, NODE=2, NODE=3)
ifdef NODE
  # Validate NODE is 1, 2, or 3
  ifeq ($(filter $(NODE),1 2 3),)
    $(error NODE must be 1, 2, or 3. Usage: make deploy-node NODE=1)
  endif

  # Node-specific configuration
  NODE_NAME := node$(NODE)
  NODE_IP_PROD := 10.11.12.$(NODE)
  NODE_IP_INITIAL := 192.168.1.1

  # Inventory selection (production uses hosts.yml, initial uses hosts-initial.yml)
  INVENTORY_PROD := inventory/hosts.yml
  INVENTORY_INITIAL := inventory/hosts-initial.yml

  # Verbose flag handling
  VERBOSE_FLAG := $(if $(VERBOSE),-vvv)
endif

.PHONY: help validate-env \
        deploy-node check-node audit-node \
        check-all check-connectivity audit vuln-scan wifi-scan deploy \
        security-audit security-check deploy-security \
        switch-to-initial-network switch-to-mesh-network switch-to-switch-network switch-to-mgmt-network \
        setup-mgmt-vlans teardown-mgmt-vlans setup-workstation-vlans teardown-workstation-vlans \
        verify backup update update-check check ping clean \
        deploy-network deploy-wireless deploy-dhcp deploy-firewall \
        packages batman-status logs \
        show-logs tail-logs clear-logs \
        uptime reboot restart-network restart-wireless install \
        usb-storage usb-status \
        deploy-monitoring monitoring-status monitoring-graphs monitoring-logs \
        syslog-view syslog-tail syslog-list syslog-capture \
        test-alert alert-status alert-logs alert-clear \
        repo-setup repo-setup-selective repo-start repo-status repo-clean \
        snapshot snapshot-all snapshot-diff \
        image-build image-build-all image-clean image-shell image-info \
        factory-reset sysupgrade \
        validate validate-smoke validate-full validate-cert validate-json validate-verbose \
        test test-quick test-wireless test-full test-destructive test-infrastructure

help:
	@echo "OpenWrt Mesh Network - Ansible Commands"
	@echo ""
	@echo "================================================================================"
	@echo "UNIFIED NODE OPERATIONS (Auto-detects Initial vs Production Phase)"
	@echo "================================================================================"
	@echo "These commands work for BOTH fresh nodes (192.168.1.1) and configured nodes"
	@echo "(10.11.12.x). The Makefile automatically detects which phase to use."
	@echo ""
	@echo "Check node connectivity:"
	@echo "  make check-node NODE=1          - Check Node 1 (auto-detects phase)"
	@echo "  make check-node NODE=2          - Check Node 2 (auto-detects phase)"
	@echo "  make check-node NODE=3          - Check Node 3 (auto-detects phase)"
	@echo "  make check-node NODE=1 VERBOSE=1 - Check Node 1 (verbose output)"
	@echo ""
	@echo "Deploy configuration to node:"
	@echo "  make deploy-node NODE=1         - Deploy to Node 1 (auto-detects phase)"
	@echo "  make deploy-node NODE=2         - Deploy to Node 2 (auto-detects phase)"
	@echo "  make deploy-node NODE=3         - Deploy to Node 3 (auto-detects phase)"
	@echo "  make deploy-node NODE=1 VERBOSE=1 - Deploy to Node 1 (verbose output)"
	@echo ""
	@echo "Audit node configuration:"
	@echo "  make audit-node NODE=1          - Audit Node 1 (auto-detects phase)"
	@echo "  make audit-node NODE=2          - Audit Node 2 (auto-detects phase)"
	@echo "  make audit-node NODE=3          - Audit Node 3 (auto-detects phase)"
	@echo "  make audit-node NODE=1 VERBOSE=1 - Audit Node 1 (verbose output)"
	@echo ""
	@echo "How phase auto-detection works:"
	@echo "  - Tries SSH to 10.11.12.x first (production mode)"
	@echo "  - If that fails, uses 192.168.1.1 (initial setup mode)"
	@echo "  - Initial setup mode automatically handles network switching"
	@echo ""
	@echo "================================================================================"
	@echo "ENVIRONMENT & SETUP"
	@echo "================================================================================"
	@echo "  make install                    - Check Ansible dependencies"
	@echo "  make validate-env               - Validate .env configuration (run first!)"
	@echo ""
	@echo "================================================================================"
	@echo "MULTI-NODE OPERATIONS (All Nodes at Once)"
	@echo "================================================================================"
	@echo "Use these AFTER all nodes are configured at their final IPs (10.11.12.x):"
	@echo ""
	@echo "  make check-all                  - Check connectivity to ALL nodes"
	@echo "  make audit                      - Audit ALL nodes"
	@echo "  make deploy                     - Deploy to ALL nodes"
	@echo "  make verify                     - Verify mesh status (all nodes)"
	@echo "  make backup                     - Backup all node configurations"
	@echo "  make update                     - Update packages on all nodes"
	@echo "  make update-check               - Check for available updates"
	@echo "  make ping                       - Test connectivity to all nodes"
	@echo ""
	@echo "================================================================================"
	@echo "MANUAL NETWORK SWITCHING"
	@echo "================================================================================"
	@echo "These are available for manual operations (deploy-node handles automatically):"
	@echo ""
	@echo "  make switch-to-initial-network  - Switch workstation to 192.168.1.100 (fresh nodes)"
	@echo "  make switch-to-mesh-network     - Switch workstation to 10.11.12.100 (deployed nodes)"
	@echo "  make switch-to-switch-network   - Switch workstation to 192.168.0.2 (factory TP-Link switches)"
	@echo "  make switch-to-mgmt-network     - Switch workstation to 10.11.10.100 (configured switches)"
	@echo ""
	@echo "  VLAN Trunk (enp5s0 on Switch A Port 5):"
	@echo "  make setup-mgmt-vlans           - Setup enp5s0 VLAN interfaces (access all networks)"
	@echo "  make teardown-mgmt-vlans        - Remove enp5s0 VLAN interfaces"
	@echo ""
	@echo "================================================================================"
	@echo "TARGETED DEPLOYMENTS (Deploy Specific Components Only)"
	@echo "================================================================================"
	@echo "  make deploy-network             - Deploy network config only"
	@echo "  make deploy-wireless            - Deploy wireless config only"
	@echo "  make deploy-dhcp                - Deploy DHCP config only"
	@echo "  make deploy-firewall            - Deploy firewall config only"
	@echo "  make packages                   - Install packages only"
	@echo ""
	@echo "================================================================================"
	@echo "USB STORAGE MANAGEMENT"
	@echo "================================================================================"
	@echo "  make usb-storage NODE=1         - Setup USB storage on Node 1 (FORMAT!)"
	@echo "  make usb-storage                - Setup USB storage on ALL nodes (FORMAT!)"
	@echo "  make usb-status NODE=1          - Check USB storage status on Node 1"
	@echo "  make usb-status                 - Check USB storage status on all nodes"
	@echo ""
	@echo "================================================================================"
	@echo "MONITORING (Requires USB Storage)"
	@echo "================================================================================"
	@echo "  make deploy-monitoring NODE=1   - Deploy collectd monitoring to Node 1"
	@echo "  make deploy-monitoring          - Deploy monitoring to ALL nodes"
	@echo "  make monitoring-status NODE=1   - Check monitoring status on Node 1"
	@echo "  make monitoring-status          - Check monitoring status on all nodes"
	@echo "  make monitoring-graphs NODE=1   - Open monitoring web UI for Node 1"
	@echo "  make monitoring-logs NODE=1     - View mesh health logs for Node 1"
	@echo ""
	@echo "================================================================================"
	@echo "DISTRIBUTED SYSLOG (Persistent Logs on USB)"
	@echo "================================================================================"
	@echo "  make syslog-view NODE=1         - View syslog summary for Node 1"
	@echo "  make syslog-view                - View syslog for all nodes"
	@echo "  make syslog-tail NODE=1         - Tail today's syslog for Node 1"
	@echo "  make syslog-list NODE=1         - List all syslog files for Node 1"
	@echo "  make syslog-capture NODE=1      - Manually trigger syslog capture"
	@echo ""
	@echo "================================================================================"
	@echo "TELEGRAM ALERTING (Instant Push Notifications)"
	@echo "================================================================================"
	@echo "  make test-alert NODE=1          - Manually trigger alert check for Node 1"
	@echo "  make alert-status NODE=1        - View alert status summary for Node 1"
	@echo "  make alert-logs NODE=1          - View full alert log for Node 1"
	@echo "  make alert-clear NODE=1         - Clear alert state for Node 1"
	@echo ""
	@echo "================================================================================"
	@echo "MONITORING & DEBUGGING"
	@echo "================================================================================"
	@echo "  make batman-status              - Check batman-adv mesh status"
	@echo "  make logs                       - Fetch recent logs from nodes"
	@echo "  make show-logs                  - Show last 100 lines of Ansible logs"
	@echo "  make tail-logs                  - Follow Ansible logs (live)"
	@echo "  make clear-logs                 - Clear Ansible log files"
	@echo ""
	@echo "================================================================================"
	@echo "SECURITY HARDENING & SCANNING"
	@echo "================================================================================"
	@echo "Security Validation:"
	@echo "  make security-audit             - Full security audit (10-phase scan)"
	@echo "  make security-check             - Quick security validation (6 checks)"
	@echo "  make deploy-security            - Deploy security hardening only"
	@echo ""
	@echo "Security Scanning (Kali Container):"
	@echo "  make vuln-scan                  - Network vulnerability scan (nmap, nikto, SSL)"
	@echo "  make wifi-scan                  - WiFi security scan (encryption, rogue AP)"
	@echo ""
	@echo "  Reports saved to:"
	@echo "    vuln-reports/vuln-scan-DATE.json"
	@echo "    wifi-reports/wifi-scan-DATE.json"
	@echo ""
	@echo "================================================================================"
	@echo "LOCAL PACKAGE REPOSITORY (Optional - faster deployments)"
	@echo "================================================================================"
	@echo "  make repo-setup                 - Download ALL packages (complete archive)"
	@echo "                                    Size: ~500 MB - 1 GB, Time: ~20-30 min"
	@echo "  make repo-setup-selective       - Download only .env packages (selective)"
	@echo "                                    Size: ~50-100 MB, Time: ~3-5 min"
	@echo "  make repo-start                 - Start local repository HTTP server"
	@echo "  make repo-status                - Check repository status and breakdown"
	@echo "  make repo-clean                 - Remove local repository cache"
	@echo ""
	@echo "  After setup, set OPKG_REPO_URL in .env and deploy normally"
	@echo "  Use repo-setup (full) for complete offline capability and updates"
	@echo "  See docs/LOCAL-PACKAGE-REPOSITORY.md for details"
	@echo ""
	@echo "================================================================================"
	@echo "CONFIGURATION SNAPSHOTS (Complete Node Documentation)"
	@echo "================================================================================"
	@echo "  make snapshot NODE=1            - Create full config snapshot for Node 1"
	@echo "  make snapshot-all               - Create snapshots for ALL nodes"
	@echo "  make snapshot-diff NODE=1       - Show changes since last snapshot"
	@echo ""
	@echo "  Output: snapshots/<hostname>/"
	@echo "    - Complete UCI configuration (machine-readable)"
	@echo "    - All /etc files (passwd, fstab, crontab, ssh keys)"
	@echo "    - Package list with versions"
	@echo "    - Custom scripts"
	@echo "    - Network, wireless, mesh state"
	@echo "    - Restore script and instructions"
	@echo ""
	@echo "================================================================================"
	@echo "CUSTOM FIRMWARE IMAGES (Build from Snapshots)"
	@echo "================================================================================"
	@echo "  make image-build NODE=1         - Build custom image for Node 1"
	@echo "  make image-build-all            - Build images for ALL nodes"
	@echo "  make image-info                 - Show Image Builder info/profiles"
	@echo "  make image-shell                - Enter Image Builder container shell"
	@echo "  make image-clean                - Remove built images"
	@echo ""
	@echo "  Prerequisites:"
	@echo "    - Node snapshot (make snapshot NODE=N)"
	@echo "    - Local package repo (make repo-setup)"
	@echo "    - Docker installed"
	@echo ""
	@echo "  Output: images/<hostname>-sysupgrade.bin"
	@echo "  See docs/IMAGE-BUILDER.md for flashing instructions"
	@echo ""
	@echo "================================================================================"
	@echo "FACTORY RESET (Restore Vanilla OpenWrt)"
	@echo "================================================================================"
	@echo "  make factory-reset NODE=1       - Reset Node 1 to factory defaults"
	@echo "  make factory-reset NODE=2       - Reset Node 2 to factory defaults"
	@echo "  make factory-reset NODE=3       - Reset Node 3 to factory defaults"
	@echo ""
	@echo "  This will:"
	@echo "    - Upload vanilla OpenWrt sysupgrade image"
	@echo "    - Run sysupgrade -n (erase all config)"
	@echo "    - Node reboots to 192.168.1.1 with no password"
	@echo ""
	@echo "  After reset, re-deploy with: make deploy-node NODE=X"
	@echo ""
	@echo "================================================================================"
	@echo "SYSUPGRADE (Flash Firmware Images)"
	@echo "================================================================================"
	@echo "  make sysupgrade NODE=1                    - Flash mesh image to Node 1"
	@echo "  make sysupgrade NODE=3 IMAGE_TYPE=mesh    - Flash custom mesh image (default)"
	@echo "  make sysupgrade NODE=3 IMAGE_TYPE=vanilla - Flash vanilla OpenWrt image"
	@echo ""
	@echo "  Image Types:"
	@echo "    mesh    - Custom-built image with config baked in (default)"
	@echo "              Node boots ready to go at 10.11.12.x"
	@echo "    vanilla - Stock OpenWrt image (same as factory-reset)"
	@echo "              Node boots to 192.168.1.1, needs deploy-node"
	@echo ""
	@echo "  Options:"
	@echo "    IMAGE_TYPE=mesh|vanilla       - Select image type"
	@echo "    IMAGE_PATH=/path/to/image     - Override with specific file"
	@echo ""
	@echo "  Works with both vanilla (192.168.1.1) and configured (10.11.12.x) nodes"
	@echo "  Config is ALWAYS wiped (sysupgrade -n)"
	@echo ""
	@echo "================================================================================"
	@echo "NETWORK VALIDATION (Unified Framework)"
	@echo "================================================================================"
	@echo "  make validate                   - Standard validation (~3min, recommended)"
	@echo "                                    Checks: connectivity, SSH, batman, VLANs"
	@echo "  make validate-smoke             - Quick smoke test (~30s)"
	@echo "                                    Checks: ping, SSH, batman module"
	@echo "  make validate-full              - Comprehensive validation (~10min)"
	@echo "                                    Checks: all above + services, security, WAN"
	@echo "  make validate-json              - Output JSON (for monitoring/CI)"
	@echo "  make validate-verbose           - Show detailed node-level results"
	@echo ""
	@echo "================================================================================"
	@echo "LIVE NETWORK TESTING (pytest-based)"
	@echo "================================================================================"
	@echo "  make test                       - Run standard live tests (recommended)"
	@echo "  make test-quick                 - Run quick connectivity tests only"
	@echo "  make test-wireless              - Run WiFi/wireless-specific tests"
	@echo "  make test-full                  - Run all tests with HTML report"
	@echo "  make test-infrastructure        - Test switches and infrastructure devices"
	@echo "                                    (Pings all switches, RPi, Proxmox nodes)"
	@echo "  make test-destructive           - Run destructive failover tests"
	@echo "                                    (CAUTION: temporarily disrupts network)"
	@echo ""
	@echo "  Test reports saved to: ../test-reports/"
	@echo ""
	@echo "================================================================================"
	@echo "ADVANCED OPERATIONS"
	@echo "================================================================================"
	@echo "  make check                      - Dry run deployment (no changes)"
	@echo "  make uptime                     - Show uptime for all nodes"
	@echo "  make reboot                     - Reboot all nodes"
	@echo "  make restart-network            - Restart network service on all nodes"
	@echo "  make restart-wireless           - Restart wireless service on all nodes"
	@echo "  make clean                      - Clean temporary files"
	@echo ""
	@echo "================================================================================"
	@echo "TYPICAL WORKFLOW"
	@echo "================================================================================"
	@echo "1. Validate environment:"
	@echo "     make validate-env"
	@echo ""
	@echo "2. Deploy nodes one at a time (connect ONE fresh node at a time):"
	@echo "     make deploy-node NODE=1    # Connect Node 1, deploy, disconnect"
	@echo "     make deploy-node NODE=2    # Connect Node 2, deploy, disconnect"
	@echo "     make deploy-node NODE=3    # Connect Node 3, deploy, disconnect"
	@echo ""
	@echo "3. After all nodes are deployed, verify mesh:"
	@echo "     make check-all             # Check all nodes are reachable"
	@echo "     make batman-status         # Verify mesh topology"
	@echo ""
	@echo "4. Make configuration changes and redeploy:"
	@echo "     make deploy                # Deploy to all nodes"
	@echo "     make verify                # Verify changes"
	@echo "================================================================================"

# ============================================================================
# PHASE 0: Environment Validation
# ============================================================================

validate-env:
	@echo "=== Validating environment configuration ==="
	@echo "Logging to: $(ANSIBLE_LOG)"
	@bash -c "$(ANSIBLE_CMD) playbooks/validate-env.yml"

# ============================================================================
# Unified Node Management (Auto-detects Initial vs Production Phase)
# ============================================================================

# Deploy to node (auto-detects deployment phase)
# Usage: make deploy-node NODE=1 [VERBOSE=1]
deploy-node:
ifndef NODE
	$(error NODE variable required. Usage: make deploy-node NODE=1)
endif
	@echo "=== Deploying to $(NODE_NAME) ==="
	@echo "Logging to: $(ANSIBLE_LOG)"
	@echo "Checking node status..."
	@bash -c "set -a && source $(ENV_FILE) && set +a && \
	if ssh -o ConnectTimeout=2 -o StrictHostKeyChecking=no -i \$$SSH_KEY_PATH root@$(NODE_IP_PROD) 'echo Node is configured' 2>/dev/null; then \
		echo 'Node found at $(NODE_IP_PROD) (production mode)'; \
		echo 'Running production deployment...'; \
		$(ANSIBLE_CMD) -i $(INVENTORY_PROD) playbooks/deploy.yml --limit $(NODE_NAME) $(VERBOSE_FLAG); \
	else \
		echo 'Node not found at $(NODE_IP_PROD), using initial setup mode (192.168.1.1)'; \
		echo 'Switching workstation to initial network...'; \
		$(ANSIBLE_CMD) playbooks/switch-to-initial-network.yml && \
		echo 'Deploying to $(NODE_NAME) at 192.168.1.1...' && \
		$(ANSIBLE_CMD) -i $(INVENTORY_INITIAL) playbooks/deploy.yml --limit $(NODE_NAME) $(VERBOSE_FLAG) && \
		echo 'Switching workstation back to mesh network...' && \
		$(ANSIBLE_CMD) playbooks/switch-to-mesh-network.yml; \
	fi"
	@echo "=== Deployment complete for $(NODE_NAME) ==="

# Check node connectivity (auto-detects deployment phase)
# Usage: make check-node NODE=1 [VERBOSE=1]
check-node:
ifndef NODE
	$(error NODE variable required. Usage: make check-node NODE=1)
endif
	@echo "=== Checking connectivity to $(NODE_NAME) ==="
	@echo "Logging to: $(ANSIBLE_LOG)"
	@bash -c "set -a && source $(ENV_FILE) && set +a && \
	if ssh -o ConnectTimeout=2 -o StrictHostKeyChecking=no -i \$$SSH_KEY_PATH root@$(NODE_IP_PROD) 'echo Node is configured' 2>/dev/null; then \
		echo 'Node found at $(NODE_IP_PROD) (production mode)'; \
		$(ANSIBLE_CMD) -i $(INVENTORY_PROD) playbooks/check-connectivity.yml --limit $(NODE_NAME) $(VERBOSE_FLAG); \
	else \
		echo 'Node not configured yet, checking at 192.168.1.1 (initial mode)'; \
		$(ANSIBLE_CMD) -i $(INVENTORY_INITIAL) playbooks/check-connectivity.yml --limit $(NODE_NAME) $(VERBOSE_FLAG); \
	fi"

# Audit node configuration (auto-detects deployment phase)
# Usage: make audit-node NODE=1 [VERBOSE=1]
audit-node:
ifndef NODE
	$(error NODE variable required. Usage: make audit-node NODE=1)
endif
	@echo "=== Auditing $(NODE_NAME) ==="
	@echo "Logging to: $(ANSIBLE_LOG)"
	@bash -c "set -a && source $(ENV_FILE) && set +a && \
	if ssh -o ConnectTimeout=2 -o StrictHostKeyChecking=no -i \$$SSH_KEY_PATH root@$(NODE_IP_PROD) 'echo Node is configured' 2>/dev/null; then \
		echo 'Node found at $(NODE_IP_PROD) (production mode)'; \
		echo 'Switching workstation to mesh network...'; \
		$(ANSIBLE_CMD) playbooks/switch-to-mesh-network.yml && \
		echo 'Auditing $(NODE_NAME) at $(NODE_IP_PROD)...' && \
		$(ANSIBLE_CMD) -i $(INVENTORY_PROD) playbooks/audit.yml --limit $(NODE_NAME) $(VERBOSE_FLAG); \
	else \
		echo 'Node not found at $(NODE_IP_PROD), using initial setup mode (192.168.1.1)'; \
		echo 'Switching workstation to initial network...'; \
		$(ANSIBLE_CMD) playbooks/switch-to-initial-network.yml && \
		echo 'Auditing $(NODE_NAME) at 192.168.1.1...' && \
		$(ANSIBLE_CMD) -i $(INVENTORY_INITIAL) playbooks/audit.yml --limit $(NODE_NAME) $(VERBOSE_FLAG) && \
		echo 'Switching workstation back to mesh network...' && \
		$(ANSIBLE_CMD) playbooks/switch-to-mesh-network.yml; \
	fi"

# ============================================================================
# USB Storage Management
# ============================================================================

# Configure USB storage on node(s) with F2FS filesystem
# Usage: make usb-storage NODE=1 [VERBOSE=1]
#        make usb-storage (for all nodes)
usb-storage:
ifdef NODE
	@echo "=== Configuring USB storage on $(NODE_NAME) ==="
	@echo "WARNING: This will FORMAT the USB drive on $(NODE_NAME)!"
	@read -p "Are you sure? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		echo "Logging to: $(ANSIBLE_LOG)"; \
		bash -c "set -a && source $(ENV_FILE) && set +a && \
		if ssh -o ConnectTimeout=2 -o StrictHostKeyChecking=no -i \$$SSH_KEY_PATH root@$(NODE_IP_PROD) 'echo Node is configured' 2>/dev/null; then \
			echo 'Node found at $(NODE_IP_PROD) (production mode)'; \
			$(ANSIBLE_CMD) -i $(INVENTORY_PROD) playbooks/usb-storage.yml --limit $(NODE_NAME) $(VERBOSE_FLAG); \
		else \
			echo 'Node not found at $(NODE_IP_PROD), cannot configure USB storage'; \
			echo 'Please deploy node first with: make deploy-node NODE=$(NODE)'; \
			exit 1; \
		fi"; \
	else \
		echo "Operation cancelled"; \
	fi
else
	@echo "=== Configuring USB storage on ALL nodes ==="
	@echo "WARNING: This will FORMAT USB drives on ALL nodes!"
	@read -p "Are you sure? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		echo "Logging to: $(ANSIBLE_LOG)"; \
		bash -c "$(ANSIBLE_CMD) -i $(INVENTORY_PROD) playbooks/usb-storage.yml"; \
	else \
		echo "Operation cancelled"; \
	fi
endif

# Check USB storage status
# Usage: make usb-status NODE=1
#        make usb-status (for all nodes)
usb-status:
ifdef NODE
	@echo "=== Checking USB storage on $(NODE_NAME) ==="
	@bash -c "set -a && source $(ENV_FILE) && set +a && \
	ansible $(NODE_NAME) -i $(INVENTORY_PROD) -m raw -a 'echo \"=== USB Storage Status for \$$(hostname) ===\"; \
	echo \"\"; \
	echo \"--- USB Devices Detected ---\"; \
	if ls /dev/sd[a-z] 2>/dev/null | grep -q sd; then \
		for dev in /dev/sd[a-z]; do \
			[ -b \"\$$dev\" ] && echo \"Found: \$$dev (\$$(fdisk -l \$$dev 2>/dev/null | grep \"^Disk /dev\" | cut -d\" \" -f3-4))\"; \
		done; \
		echo \"\"; \
		echo \"--- USB Bus Information ---\"; \
		lsusb 2>/dev/null | grep -v \"root hub\" || dmesg | grep -i \"usb.*storage\" | tail -5; \
	else \
		echo \"No USB storage devices detected at /dev/sd*\"; \
		echo \"\"; \
		echo \"--- Checking USB Modules ---\"; \
		lsmod | grep -E \"usb_storage|uas\" || echo \"USB storage modules not loaded\"; \
	fi; \
	echo \"\"; \
	echo \"--- Mount Point /x00 Status ---\"; \
	if mount | grep -q \"/x00\"; then \
		mount | grep /x00; \
		echo \"\"; \
		df -h /x00; \
		echo \"\"; \
		echo \"Contents: \$$(ls -la /x00 2>/dev/null | wc -l) items\"; \
	else \
		echo \"Not mounted at /x00\"; \
		[ -d /x00 ] && echo \"Mount point exists but not mounted\" || echo \"Mount point /x00 does not exist\"; \
	fi; \
	echo \"\"; \
	echo \"--- Auto-mount Configuration ---\"; \
	uci show fstab 2>/dev/null | grep -A3 \"target=./x00\" || echo \"No auto-mount configured for /x00\"'"
else
	@echo "=== Checking USB storage on all nodes ==="
	@bash -c "set -a && source $(ENV_FILE) && set +a && \
	ansible mesh_nodes -i $(INVENTORY_PROD) -m raw -a 'echo \"=== Node: \$$(hostname) ===\"; \
	if ls /dev/sd[a-z] 2>/dev/null | grep -q sd; then \
		echo \"USB device found\"; \
		df -h /x00 2>/dev/null || echo \"Not mounted at /x00\"; \
	else \
		echo \"No USB storage detected\"; \
	fi; \
	echo \"\"'"
endif

# ============================================================================
# Monitoring Management
# ============================================================================

# Deploy monitoring (collectd + vnstat) to nodes
# REQUIRES: USB storage must be mounted at /x00
# Usage: make deploy-monitoring NODE=1
#        make deploy-monitoring (for all nodes)
deploy-monitoring:
ifdef NODE
	@echo "=== Deploying monitoring to $(NODE_NAME) ==="
	@echo "Logging to: $(ANSIBLE_LOG)"
	@bash -c "set -a && source $(ENV_FILE) && set +a && \
	if ssh -o ConnectTimeout=2 -o StrictHostKeyChecking=no -i \$$SSH_KEY_PATH root@$(NODE_IP_PROD) 'mount | grep -q /x00' 2>/dev/null; then \
		echo 'USB storage detected at /x00 - proceeding with monitoring deployment'; \
		$(ANSIBLE_CMD) -i $(INVENTORY_PROD) playbooks/monitoring.yml --limit $(NODE_NAME) $(VERBOSE_FLAG); \
	else \
		echo 'ERROR: USB storage not mounted at /x00 on $(NODE_NAME)'; \
		echo 'Please run: make usb-storage NODE=$(NODE) first'; \
		exit 1; \
	fi"
else
	@echo "=== Deploying monitoring to ALL nodes ==="
	@echo "Logging to: $(ANSIBLE_LOG)"
	@bash -c "$(ANSIBLE_CMD) -i $(INVENTORY_PROD) playbooks/monitoring.yml"
endif

# Check monitoring status
# Usage: make monitoring-status NODE=1
#        make monitoring-status (for all nodes)
monitoring-status:
ifdef NODE
	@echo "=== Checking monitoring status on $(NODE_NAME) ==="
	@bash -c "set -a && source $(ENV_FILE) && set +a && \
	ansible $(NODE_NAME) -i $(INVENTORY_PROD) -m raw -a '/usr/bin/monitoring-report.sh 2>/dev/null || echo \"Monitoring not deployed\"'"
else
	@echo "=== Checking monitoring status on all nodes ==="
	@bash -c "set -a && source $(ENV_FILE) && set +a && \
	ansible mesh_nodes -i $(INVENTORY_PROD) -m raw -a 'echo \"=== \$$(hostname) ===\"; \
	if [ -f /usr/bin/monitoring-report.sh ]; then \
		echo \"Collectd: \$$(/etc/init.d/collectd status 2>&1 | head -1)\"; \
		echo \"vnStat: \$$(/etc/init.d/vnstat status 2>&1 | head -1)\"; \
		echo \"Data: \$$(du -sh /x00/monitoring 2>/dev/null | cut -f1 || echo \"No data\")\"; \
	else \
		echo \"Not deployed\"; \
	fi; \
	echo \"\"'"
endif

# View monitoring data/graphs
# Usage: make monitoring-graphs NODE=1
monitoring-graphs:
ifndef NODE
	$(error NODE variable required. Usage: make monitoring-graphs NODE=1)
endif
	@echo "=== Monitoring Web Interface for $(NODE_NAME) ==="
	@echo "Opening: http://$(NODE_IP_PROD)/cgi-bin/luci/admin/statistics/graph"
	@which xdg-open >/dev/null 2>&1 && xdg-open "http://$(NODE_IP_PROD)/cgi-bin/luci/admin/statistics/graph" || \
	echo "Please open in browser: http://$(NODE_IP_PROD)/cgi-bin/luci/admin/statistics/graph"

# View mesh health logs
# Usage: make monitoring-logs NODE=1
monitoring-logs:
ifndef NODE
	$(error NODE variable required. Usage: make monitoring-logs NODE=1)
endif
	@echo "=== Mesh health logs for $(NODE_NAME) ==="
	@bash -c "set -a && source $(ENV_FILE) && set +a && \
	ansible $(NODE_NAME) -i $(INVENTORY_PROD) -m raw -a 'tail -50 /x00/monitoring/logs/mesh-health.log 2>/dev/null || echo \"No logs found\"'"

# View distributed syslog (persistent logs on USB)
# Usage: make syslog-view NODE=1
#        make syslog-view (for all nodes)
syslog-view:
ifdef NODE
	@echo "=== Viewing syslog for $(NODE_NAME) ==="
	@bash -c "set -a && source $(ENV_FILE) && set +a && \
	ansible $(NODE_NAME) -i $(INVENTORY_PROD) -m raw -a '/usr/bin/syslog-view.sh 2>/dev/null || echo \"Syslog not configured\"'"
else
	@echo "=== Viewing syslog for all nodes ==="
	@bash -c "set -a && source $(ENV_FILE) && set +a && \
	ansible mesh_nodes -i $(INVENTORY_PROD) -m raw -a '/usr/bin/syslog-view.sh 2>/dev/null || echo \"Syslog not configured\"'"
endif

# View today's syslog entries (tail)
# Usage: make syslog-tail NODE=1
syslog-tail:
ifndef NODE
	$(error NODE variable required. Usage: make syslog-tail NODE=1)
endif
	@echo "=== Tailing today's syslog for $(NODE_NAME) ==="
	@bash -c "set -a && source $(ENV_FILE) && set +a && \
	ansible $(NODE_NAME) -i $(INVENTORY_PROD) -m raw -a 'HOSTNAME=\$$(uci -q get system.@system[0].hostname || hostname); tail -50 /x00/logs/\$$HOSTNAME-\$$(date +%Y-%m-%d).log 2>/dev/null || echo \"No log file for today\"'"

# List all syslog files
# Usage: make syslog-list NODE=1
syslog-list:
ifndef NODE
	$(error NODE variable required. Usage: make syslog-list NODE=1)
endif
	@echo "=== Listing syslog files for $(NODE_NAME) ==="
	@bash -c "set -a && source $(ENV_FILE) && set +a && \
	ansible $(NODE_NAME) -i $(INVENTORY_PROD) -m raw -a 'ls -lh /x00/logs/*.log 2>/dev/null || echo \"No log files found\"'"

# Manually trigger syslog capture
# Usage: make syslog-capture NODE=1
syslog-capture:
ifndef NODE
	$(error NODE variable required. Usage: make syslog-capture NODE=1)
endif
	@echo "=== Capturing syslog for $(NODE_NAME) ==="
	@bash -c "set -a && source $(ENV_FILE) && set +a && \
	ansible $(NODE_NAME) -i $(INVENTORY_PROD) -m raw -a '/usr/bin/syslog-capture.sh && echo \"Syslog captured to /x00/logs/\"'"

# ============================================================================
# Telegram Alerting Management
# ============================================================================

# Manually trigger alert check
# Usage: make test-alert NODE=1
test-alert:
ifndef NODE
	$(error NODE variable required. Usage: make test-alert NODE=1)
endif
	@echo "=== Running alert check on $(NODE_NAME) ==="
	@bash -c "set -a && source $(ENV_FILE) && set +a && \
	ansible $(NODE_NAME) -i $(INVENTORY_PROD) -m raw -a '/usr/bin/telegram-alert.sh 2>/dev/null || echo \"Telegram alerting not configured\"'"

# View alert status summary
# Usage: make alert-status NODE=1
alert-status:
ifndef NODE
	$(error NODE variable required. Usage: make alert-status NODE=1)
endif
	@echo "=== Alert status for $(NODE_NAME) ==="
	@bash -c "set -a && source $(ENV_FILE) && set +a && \
	ansible $(NODE_NAME) -i $(INVENTORY_PROD) -m raw -a 'echo \"=== Alert Configuration ===\"; \
	if [ -f /usr/bin/telegram-alert.sh ]; then \
		echo \"✓ Telegram alerting configured\"; \
		echo \"\"; \
		echo \"=== Cron Job ===\"; \
		crontab -l | grep telegram-alert || echo \"No cron job found\"; \
		echo \"\"; \
		echo \"=== Alert State ===\"; \
		if [ -f /tmp/alert-state.txt ]; then \
			cat /tmp/alert-state.txt; \
		else \
			echo \"No active alerts\"; \
		fi; \
		echo \"\"; \
		echo \"=== Recent Alerts (last 10) ===\"; \
		if [ -f /x00/logs/alerts-sent.log ]; then \
			tail -10 /x00/logs/alerts-sent.log; \
		else \
			echo \"No alerts sent yet\"; \
		fi; \
	else \
		echo \"✗ Telegram alerting not configured\"; \
	fi'"

# View full alert log
# Usage: make alert-logs NODE=1
alert-logs:
ifndef NODE
	$(error NODE variable required. Usage: make alert-logs NODE=1)
endif
	@echo "=== Alert logs for $(NODE_NAME) ==="
	@bash -c "set -a && source $(ENV_FILE) && set +a && \
	ansible $(NODE_NAME) -i $(INVENTORY_PROD) -m raw -a 'if [ -f /x00/logs/alerts-sent.log ]; then \
		cat /x00/logs/alerts-sent.log; \
	else \
		echo \"No alert log found - either alerting not configured or no alerts sent yet\"; \
	fi'"

# Clear alert state
# Usage: make alert-clear NODE=1
alert-clear:
ifndef NODE
	$(error NODE variable required. Usage: make alert-clear NODE=1)
endif
	@echo "=== Clearing alert state for $(NODE_NAME) ==="
	@bash -c "set -a && source $(ENV_FILE) && set +a && \
	ansible $(NODE_NAME) -i $(INVENTORY_PROD) -m raw -a 'if [ -f /tmp/alert-state.txt ]; then \
		rm /tmp/alert-state.txt; \
		echo \"Alert state cleared - next run will send fresh alerts\"; \
	else \
		echo \"No alert state to clear\"; \
	fi'"

# ============================================================================
# Network Switching (Manual Operations)
# ============================================================================
# These targets are available for manual network switching if needed
# (The unified deploy-node target handles this automatically)

switch-to-initial-network:
	@bash -c "$(ANSIBLE_CMD) playbooks/switch-to-initial-network.yml"

switch-to-mesh-network:
	@bash -c "$(ANSIBLE_CMD) playbooks/switch-to-mesh-network.yml"

switch-to-switch-network:
	@bash -c "$(ANSIBLE_CMD) playbooks/switch-to-switch-network.yml"

switch-to-mgmt-network:
	@bash -c "$(ANSIBLE_CMD) playbooks/switch-to-mgmt-network.yml"

# Setup VLAN interfaces on enp5s0 for management workstation trunk port
# This configures enp5s0 with tagged VLAN sub-interfaces for access to all networks:
#   - enp5s0 (untagged): Switch management (10.11.10.101/32) - TL-SG108E only responds on untagged
#   - enp5s0.10: Management network (10.11.10.100/24) - mesh nodes, infrastructure
#   - enp5s0.30: IoT network (10.11.30.100/24) - IoT devices
#   - enp5s0.200: LAN/Client network (10.11.12.100/24) - client devices
# Requires: enp5s0 connected to Switch A Port 5 (trunk with all VLANs tagged)
setup-mgmt-vlans setup-workstation-vlans:
	@echo "=== Setting up VLAN interfaces on enp5s0 ==="
	@echo "Logging to: $(ANSIBLE_LOG)"
	@bash -c "$(ANSIBLE_CMD) playbooks/setup-workstation-vlans.yml"

# Remove VLAN interfaces from enp5s0
teardown-mgmt-vlans teardown-workstation-vlans:
	@echo "=== Removing VLAN interfaces from enp5s0 ==="
	@echo "Logging to: $(ANSIBLE_LOG)"
	@bash -c "$(ANSIBLE_CMD) playbooks/teardown-workstation-vlans.yml"

# ============================================================================
# Multi-Node Operations (All Nodes at Once)
# ============================================================================
# Use these targets AFTER all nodes are configured and at their final IPs

# Check connectivity to all nodes
check-all:
	@echo "=== Checking connectivity to all nodes ==="
	@echo "Logging to: $(ANSIBLE_LOG)"
	@bash -c "$(ANSIBLE_CMD) playbooks/check-connectivity.yml"

# Backwards compatibility alias
check-connectivity: check-all

# Audit nodes (respects NODE variable if set)
audit:
ifdef NODE
	@echo "=== Auditing $(NODE_NAME) ==="
	@echo "Logging to: $(ANSIBLE_LOG)"
	@bash -c "$(ANSIBLE_CMD) playbooks/audit.yml --limit $(NODE_NAME)"
else
	@echo "=== Auditing all nodes ==="
	@echo "Logging to: $(ANSIBLE_LOG)"
	@bash -c "$(ANSIBLE_CMD) playbooks/audit.yml"
endif

# Vulnerability scan using Kali container
vuln-scan:
	@echo "=== Running Vulnerability Scan via Kali Container ==="
	@echo "Logging to: $(ANSIBLE_LOG)"
	@bash -c "$(ANSIBLE_CMD) playbooks/vulnerability_scan.yml"

# WiFi security scan using Kali container
wifi-scan:
	@echo "=== Running WiFi Security Scan via Kali Container ==="
	@echo "Logging to: $(ANSIBLE_LOG)"
	@bash -c "$(ANSIBLE_CMD) playbooks/wifi_security_scan.yml"

# ============================================================================
# Security Hardening Operations
# ============================================================================

# Full security audit (10-phase comprehensive scan)
# Usage: make security-audit
#        make security-audit NODE=1
security-audit:
ifdef NODE
	@echo "=== Running Security Audit on $(NODE_NAME) ==="
	@echo "Logging to: $(ANSIBLE_LOG)"
	@bash -c "$(ANSIBLE_CMD) -i $(INVENTORY_PROD) playbooks/security_audit.yml --limit $(NODE_NAME) $(VERBOSE_FLAG)"
else
	@echo "=== Running Security Audit on all nodes ==="
	@echo "Logging to: $(ANSIBLE_LOG)"
	@bash -c "$(ANSIBLE_CMD) -i $(INVENTORY_PROD) playbooks/security_audit.yml"
endif

# Quick security validation (6 checks)
# Usage: make security-check
#        make security-check NODE=1
security-check:
ifdef NODE
	@echo "=== Running Security Check on $(NODE_NAME) ==="
	@echo "Logging to: $(ANSIBLE_LOG)"
	@bash -c "$(ANSIBLE_CMD) -i $(INVENTORY_PROD) playbooks/security_check.yml --limit $(NODE_NAME) $(VERBOSE_FLAG)"
else
	@echo "=== Running Security Check on all nodes ==="
	@echo "Logging to: $(ANSIBLE_LOG)"
	@bash -c "$(ANSIBLE_CMD) -i $(INVENTORY_PROD) playbooks/security_check.yml"
endif

# Deploy security hardening only (without full deployment)
# Usage: make deploy-security
#        make deploy-security NODE=1
deploy-security:
ifdef NODE
	@echo "=== Deploying Security Hardening to $(NODE_NAME) ==="
	@echo "Logging to: $(ANSIBLE_LOG)"
	@bash -c "$(ANSIBLE_CMD) -i $(INVENTORY_PROD) playbooks/deploy.yml --tags security --limit $(NODE_NAME) $(VERBOSE_FLAG)"
else
	@echo "=== Deploying Security Hardening to all nodes ==="
	@echo "Logging to: $(ANSIBLE_LOG)"
	@bash -c "$(ANSIBLE_CMD) -i $(INVENTORY_PROD) playbooks/deploy.yml --tags security"
endif

# Deploy to all nodes
deploy:
	@echo "=== Deploying to all nodes ==="
	@echo "Logging to: $(ANSIBLE_LOG)"
	@bash -c "$(ANSIBLE_CMD) playbooks/deploy.yml"

verify:
	@bash -c "$(ANSIBLE_CMD) playbooks/verify.yml"

backup:
	@bash -c "$(ANSIBLE_CMD) playbooks/backup.yml"

update:
	@bash -c "$(ANSIBLE_CMD) playbooks/update.yml"

update-check:
	@bash -c "$(ANSIBLE_CMD) playbooks/update.yml --tags check"

check:
	@bash -c "$(ANSIBLE_CMD) playbooks/deploy.yml --check"

ping:
	ansible mesh_nodes -m ping

clean:
	find . -name "*.retry" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

# Network-specific deployments
deploy-network:
	@bash -c "$(ANSIBLE_CMD) playbooks/deploy.yml --tags network"

deploy-wireless:
	@bash -c "$(ANSIBLE_CMD) playbooks/deploy.yml --tags wireless"

deploy-dhcp:
	@bash -c "$(ANSIBLE_CMD) playbooks/deploy.yml --tags dhcp"

deploy-firewall:
	@bash -c "$(ANSIBLE_CMD) playbooks/deploy.yml --tags firewall"

# Package management
packages:
	@bash -c "$(ANSIBLE_CMD) playbooks/deploy.yml --tags packages"

# Advanced operations
batman-status:
	@echo "=== Batman Interfaces ==="
	@ansible mesh_nodes -a "batctl if"
	@echo ""
	@echo "=== Batman Originators ==="
	@ansible mesh_nodes -a "batctl o"
	@echo ""
	@echo "=== Gateway Status ==="
	@ansible mesh_nodes -a "batctl gwl"

logs:
	ansible mesh_nodes -a "logread | tail -50"

# Show local Ansible logs
show-logs:
	@if [ -f logs/ansible.log ]; then \
		tail -100 logs/ansible.log; \
	else \
		echo "No log file found at logs/ansible.log"; \
		echo "Logs will be created after first playbook run"; \
	fi

# Tail Ansible logs (follow)
tail-logs:
	@if [ -f logs/ansible.log ]; then \
		tail -f logs/ansible.log; \
	else \
		echo "No log file found at logs/ansible.log"; \
		echo "Logs will be created after first playbook run"; \
	fi

# Clear Ansible logs
clear-logs:
	@if [ -f logs/ansible.log ]; then \
		rm logs/ansible.log; \
		echo "Cleared ansible.log"; \
	else \
		echo "No log file to clear"; \
	fi

uptime:
	ansible mesh_nodes -a "uptime"

reboot:
	ansible mesh_nodes -a "reboot"
	@echo "Waiting for nodes to reboot..."
	@sleep 60
	@make ping

restart-network:
	ansible mesh_nodes -a "/etc/init.d/network restart"

restart-wireless:
	ansible mesh_nodes -a "wifi reload"

# Installation target for first-time setup
install:
	@echo "Installing Ansible dependencies..."
	@which ansible > /dev/null || (echo "Please install Ansible first" && exit 1)
	@echo "Ansible found: $$(ansible --version | head -1)"
	@echo ""
	@echo "Setup complete! Next steps:"
	@echo "1. Edit group_vars/all.yml with your passwords"
	@echo "2. Edit inventory/hosts.yml with correct IPs"
	@echo "3. Run: make deploy-node1"

# ============================================================================
# Local Package Repository Management
# ============================================================================

# Setup local package repository (full archive - all packages)
repo-setup:
	@echo "=== Setting up local OpenWrt package repository (FULL ARCHIVE) ==="
	@echo "This will download ALL packages from all feeds (~500 MB - 1 GB)"
	@echo ""
	@./scripts/setup-local-repo.sh

# Setup local package repository (selective - only .env packages)
repo-setup-selective:
	@echo "=== Setting up local OpenWrt package repository (SELECTIVE) ==="
	@echo "This will download only packages listed in .env (~50-100 MB)"
	@echo ""
	@./scripts/setup-local-repo.sh --selective

# Start local repository HTTP server
repo-start:
	@echo "=== Starting local repository server ==="
	@echo "Press Ctrl+C to stop"
	@./scripts/start-local-repo.sh

# Check repository status
repo-status:
	@if [ -d openwrt-repo ]; then \
		echo "=== Local Repository Status ==="; \
		echo ""; \
		echo "Location: $(PWD)/openwrt-repo"; \
		echo "Total size: $$(du -sh openwrt-repo | cut -f1)"; \
		echo ""; \
		echo "Package Breakdown:"; \
		for feed in base luci packages routing telephony; do \
			count=$$(find openwrt-repo/packages -path "*/$$feed/*.ipk" 2>/dev/null | wc -l); \
			size=$$(du -sh openwrt-repo/packages/*/mipsel_24kc/$$feed 2>/dev/null | cut -f1 | head -1); \
			[ -z "$$size" ] && size="0"; \
			printf "  %-12s %4d packages  %s\n" "$$feed:" "$$count" "$$size"; \
		done; \
		total=$$(find openwrt-repo/packages -name '*.ipk' 2>/dev/null | wc -l); \
		echo "  ────────────────────────────────"; \
		printf "  %-12s %4d packages total\n" "TOTAL:" "$$total"; \
		echo ""; \
		echo "Firmware Images: $$(find openwrt-repo/targets -name '*.bin' 2>/dev/null | wc -l) cached"; \
		echo ""; \
		if [ -n "$$(lsof -ti:8080 2>/dev/null)" ]; then \
			echo "Server: Running on port 8080"; \
			LOCAL_IP=$$(ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1' | head -1); \
			echo "URL: http://$$LOCAL_IP:8080"; \
		else \
			echo "Server: Not running (use 'make repo-start')"; \
		fi; \
		echo ""; \
		if [ -n "$$(grep '^OPKG_REPO_URL=' ../.env | grep -v '^OPKG_REPO_URL=$$')" ]; then \
			echo "Configuration: Enabled in .env"; \
			grep '^OPKG_REPO_URL=' ../.env; \
		else \
			echo "Configuration: Not enabled (set OPKG_REPO_URL in .env)"; \
		fi; \
	else \
		echo "Local repository not set up"; \
		echo "Run: make repo-setup"; \
	fi

# Clean local repository
repo-clean:
	@echo "=== Removing local repository ==="
	@if [ -d openwrt-repo ]; then \
		SIZE=$$(du -sh openwrt-repo | cut -f1); \
		read -p "Remove openwrt-repo/ ($$SIZE)? [y/N]: " confirm; \
		if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
			rm -rf openwrt-repo; \
			echo "Repository removed"; \
		else \
			echo "Cancelled"; \
		fi; \
	else \
		echo "Repository does not exist"; \
	fi

# ============================================================================
# Configuration Snapshots
# ============================================================================
# Create complete filesystem snapshots - downloads entire overlay from node
# This captures ALL changes from factory default including /etc, /root, etc.

# Create snapshot for single node
# Usage: make snapshot NODE=1
snapshot:
ifndef NODE
	$(error NODE variable required. Usage: make snapshot NODE=1)
endif
	@echo "=== Creating full filesystem snapshot for $(NODE_NAME) ==="
	@echo "Logging to: $(ANSIBLE_LOG)"
	@bash -c "set -a && source $(ENV_FILE) && set +a && \
	if ssh -o ConnectTimeout=2 -o StrictHostKeyChecking=no -i \$$SSH_KEY_PATH root@$(NODE_IP_PROD) 'echo Node is configured' 2>/dev/null; then \
		echo 'Node found at $(NODE_IP_PROD)'; \
		$(ANSIBLE_CMD) -i $(INVENTORY_PROD) playbooks/snapshot-full.yml --limit $(NODE_NAME) $(VERBOSE_FLAG); \
	else \
		echo 'ERROR: Node not reachable at $(NODE_IP_PROD)'; \
		echo 'Snapshots can only be created for deployed nodes.'; \
		exit 1; \
	fi"
	@echo ""
	@echo "=== Snapshot complete ==="
	@echo "Location: snapshots/"
	@ls -la snapshots/ 2>/dev/null || true

# Create snapshots for all nodes
# Usage: make snapshot-all
snapshot-all:
	@echo "=== Creating full filesystem snapshots for ALL nodes ==="
	@echo "Logging to: $(ANSIBLE_LOG)"
	@bash -c "$(ANSIBLE_CMD) -i $(INVENTORY_PROD) playbooks/snapshot-full.yml"
	@echo ""
	@echo "=== All snapshots complete ==="
	@echo "Locations:"
	@ls -d snapshots/*/ 2>/dev/null || echo "No snapshots found"

# Show changes since last snapshot (diff)
# Usage: make snapshot-diff NODE=1
snapshot-diff:
ifndef NODE
	$(error NODE variable required. Usage: make snapshot-diff NODE=1)
endif
	@echo "=== Comparing current config to last snapshot for $(NODE_NAME) ==="
	@bash -c "set -a && source $(ENV_FILE) && set +a && \
	HOSTNAME=\$$(ssh -o ConnectTimeout=2 -o StrictHostKeyChecking=no -i \$$SSH_KEY_PATH root@$(NODE_IP_PROD) \
		'uci -q get system.@system[0].hostname || hostname' 2>/dev/null); \
	if [ -z \"\$$HOSTNAME\" ]; then \
		echo 'ERROR: Cannot reach node at $(NODE_IP_PROD)'; \
		exit 1; \
	fi; \
	SNAPSHOT_DIR=\"snapshots/\$$HOSTNAME\"; \
	if [ ! -d \"\$$SNAPSHOT_DIR\" ]; then \
		echo 'No snapshot found for '\$$HOSTNAME; \
		echo 'Create one first: make snapshot NODE=$(NODE)'; \
		exit 1; \
	fi; \
	echo 'Comparing against: '\$$SNAPSHOT_DIR; \
	echo ''; \
	echo '=== UCI Configuration Changes ==='; \
	CURRENT_UCI=\$$(mktemp); \
	ssh -o StrictHostKeyChecking=no -i \$$SSH_KEY_PATH root@$(NODE_IP_PROD) 'uci export' > \$$CURRENT_UCI 2>/dev/null; \
	diff -u \"\$$SNAPSHOT_DIR/config/uci_export.txt\" \$$CURRENT_UCI || echo '(no changes)'; \
	rm -f \$$CURRENT_UCI; \
	echo ''; \
	echo '=== Package Changes ==='; \
	CURRENT_PKGS=\$$(mktemp); \
	ssh -o StrictHostKeyChecking=no -i \$$SSH_KEY_PATH root@$(NODE_IP_PROD) 'opkg list-installed | awk \"{print \\\$$1}\"' > \$$CURRENT_PKGS 2>/dev/null; \
	diff -u \"\$$SNAPSHOT_DIR/packages/installed.txt\" \$$CURRENT_PKGS || echo '(no changes)'; \
	rm -f \$$CURRENT_PKGS"

# ============================================================================
# Custom Firmware Image Building
# ============================================================================
# Build custom OpenWrt firmware images from node snapshots using the
# OpenWrt Image Builder in Docker. Images include all packages and
# UCI configuration baked in for instant deployment.

# Docker compose command for image builder
IMAGEBUILDER_DIR := docker/imagebuilder
IMAGEBUILDER_COMPOSE := docker compose -f $(IMAGEBUILDER_DIR)/docker-compose.yml

# Build image for single node
# Usage: make image-build NODE=1
image-build:
ifndef NODE
	$(error NODE variable required. Usage: make image-build NODE=1)
endif
	@echo "=== Building custom firmware image for $(NODE_NAME) ==="
	@if [ ! -d "snapshots/mesh-node$(NODE)" ]; then \
		echo "ERROR: Snapshot not found for mesh-node$(NODE)"; \
		echo "Create one first: make snapshot NODE=$(NODE)"; \
		exit 1; \
	fi
	@if [ ! -d "openwrt-repo/packages" ]; then \
		echo "ERROR: Local package repository not found"; \
		echo "Set up first: make repo-setup"; \
		exit 1; \
	fi
	@echo "Building Docker image (first time may take a few minutes)..."
	@cd $(IMAGEBUILDER_DIR) && docker compose build --quiet
	@echo "Running Image Builder..."
	@UID=$$(id -u) GID=$$(id -g) $(IMAGEBUILDER_COMPOSE) run --rm imagebuilder \
		/scripts/build-image.sh $(NODE_NAME)
	@echo ""
	@echo "=== Build complete ==="
	@ls -lh images/mesh-node$(NODE)-sysupgrade.bin 2>/dev/null || echo "Image not found"

# Build images for all nodes
# Usage: make image-build-all
image-build-all:
	@echo "=== Building custom firmware images for ALL nodes ==="
	@for n in 1 2 3; do \
		if [ -d "snapshots/mesh-node$$n" ]; then \
			echo ""; \
			echo ">>> Building image for node$$n..."; \
			$(MAKE) image-build NODE=$$n; \
		else \
			echo "Skipping node$$n (no snapshot found)"; \
		fi; \
	done
	@echo ""
	@echo "=== All builds complete ==="
	@ls -lh images/*.bin 2>/dev/null || echo "No images found"

# Show Image Builder info and available profiles
# Usage: make image-info
image-info:
	@echo "=== OpenWrt Image Builder Information ==="
	@cd $(IMAGEBUILDER_DIR) && docker compose build --quiet
	@UID=$$(id -u) GID=$$(id -g) $(IMAGEBUILDER_COMPOSE) run --rm imagebuilder \
		make info | grep -E "^(Current|Default|Available|Target|Subtarget)"
	@echo ""
	@echo "=== D-Link DIR-1960 Profile ==="
	@UID=$$(id -u) GID=$$(id -g) $(IMAGEBUILDER_COMPOSE) run --rm imagebuilder \
		make info | grep -A5 "dlink_dir-1960" || echo "Profile: dlink_dir-1960-a1"

# Enter Image Builder container shell for debugging
# Usage: make image-shell
image-shell:
	@echo "=== Entering Image Builder shell ==="
	@echo "Exit with 'exit' or Ctrl+D"
	@cd $(IMAGEBUILDER_DIR) && docker compose build --quiet
	@UID=$$(id -u) GID=$$(id -g) $(IMAGEBUILDER_COMPOSE) run --rm imagebuilder /bin/bash

# Clean built images
# Usage: make image-clean
image-clean:
	@echo "=== Cleaning built images ==="
	@if [ -d "images" ] && [ -n "$$(ls images/*.bin 2>/dev/null)" ]; then \
		echo "Removing:"; \
		ls -lh images/*.bin 2>/dev/null; \
		rm -f images/*.bin images/*.sha256; \
		echo "Done"; \
	else \
		echo "No images to clean"; \
	fi

# ============================================================================
# Factory Reset (Restore Vanilla OpenWrt)
# ============================================================================
# Reset a configured mesh node back to vanilla OpenWrt factory defaults
# This allows re-deployment from scratch without physical access

# Factory reset node (restore vanilla OpenWrt)
# Usage: make factory-reset NODE=1
factory-reset:
ifndef NODE
	$(error NODE variable required. Usage: make factory-reset NODE=1)
endif
	@echo "=== Factory Reset for $(NODE_NAME) ==="
	@echo ""
	@echo "WARNING: This will ERASE ALL CONFIGURATION on $(NODE_NAME)!"
	@echo "The node will reboot to 192.168.1.1 with factory defaults."
	@echo ""
	@read -p "Are you sure you want to factory reset $(NODE_NAME)? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		echo ""; \
		echo "Logging to: $(ANSIBLE_LOG)"; \
		bash -c "set -a && source $(ENV_FILE) && set +a && \
		if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no -i \$$SSH_KEY_PATH root@$(NODE_IP_PROD) 'echo Node reachable' 2>/dev/null; then \
			echo 'Node found at $(NODE_IP_PROD)'; \
			$(ANSIBLE_CMD) -i $(INVENTORY_PROD) playbooks/factory-reset.yml --limit $(NODE_NAME) $(VERBOSE_FLAG); \
		else \
			echo 'ERROR: Cannot reach node at $(NODE_IP_PROD)'; \
			echo 'Factory reset requires node to be reachable at production IP.'; \
			exit 1; \
		fi"; \
	else \
		echo "Operation cancelled"; \
	fi

# ============================================================================
# Sysupgrade (Flash Firmware Images)
# ============================================================================
# Flash firmware images to nodes (vanilla or configured)
# Supports two image types:
#   - mesh:    Custom-built image with config baked in (default)
#   - vanilla: Stock OpenWrt image (factory reset)
# Config is ALWAYS wiped (sysupgrade -n)

# Sysupgrade node (auto-detects vanilla vs configured node)
# Usage: make sysupgrade NODE=1                     (mesh image, default)
#        make sysupgrade NODE=1 IMAGE_TYPE=mesh     (mesh image)
#        make sysupgrade NODE=1 IMAGE_TYPE=vanilla  (vanilla OpenWrt)
#        make sysupgrade NODE=1 IMAGE_PATH=/path/to/image.bin
sysupgrade:
ifndef NODE
	$(error NODE variable required. Usage: make sysupgrade NODE=1)
endif
	@echo "=== Sysupgrade for $(NODE_NAME) ==="
	@echo ""
	@echo "Image Type: $(if $(IMAGE_TYPE),$(IMAGE_TYPE),mesh) (default: mesh)"
	@echo "Config: ALWAYS WIPED (sysupgrade -n)"
	@echo ""
	@bash -c "set -a && source $(ENV_FILE) && set +a && \
	IMAGE_TYPE_VAL=\"$(if $(IMAGE_TYPE),$(IMAGE_TYPE),mesh)\"; \
	if [ \"\$$IMAGE_TYPE_VAL\" = 'mesh' ]; then \
		echo 'Image: MESH (custom-built with config baked in)'; \
		echo 'Result: Node boots to 10.11.12.$(NODE) ready to go'; \
	else \
		echo 'Image: VANILLA (stock OpenWrt)'; \
		echo 'Result: Node boots to 192.168.1.1 (needs deploy-node)'; \
	fi; \
	echo ''; \
	echo 'Checking for node...'; \
	echo ''; \
	if ssh -o ConnectTimeout=3 -o BatchMode=yes -o StrictHostKeyChecking=no -i \$$SSH_KEY_PATH root@$(NODE_IP_PROD) 'echo ok' 2>/dev/null; then \
		echo 'Node found at $(NODE_IP_PROD) (CONFIGURED)'; \
		echo ''; \
		read -p 'Proceed with sysupgrade of $(NODE_NAME)? (yes/no): ' confirm; \
		if [ \"\$$confirm\" = 'yes' ]; then \
			echo ''; \
			echo 'Logging to: $(ANSIBLE_LOG)'; \
			$(ANSIBLE_CMD) -i $(INVENTORY_PROD) playbooks/sysupgrade.yml --limit $(NODE_NAME) $(VERBOSE_FLAG); \
		else \
			echo 'Operation cancelled'; \
		fi; \
	else \
		echo 'Node not at $(NODE_IP_PROD), checking for vanilla node...'; \
		echo 'Switching workstation to initial network...'; \
		$(ANSIBLE_CMD) playbooks/switch-to-initial-network.yml; \
		echo ''; \
		if ssh -o ConnectTimeout=3 -o BatchMode=yes -o StrictHostKeyChecking=no root@$(NODE_IP_INITIAL) 'echo ok' 2>/dev/null; then \
			echo 'Node found at $(NODE_IP_INITIAL) (VANILLA)'; \
			echo ''; \
			read -p 'Proceed with sysupgrade of $(NODE_NAME)? (yes/no): ' confirm; \
			if [ \"\$$confirm\" = 'yes' ]; then \
				echo ''; \
				echo 'Logging to: $(ANSIBLE_LOG)'; \
				$(ANSIBLE_CMD) -i $(INVENTORY_INITIAL) playbooks/sysupgrade.yml --limit $(NODE_NAME) $(VERBOSE_FLAG); \
				echo ''; \
				if [ \"\$$IMAGE_TYPE_VAL\" = 'mesh' ]; then \
					echo 'Switching workstation to mesh network...'; \
					$(ANSIBLE_CMD) playbooks/switch-to-mesh-network.yml; \
				else \
					echo 'Node will boot to 192.168.1.1 - staying on initial network'; \
				fi; \
			else \
				echo 'Operation cancelled'; \
			fi; \
		else \
			echo ''; \
			echo 'ERROR: Cannot reach node at $(NODE_IP_PROD) or $(NODE_IP_INITIAL)'; \
			echo ''; \
			echo 'Ensure the node is connected and powered on.'; \
			exit 1; \
		fi; \
	fi"

# ============================================================================
# Network Validation Framework
# ============================================================================
# Unified validation framework to prove the mesh network is functioning
# Uses tiered checks: smoke (30s), standard (3min), comprehensive (10min)
# See validate/ package for implementation details

# Standard validation (Tier 2) - recommended for post-deployment
# Checks: connectivity, SSH, batman-adv, topology, VLANs
# Usage: make validate
validate:
	@echo "=== Mesh Network Validation (Standard) ==="
	@cd .. && uv run python -m validate standard

# Quick smoke test (Tier 1) - fast health check
# Checks: ping, SSH, batman module loaded
# Usage: make validate-smoke
validate-smoke:
	@echo "=== Mesh Network Validation (Smoke) ==="
	@cd .. && uv run python -m validate smoke

# Comprehensive validation (Tier 3) - full functional test
# Checks: all Tier 2 + services, security, WAN, infrastructure
# Usage: make validate-full
validate-full:
	@echo "=== Mesh Network Validation (Comprehensive) ==="
	@cd .. && uv run python -m validate comprehensive

# Certification validation (Tier 4) - production readiness
# Checks: all Tier 3 + failover, wireless, stress testing
# Usage: make validate-cert
validate-cert:
	@echo "=== Mesh Network Validation (Certification) ==="
	@cd .. && uv run python -m validate certification

# Validation with JSON output (for monitoring/CI)
# Usage: make validate-json
validate-json:
	@cd .. && uv run python -m validate standard --json

# Verbose validation showing node details
# Usage: make validate-verbose
validate-verbose:
	@cd .. && uv run python -m validate standard --verbose

# ============================================================================
# Live Network Testing
# ============================================================================
# Run pytest live tests to validate mesh network is functioning correctly
# Tests are located in ../tests/live/
# Reports are saved to test-reports/ within the project root

# Test report directory (relative to project root, not Makefile location)
TEST_REPORT_DIR := test-reports

# Standard live tests (recommended)
# Runs all non-destructive tests with standard timeout
# Usage: make test
test:
	@echo "=== Running Live Network Tests ==="
	@echo "Testing mesh network functionality..."
	@echo ""
	@cd .. && mkdir -p $(TEST_REPORT_DIR) && uv run pytest tests/live/ -v --timeout=120 \
		-m "live and not destructive and not wlan2" \
		--html=$(TEST_REPORT_DIR)/live-tests-$$(date +%Y%m%d_%H%M%S).html \
		--self-contained-html \
		2>&1 | tee $(TEST_REPORT_DIR)/live-tests-latest.log
	@echo ""
	@echo "=== Test Complete ==="
	@echo "Report: $(TEST_REPORT_DIR)/"

# Wireless/wlan2 tests only
# Runs wireless configuration and client connection tests
# Usage: make test-wireless
test-wireless:
	@echo "=== Running Wireless Tests ==="
	@echo ""
	@cd .. && uv run pytest tests/live/test_wireless.py -v --timeout=120 \
		-m "live"
	@echo ""
	@echo "=== Wireless Tests Complete ==="

# Quick connectivity tests only
# Runs basic connectivity and batman status tests
# Usage: make test-quick
test-quick:
	@echo "=== Running Quick Connectivity Tests ==="
	@echo ""
	@cd .. && uv run pytest tests/live/test_connectivity.py tests/live/test_batman_mesh.py -v --timeout=60 \
		-m "live and not destructive"
	@echo ""
	@echo "=== Quick Tests Complete ==="

# Full test suite with HTML report
# Runs all tests including performance benchmarks
# Usage: make test-full
test-full:
	@echo "=== Running Full Live Test Suite ==="
	@echo "This may take several minutes..."
	@echo ""
	@cd .. && mkdir -p $(TEST_REPORT_DIR) && uv run pytest tests/live/ -v --timeout=180 \
		-m "live and not destructive" \
		--html=$(TEST_REPORT_DIR)/full-tests-$$(date +%Y%m%d_%H%M%S).html \
		--self-contained-html \
		2>&1 | tee $(TEST_REPORT_DIR)/full-tests-latest.log
	@echo ""
	@echo "=== Full Test Suite Complete ==="
	@echo "Report: $(TEST_REPORT_DIR)/"

# Destructive failover tests
# WARNING: These tests temporarily disrupt network connectivity!
# Usage: make test-destructive
test-destructive:
	@echo "=== Destructive Failover Tests ==="
	@echo ""
	@echo "WARNING: These tests will temporarily disrupt network connectivity!"
	@echo "They test link failover and WAN failover scenarios."
	@echo ""
	@read -p "Are you sure you want to run destructive tests? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		echo ""; \
		cd .. && mkdir -p $(TEST_REPORT_DIR) && MESH_RUN_DESTRUCTIVE_TESTS=true uv run pytest tests/live/ -v --timeout=300 \
			-m "live and destructive" \
			--html=$(TEST_REPORT_DIR)/destructive-tests-$$(date +%Y%m%d_%H%M%S).html \
			--self-contained-html \
			2>&1 | tee $(TEST_REPORT_DIR)/destructive-tests-latest.log; \
		echo ""; \
		echo "=== Destructive Tests Complete ==="; \
		echo "Report: $(TEST_REPORT_DIR)/"; \
	else \
		echo "Operation cancelled"; \
	fi

# Infrastructure tests (switches and infrastructure devices)
# Tests connectivity to all switches and infrastructure on management network
# Usage: make test-infrastructure
test-infrastructure:
	@echo "=== Running Infrastructure Tests ==="
	@echo "Testing switches (10.11.10.11-13) and infrastructure devices..."
	@echo ""
	@cd .. && mkdir -p $(TEST_REPORT_DIR) && uv run pytest tests/live/test_infrastructure.py -v --timeout=120 \
		-m "infrastructure" \
		--html=$(TEST_REPORT_DIR)/infrastructure-tests-$$(date +%Y%m%d_%H%M%S).html \
		--self-contained-html \
		2>&1 | tee $(TEST_REPORT_DIR)/infrastructure-tests-latest.log
	@echo ""
	@echo "=== Infrastructure Tests Complete ==="
	@echo "Report: $(TEST_REPORT_DIR)/"
