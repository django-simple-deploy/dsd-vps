"""Utilities specific to Digital Ocean."""

import os

import paramiko


def run_server_cmd_ssh(cmd):
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
        )
        _stdin, _stdout, _stderr = client.exec_command(cmd)
        stdout = _stdout.read().decode().strip()
        stderr = _stderr.read().decode().strip()
    finally:
        client.close()

    return stdout, stderr