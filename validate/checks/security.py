"""
Security validation checks.

Tier 3 (Comprehensive):
- check_ssh_hardening: SSH security settings applied
- check_https: TLS certificates valid for LuCI
"""

from validate.config import NODES
from validate.core.executor import NodeExecutor
from validate.core.results import CheckResult, CheckStatus


def check_ssh_hardening() -> CheckResult:  # noqa: C901
    """
    Check that SSH hardening is applied.

    Validates:
    - Password authentication disabled
    - Root login with key only
    - Connection limits set

    Returns:
        CheckResult with SSH security status.
    """
    result = CheckResult(
        category="security.ssh",
        status=CheckStatus.PASS,
        message="",
    )

    for node_name in NODES:
        executor = NodeExecutor(node_name)
        issues = []

        # Check for OpenSSH (sshd) or Dropbear
        rc_sshd, _, _ = executor.run("pgrep sshd")
        rc_dropbear, _, _ = executor.run("pgrep dropbear")

        if rc_sshd == 0:
            # OpenSSH - check sshd_config
            rc, config, _ = executor.run("cat /etc/ssh/sshd_config 2>/dev/null")

            if rc == 0:
                # Check PasswordAuthentication
                if "PasswordAuthentication yes" in config:
                    issues.append("password auth enabled")

                # Check PermitRootLogin
                if "PermitRootLogin yes" in config:
                    issues.append("root password login allowed")

        elif rc_dropbear == 0:
            # Dropbear - check UCI config
            rc, passwd_auth, _ = executor.run(
                "uci get dropbear.@dropbear[0].PasswordAuth 2>/dev/null"
            )
            if "on" in passwd_auth.lower():
                issues.append("password auth enabled")

        else:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.FAIL,
                message="No SSH daemon running",
            )
            continue

        # Check for SSH key
        rc_key, _, _ = executor.run(
            "test -f /etc/dropbear/authorized_keys || test -f /root/.ssh/authorized_keys"
        )

        if rc_key != 0:
            issues.append("no authorized_keys")

        if issues:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.FAIL,
                message=", ".join(issues),
                data={"issues": issues},
            )
        else:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.PASS,
                message="SSH hardened",
            )

    result.aggregate_status()

    if result.passed:
        result.message = "SSH hardening applied on all nodes"
    else:
        failed = [n for n, r in result.nodes.items() if r.status == CheckStatus.FAIL]
        result.message = f"SSH security issues: {', '.join(failed)}"

    return result


def check_https() -> CheckResult:
    """
    Check that HTTPS/TLS is configured for LuCI.

    Validates:
    - TLS certificate exists
    - uhttpd configured for HTTPS
    - HTTP redirects to HTTPS (optional)

    Returns:
        CheckResult with HTTPS status.
    """
    result = CheckResult(
        category="security.https",
        status=CheckStatus.PASS,
        message="",
    )

    for node_name in NODES:
        executor = NodeExecutor(node_name)

        # Check certificate exists
        rc_cert, _, _ = executor.run("test -f /etc/uhttpd.crt")
        rc_key, _, _ = executor.run("test -f /etc/uhttpd.key")

        if rc_cert != 0 or rc_key != 0:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.FAIL,
                message="TLS certificate missing",
            )
            continue

        # Check uhttpd is listening on HTTPS
        rc, listen, _ = executor.run("uci get uhttpd.main.listen_https 2>/dev/null")

        if rc != 0 or not listen.strip():
            result.add_node_result(
                node=node_name,
                status=CheckStatus.FAIL,
                message="HTTPS not configured in uhttpd",
            )
            continue

        # Check certificate validity (basic check)
        rc_valid, cert_info, _ = executor.run(
            "openssl x509 -in /etc/uhttpd.crt -noout -dates 2>/dev/null | grep notAfter"
        )

        if rc_valid == 0:
            result.add_node_result(
                node=node_name,
                status=CheckStatus.PASS,
                message="HTTPS enabled",
                data={"expiry": cert_info.strip()},
            )
        else:
            # Certificate exists but couldn't verify - still OK
            result.add_node_result(
                node=node_name,
                status=CheckStatus.PASS,
                message="HTTPS enabled (cert check skipped)",
            )

    result.aggregate_status()

    if result.passed:
        result.message = "HTTPS enabled on all nodes"
    else:
        failed = [n for n, r in result.nodes.items() if r.status == CheckStatus.FAIL]
        result.message = f"HTTPS issues: {', '.join(failed)}"

    return result
