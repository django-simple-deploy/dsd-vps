"""Utilities specific to Digital Ocean."""

import os
import time

import paramiko

from django_simple_deploy.management.commands.utils import plugin_utils


def run_server_cmd_ssh(cmd, timeout=10):
    """Run a command on the server, through an SSH connection.

    Returns:
        Tuple of Str: (stdout, stderr)
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

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

    return stdout, stderr


def check_server_available(delay=10, timeout=300):
    """Check if the server is responding.

    Returns:
        bool
    """
    plugin_utils.write_output("Checking if server is responding...")

    max_attempts = int(timeout / delay)
    for attempt in range(max_attempts):
        try:
            # client = paramiko.SSHClient()
            # client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # client.connect(
            #     hostname = os.environ.get("DSD_HOST_IPADDR"),
            #     username = os.environ.get("DSD_HOST_USERNAME"),
            #     password = os.environ.get("DSD_HOST_PW"),
            #     timeout = 5,
            # )
            stdout, stderr = run_server_cmd_ssh("uptime")
            plugin_utils.write_output("  Server is available.")
            # breakpoint()
            # client.close()
            return True
        except TimeoutError:
            plugin_utils.write_output(f"  Attempt {attempt+1}/{max_attempts} failed.")
            time.sleep(delay)

    plugin_utils.write_output("Server did not respond.")
    return False