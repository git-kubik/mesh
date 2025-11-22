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
        check-all check-connectivity audit deploy \
        switch-to-initial-network switch-to-mesh-network \
        verify backup update update-check check ping clean \
        deploy-network deploy-wireless deploy-dhcp deploy-firewall \
        packages batman-status logs \
        show-logs tail-logs clear-logs \
        uptime reboot restart-network restart-wireless install \
        usb-storage usb-status

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
	@echo "  make switch-to-initial-network  - Switch workstation to 192.168.1.100"
	@echo "  make switch-to-mesh-network     - Switch workstation to 10.11.12.100"
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
	@echo "MONITORING & DEBUGGING"
	@echo "================================================================================"
	@echo "  make batman-status              - Check batman-adv mesh status"
	@echo "  make logs                       - Fetch recent logs from nodes"
	@echo "  make show-logs                  - Show last 100 lines of Ansible logs"
	@echo "  make tail-logs                  - Follow Ansible logs (live)"
	@echo "  make clear-logs                 - Clear Ansible log files"
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
		$(ANSIBLE_CMD) -i $(INVENTORY_PROD) playbooks/audit.yml --limit $(NODE_NAME) $(VERBOSE_FLAG); \
	else \
		echo 'Node not configured yet, checking at 192.168.1.1 (initial mode)'; \
		$(ANSIBLE_CMD) -i $(INVENTORY_INITIAL) playbooks/audit.yml --limit $(NODE_NAME) $(VERBOSE_FLAG); \
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
# Network Switching (Manual Operations)
# ============================================================================
# These targets are available for manual network switching if needed
# (The unified deploy-node target handles this automatically)

switch-to-initial-network:
	@bash -c "$(ANSIBLE_CMD) playbooks/switch-to-initial-network.yml"

switch-to-mesh-network:
	@bash -c "$(ANSIBLE_CMD) playbooks/switch-to-mesh-network.yml"

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

# Audit all nodes
audit:
	@echo "=== Auditing all nodes ==="
	@echo "Logging to: $(ANSIBLE_LOG)"
	@bash -c "$(ANSIBLE_CMD) playbooks/audit.yml"

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
