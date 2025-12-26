"""
SSH execution utilities for network validation.

Ported from tests/live/conftest.py for standalone use.
"""

import subprocess
from typing import List, Tuple

from validate.config import NODES, get_ssh_key_path


def ssh_command(node_ip: str, command: str, timeout: int = 30) -> Tuple[int, str, str]:
    """
    Execute a command on a node via SSH.

    Args:
        node_ip: IP address of the node.
        command: Command to execute.
        timeout: Command timeout in seconds.

    Returns:
        Tuple of (return_code, stdout, stderr).
    """
    ssh_key = get_ssh_key_path()
    ssh_opts = [
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "UserKnownHostsFile=/dev/null",
        "-o",
        "ConnectTimeout=10",
        "-o",
        "BatchMode=yes",
        "-i",
        ssh_key,
    ]

    cmd = ["ssh", *ssh_opts, f"root@{node_ip}", command]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Command timed out after {timeout}s"
    except Exception as e:
        return -1, "", str(e)


def run_on_node(node: str, command: str, timeout: int = 30) -> Tuple[int, str, str]:
    """
    Execute a command on a named node.

    Args:
        node: Node name (node1, node2, node3).
        command: Command to execute.
        timeout: Command timeout in seconds.

    Returns:
        Tuple of (return_code, stdout, stderr).
    """
    node_info = NODES.get(node)
    if not node_info:
        return -1, "", f"Unknown node: {node}"
    return ssh_command(node_info.ip, command, timeout)


def run_local(command: str, timeout: int = 30) -> Tuple[int, str, str]:
    """
    Execute a command locally.

    Args:
        command: Command to execute (as shell string).
        timeout: Command timeout in seconds.

    Returns:
        Tuple of (return_code, stdout, stderr).
    """
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Command timed out after {timeout}s"
    except Exception as e:
        return -1, "", str(e)


class NodeExecutor:
    """Helper class for executing commands on nodes."""

    def __init__(self, node: str):
        """
        Initialize with node name.

        Args:
            node: Node name (node1, node2, node3).
        """
        self.node = node
        self.node_info = NODES[node]

    def run(self, command: str, timeout: int = 30) -> Tuple[int, str, str]:
        """
        Execute command on this node.

        Args:
            command: Command to execute.
            timeout: Command timeout in seconds.

        Returns:
            Tuple of (return_code, stdout, stderr).
        """
        return run_on_node(self.node, command, timeout)

    def run_ok(self, command: str, timeout: int = 30) -> str:
        """
        Execute command and raise on failure, return stdout.

        Args:
            command: Command to execute.
            timeout: Command timeout in seconds.

        Returns:
            stdout as string.

        Raises:
            RuntimeError: If command fails.
        """
        rc, stdout, stderr = self.run(command, timeout)
        if rc != 0:
            raise RuntimeError(f"Command failed on {self.node}: {command}\nstderr: {stderr}")
        return stdout

    def batctl(self, args: str, timeout: int = 30) -> str:
        """
        Execute batctl command and return output.

        Args:
            args: Arguments to pass to batctl.
            timeout: Command timeout in seconds.

        Returns:
            Command output as string.
        """
        return self.run_ok(f"batctl {args}", timeout)

    def uci_get(self, key: str) -> str:
        """
        Get UCI configuration value.

        Args:
            key: UCI key to query.

        Returns:
            Configuration value.
        """
        return self.run_ok(f"uci get {key}").strip()

    def ping(self, target: str, count: int = 3) -> bool:
        """
        Ping a target from this node.

        Args:
            target: Target IP or hostname.
            count: Number of ping packets.

        Returns:
            True if ping succeeds.
        """
        rc, _, _ = self.run(f"ping -c {count} -W 2 {target}")
        return rc == 0

    def service_running(self, service: str) -> bool:
        """
        Check if a service is running.

        Args:
            service: Service name.

        Returns:
            True if service is running.
        """
        rc, _, _ = self.run(f"/etc/init.d/{service} status 2>/dev/null || pgrep -x {service}")
        return rc == 0

    def file_exists(self, path: str) -> bool:
        """
        Check if a file exists on the node.

        Args:
            path: File path to check.

        Returns:
            True if file exists.
        """
        rc, _, _ = self.run(f"test -f {path}")
        return rc == 0


def get_all_executors() -> List["NodeExecutor"]:
    """Get executors for all nodes."""
    return [NodeExecutor(node) for node in NODES]
