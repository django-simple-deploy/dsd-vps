"""Utilities specific to Digital Ocean."""

import os
import time

import paramiko

from django_simple_deploy.management.commands.utils import plugin_utils
from django_simple_deploy.management.commands.utils.plugin_utils import dsd_config


def run_server_cmd_ssh(cmd, timeout=10, show_output=True, skip_logging=None):
    """Run a command on the server, through an SSH connection.

    Returns:
        Tuple of Str: (stdout, stderr)
    """
    # If skip_logging is not explicitly set, set it to False.
    # This matches the default in plugin_utils.write_output().
    if skip_logging is None:
        skip_logging = False

    plugin_utils.write_output("Running server command over SSH...", skip_logging=skip_logging)
    plugin_utils.write_output(f"  command: {cmd}", skip_logging=skip_logging)

    # Get client.
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Run command, and close connection.
    try:
        client.connect(
            hostname = os.environ.get("DSD_HOST_IPADDR"),
            username = os.environ.get("DSD_HOST_USERNAME"),
            password = os.environ.get("DSD_HOST_PW"),
            timeout = timeout
        )
        _stdin, _stdout, _stderr = client.exec_command(cmd)

        stdout = _stdout.read().decode().strip()
        stderr = _stderr.read().decode().strip()
    finally:
        client.close()

    # Show stdout and stderr, unless suppressed.
    if stdout and show_output:
        plugin_utils.write_output(stdout, skip_logging=skip_logging)
    if stderr and show_output:
        plugin_utils.write_output(stderr, skip_logging=skip_logging)

    # Return both stdout and stderr.
    return stdout, stderr


def reboot_if_required():
    """Reboot the server if required.

    Returns:
        bool: True if rebooted, False if not rebooted.
    """
    plugin_utils.write_output("Checking if reboot required...")

    cmd = "ls /var/run"
    stdout, stderr = run_server_cmd_ssh(cmd, show_output=False)

    if "reboot-required" in stdout:
        reboot_server()
        return True
    else:
        plugin_utils.write_output("  No reboot required.")
        return False

def reboot_server():
    """Reboot the server, and wait for it to be available again.

    Returns:
        None
    Raises:
        DSDCommandError: If the server is unavailable after rebooting.
    """
    plugin_utils.write_output("  Rebooting...")
    cmd = "sudo shutdown -r now"
    stdout, stderr = run_server_cmd_ssh(cmd)

    # Pause to let shutdown begin; polling too soon shows server available because
    # shutdown hasn't started yet.
    time.sleep(5)

    # Poll for availability.
    if not check_server_available():
        raise DSDCommandError("Cannot reach server after reboot.")


def check_server_available(delay=10, timeout=300):
    """Check if the server is responding.

    Returns:
        bool
    """
    plugin_utils.write_output("Checking if server is responding...")

    max_attempts = int(timeout / delay)
    for attempt in range(max_attempts):
        try:
            stdout, stderr = run_server_cmd_ssh("uptime")
            plugin_utils.write_output("  Server is available.")
            return True
        except TimeoutError:
            plugin_utils.write_output(f"  Attempt {attempt+1}/{max_attempts} failed.")
            plugin_utils.write_output(f"    Waiting {delay}s for server to become available.")
            time.sleep(delay)

    plugin_utils.write_output("Server did not respond.")
    return False

def add_server_user():
    """Add a non-root user.

    Only if current user is root.

    Returns:
        None
    """
    username = os.environ.get("DSD_HOST_USERNAME")
    if (username != "root") or dsd_config.unit_testing:
        return

    plugin_utils.write_output("Adding non-root user...")
    django_username = "django_user"

    cmd = f"useradd -m {django_username}"
    run_server_cmd_ssh(cmd)

    password = os.environ.get("DSD_HOST_PW")
    cmd = f'echo "{django_username}:{password}" | chpasswd'

    run_server_cmd_ssh(cmd, skip_logging=True)




