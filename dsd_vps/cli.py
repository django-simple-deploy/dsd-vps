"""Extends the core django-simple-deploy CLI."""

import json
import shlex
import subprocess
from pathlib import Path

from django_simple_deploy.management.commands.utils.plugin_utils import dsd_config
from django_simple_deploy.management.commands.utils.command_errors import (
    DSDCommandError,
)

from .plugin_config import plugin_config


class PluginCLI:

    def __init__(self, parser):
        """Add plugin-specific args."""
        group_desc = "Plugin-specific CLI args for dsd-vps"
        plugin_group = parser.add_argument_group(
            title="Options for dsd-vps",
            description = group_desc,
        )

        plugin_group.add_argument(
            "--platform",
            type=Path,
            help="Hosting platform, such as digital_ocean.",
            default=None,
        )

        plugin_group.add_argument(
            "--ssh-key",
            type=Path,
            help="Path to private SSH key for accessing VPS instance.",
            default=None,
        )


def validate_cli(options):
    """Validate options that were passed to CLI."""
    platform = options["platform"]
    _validate_platform(platform)

    ssh_key = options(["ssh_key"])
    if ssh_key is not None:
        path_ssh_key = Path(options["ssh_key"])
        _validate_ssh_key(path_ssh_key)



# --- Helper functions ---

def _validate_platform(platform):
    """Validate the --platform arg.

    Should only be used to create initial resources on server in fully automated workflow.
    """
    # DEV: If using --automate-all, must specify platform.
    if not platform:
        return

    supported_platforms = ["digital_ocean"]
    if platform not in supported_platforms:
        msg = f"The platform arg must be one of: {', '.join(supported_platforms)}"
        raise DSDCommandError(msg)


def _validate_ssh_key(path_ssh_key):
    """Validate the ssh key arg that was passed.

    It's not None if this function is reached.
    """
    if dsd_config.unit_testing:
        return

    if not path_ssh_key.exists():
        msg = f"The path {path_ssh_key.as_posix()} does not exist."
        raise DSDCommandError(msg)

    # ssh_key arg is valid. Set the relevant plugin_config attribute.
    plugin_config.path_ssh_key = path_ssh_key