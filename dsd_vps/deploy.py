"""Manages all VPS-specific aspects of the deployment process.

Notes:
- ...
"""

import django_simple_deploy

from dsd_vps.platform_deployer import PlatformDeployer
from .plugin_config import PluginConfig

from . import cli


@django_simple_deploy.hookimpl
def dsd_get_plugin_config():
    """Get platform-specific attributes needed by core."""
    plugin_config = PluginConfig()
    return plugin_config


@django_simple_deploy.hookimpl
def dsd_get_plugin_cli_args(parser):
    # parser.add_argument(
    #     "--ssh-key",
    #     help="Path to private SSH key for accessing VPS instance.",
    # )
    plugin_cli = cli.PluginCLI(parser)


@django_simple_deploy.hookimpl
def dsd_deploy():
    """Carry out platform-specific deployment steps."""
    platform_deployer = PlatformDeployer()
    platform_deployer.deploy()
