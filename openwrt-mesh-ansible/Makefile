# Makefile for OpenWrt Mesh Network Ansible

# Source .env file if it exists to load environment variables
-include ../.env
export

# Command prefix to source .env for ansible-playbook commands
ENV_FILE := ../.env
ANSIBLE_CMD := $(if $(wildcard $(ENV_FILE)),set -a && source $(ENV_FILE) && set +a &&,) ansible-playbook

.PHONY: help validate-env check-all check-connectivity check-initial-node1 check-initial-node2 check-initial-node3 \
        deploy-initial-node1 deploy-initial-node2 deploy-initial-node3 \
        deploy-initial-node1-verbose deploy-initial-node2-verbose deploy-initial-node3-verbose \
        switch-to-initial-network switch-to-mesh-network \
        check-node1 check-node2 check-node3 audit deploy verify backup update check clean \
        show-logs tail-logs clear-logs

help:
	@echo "OpenWrt Mesh Network - Ansible Commands"
	@echo ""
	@echo "=========================================="
	@echo "PHASE 0: Environment Setup (REQUIRED FIRST)"
	@echo "=========================================="
	@echo "  make validate-env            - Validate .env configuration"
	@echo ""
	@echo "=========================================="
	@echo "PHASE 1: Initial Setup (Fresh OpenWrt - Dropbear, No Password)"
	@echo "=========================================="
	@echo "Configure ONE node at a time (all start at 192.168.1.1, no root password):"
	@echo ""
	@echo "Check connectivity:"
	@echo "  make check-initial-node1     - Check fresh Node 1 (at 192.168.1.1)"
	@echo "  make check-initial-node2     - Check fresh Node 2 (at 192.168.1.1)"
	@echo "  make check-initial-node3     - Check fresh Node 3 (at 192.168.1.1)"
	@echo ""
	@echo "Deploy (includes automatic network switching):"
	@echo "  make deploy-initial-node1            - Deploy to Node 1 (quiet)"
	@echo "  make deploy-initial-node2            - Deploy to Node 2 (quiet)"
	@echo "  make deploy-initial-node3            - Deploy to Node 3 (quiet)"
	@echo "  make deploy-initial-node1 VERBOSE=1  - Deploy to Node 1 (verbose -vvv)"
	@echo "  make deploy-initial-node2 VERBOSE=1  - Deploy to Node 2 (verbose -vvv)"
	@echo "  make deploy-initial-node3 VERBOSE=1  - Deploy to Node 3 (verbose -vvv)"
	@echo ""
	@echo "Each deployment automatically:"
	@echo "  1. Switches workstation to 192.168.1.100 (initial network)"
	@echo "  2. Deploys configuration to node at 192.168.1.1"
	@echo "  3. Switches workstation to 10.11.12.100 (mesh network)"
	@echo ""
	@echo "Manual network switching (if needed):"
	@echo "  make switch-to-initial-network       - Switch to 192.168.1.100"
	@echo "  make switch-to-mesh-network          - Switch to 10.11.12.100"
	@echo ""
	@echo "=========================================="
	@echo "PHASE 2: Production (OpenSSH with SSH Key)"
	@echo "=========================================="
	@echo "After all nodes are configured (10.11.12.x, passwordless SSH key):"
	@echo "  make check-all               - Check connectivity to ALL nodes"
	@echo "  make check-node1             - Check configured Node 1 (at 10.11.12.1)"
	@echo "  make check-node2             - Check configured Node 2 (at 10.11.12.2)"
	@echo "  make check-node3             - Check configured Node 3 (at 10.11.12.3)"
	@echo "  make audit                   - Audit all nodes"
	@echo ""
	@echo "Available targets:"
	@echo "  make deploy         - Deploy configuration to all nodes"
	@echo "  make deploy-node1   - Deploy to Node 1 only"
	@echo "  make deploy-node2   - Deploy to Node 2 only"
	@echo "  make deploy-node3   - Deploy to Node 3 only"
	@echo "  make verify         - Check mesh status"
	@echo "  make backup         - Backup all node configurations"
	@echo "  make update         - Update packages on all nodes"
	@echo "  make update-check   - Check for available updates"
	@echo "  make check          - Dry run deployment (no changes)"
	@echo "  make ping           - Test connectivity to all nodes"
	@echo "  make clean          - Clean temporary files"
	@echo ""
	@echo "Network-specific targets:"
	@echo "  make deploy-network  - Deploy network config only"
	@echo "  make deploy-wireless - Deploy wireless config only"
	@echo "  make deploy-dhcp     - Deploy DHCP config only"
	@echo "  make deploy-firewall - Deploy firewall config only"
	@echo ""
	@echo "Advanced:"
	@echo "  make packages        - Install packages only"
	@echo "  make batman-status   - Check batman-adv status"
	@echo "  make logs            - Fetch recent logs from nodes"
	@echo ""
	@echo "Debugging:"
	@echo "  make show-logs       - Show last 100 lines of Ansible logs"
	@echo "  make tail-logs       - Follow Ansible logs (live)"
	@echo "  make clear-logs      - Clear Ansible log file"

