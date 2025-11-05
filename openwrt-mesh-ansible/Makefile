# Makefile for OpenWrt Mesh Network Ansible

.PHONY: help deploy verify backup update check clean

help:
	@echo "OpenWrt Mesh Network - Ansible Commands"
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
	@echo "  make logs            - Fetch recent logs"

deploy:
	ansible-playbook playbooks/deploy.yml

deploy-node1:
	ansible-playbook playbooks/deploy.yml --limit node1

deploy-node2:
	ansible-playbook playbooks/deploy.yml --limit node2

deploy-node3:
	ansible-playbook playbooks/deploy.yml --limit node3

verify:
	ansible-playbook playbooks/verify.yml

backup:
	ansible-playbook playbooks/backup.yml

update:
	ansible-playbook playbooks/update.yml

update-check:
	ansible-playbook playbooks/update.yml --tags check

check:
	ansible-playbook playbooks/deploy.yml --check

ping:
	ansible mesh_nodes -m ping

clean:
	find . -name "*.retry" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

# Network-specific deployments
deploy-network:
	ansible-playbook playbooks/deploy.yml --tags network

deploy-wireless:
	ansible-playbook playbooks/deploy.yml --tags wireless

deploy-dhcp:
	ansible-playbook playbooks/deploy.yml --tags dhcp

deploy-firewall:
	ansible-playbook playbooks/deploy.yml --tags firewall

# Package management
packages:
	ansible-playbook playbooks/deploy.yml --tags packages

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
