"""Manages all VPS-specific aspects of the deployment process.

Notes:
- ...
"""

import django_simple_deploy

from dsd_vps.platform_deployer import PlatformDeployer
from .plugin_config import PluginConfig


@django_simple_deploy.hookimpl
def dsd_get_plugin_config():
    """Get platform-specific attributes needed by core."""
    plugin_config = PluginConfig()
    return plugin_config


@django_simple_deploy.hookimpl
def dsd_deploy():
    """Carry out platform-specific deployment steps."""
    platform_deployer = PlatformDeployer()
    platform_deployer.deploy()