# ============================================================================
# PHASE 0: Environment Validation
# ============================================================================

validate-env:
	@bash -c "$(ANSIBLE_CMD) playbooks/validate-env.yml"

# ============================================================================
# PHASE 1: Initial Setup - Fresh OpenWrt Nodes (192.168.1.1)
# ============================================================================
# Use these targets when setting up a FRESH OpenWrt node at 192.168.1.1
# IMPORTANT: Only connect to ONE node at a time (they all start at same IP)

check-initial-node1:
	@bash -c "$(ANSIBLE_CMD) -i inventory/hosts-initial.yml playbooks/check-connectivity.yml --limit node1"

check-initial-node2:
	@bash -c "$(ANSIBLE_CMD) -i inventory/hosts-initial.yml playbooks/check-connectivity.yml --limit node2"

check-initial-node3:
	@bash -c "$(ANSIBLE_CMD) -i inventory/hosts-initial.yml playbooks/check-connectivity.yml --limit node3"

deploy-initial-node1:
	@bash -c "$(ANSIBLE_CMD) playbooks/switch-to-initial-network.yml && \
	          $(ANSIBLE_CMD) -i inventory/hosts-initial.yml playbooks/deploy.yml --limit node1 $(if $(VERBOSE),-vvv) && \
	          $(ANSIBLE_CMD) playbooks/switch-to-mesh-network.yml"

deploy-initial-node2:
	@bash -c "$(ANSIBLE_CMD) playbooks/switch-to-initial-network.yml && \
	          $(ANSIBLE_CMD) -i inventory/hosts-initial.yml playbooks/deploy.yml --limit node2 $(if $(VERBOSE),-vvv) && \
	          $(ANSIBLE_CMD) playbooks/switch-to-mesh-network.yml"

deploy-initial-node3:
	@bash -c "$(ANSIBLE_CMD) playbooks/switch-to-initial-network.yml && \
	          $(ANSIBLE_CMD) -i inventory/hosts-initial.yml playbooks/deploy.yml --limit node3 $(if $(VERBOSE),-vvv) && \
	          $(ANSIBLE_CMD) playbooks/switch-to-mesh-network.yml"

# Network switching (for workstation eth interface)
switch-to-initial-network:
	@bash -c "$(ANSIBLE_CMD) playbooks/switch-to-initial-network.yml"

switch-to-mesh-network:
	@bash -c "$(ANSIBLE_CMD) playbooks/switch-to-mesh-network.yml"

# Backward compatibility aliases (deprecated - use VERBOSE=1 instead)
deploy-initial-node1-verbose:
	@$(MAKE) deploy-initial-node1 VERBOSE=1

deploy-initial-node2-verbose:
	@$(MAKE) deploy-initial-node2 VERBOSE=1

deploy-initial-node3-verbose:
	@$(MAKE) deploy-initial-node3 VERBOSE=1

# ============================================================================
# PHASE 2: Production - Configured Mesh Nodes (10.11.12.x)
# ============================================================================
# Use these targets AFTER all nodes are configured and at their final IPs

# check-all: Use AFTER nodes are configured with different IPs (10.11.12.x)
check-all:
	@bash -c "$(ANSIBLE_CMD) playbooks/check-connectivity.yml"

# Backwards compatibility alias
check-connectivity: check-all

# check-nodeX: Check individual configured nodes at their final IPs
check-node1:
	@bash -c "$(ANSIBLE_CMD) playbooks/check-connectivity.yml --limit node1"

check-node2:
	@bash -c "$(ANSIBLE_CMD) playbooks/check-connectivity.yml --limit node2"

check-node3:
	@bash -c "$(ANSIBLE_CMD) playbooks/check-connectivity.yml --limit node3"

# Node Audit & Preparation
audit:
	@bash -c "$(ANSIBLE_CMD) playbooks/audit.yml"

audit-node1:
	@bash -c "$(ANSIBLE_CMD) playbooks/audit.yml --limit node1"

audit-node2:
	@bash -c "$(ANSIBLE_CMD) playbooks/audit.yml --limit node2"

audit-node3:
	@bash -c "$(ANSIBLE_CMD) playbooks/audit.yml --limit node3"

# Deployment targets
deploy:
	@bash -c "$(ANSIBLE_CMD) playbooks/deploy.yml"

deploy-node1:
	@bash -c "$(ANSIBLE_CMD) playbooks/deploy.yml --limit node1"

deploy-node2:
	@bash -c "$(ANSIBLE_CMD) playbooks/deploy.yml --limit node2"

deploy-node3:
	@bash -c "$(ANSIBLE_CMD) playbooks/deploy.yml --limit node3"

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
