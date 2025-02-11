"""Manages all Digital Ocean-specific aspects of the deployment process.

Notes:
- 

Add a new file to the user's project, without using a template:

    def _add_dockerignore(self):
        # Add a dockerignore file, based on user's local project environmnet.
        path = dsd_config.project_root / ".dockerignore"
        dockerignore_str = self._build_dockerignore()
        plugin_utils.add_file(path, dockerignore_str)

Add a new file to the user's project, using a template:

    def _add_dockerfile(self):
        # Add a minimal dockerfile.
        template_path = self.templates_path / "dockerfile_example"
        context = {
            "django_project_name": dsd_config.local_project_name,
        }
        contents = plugin_utils.get_template_string(template_path, context)

        # Write file to project.
        path = dsd_config.project_root / "Dockerfile"
        plugin_utils.add_file(path, contents)

Modify user's settings file:

    def _modify_settings(self):
        # Add platformsh-specific settings.
        template_path = self.templates_path / "settings.py"
        context = {
            "deployed_project_name": self._get_deployed_project_name(),
        }
        plugin_utils.modify_settings_file(template_path, context)

Add a set of requirements:

    def _add_requirements(self):
        # Add requirements for deploying to Fly.io.
        requirements = ["gunicorn", "psycopg2-binary", "dj-database-url", "whitenoise"]
        plugin_utils.add_packages(requirements)
"""

import sys, os, re, json
from pathlib import Path

from django.utils.safestring import mark_safe

import requests
import paramiko

from . import deploy_messages as platform_msgs
from . import utils as do_utils

from django_simple_deploy.management.commands.utils import plugin_utils
from django_simple_deploy.management.commands.utils.plugin_utils import dsd_config
from django_simple_deploy.management.commands.utils.command_errors import DSDCommandError


class PlatformDeployer:
    """Perform the initial deployment to Digital Ocean

    If --automate-all is used, carry out an actual deployment.
    If not, do all configuration work so the user only has to commit changes, and ...
    """

    def __init__(self):
        self.templates_path = Path(__file__).parent / "templates"

    # --- Public methods ---

    def deploy(self, *args, **options):
        """Coordinate the overall configuration and deployment."""
        plugin_utils.write_output("\nConfiguring project for deployment to Digital Ocean...")

        self._validate_platform()
        self._prep_automate_all()

        # Configure project for deployment to Digital Ocean.

        # Update server.
        # Run a read-only command through SSH.
        self._update_server()
        

        self._conclude_automate_all()
        self._show_success_message()

    # --- Helper methods for deploy() ---

    def _validate_platform(self):
        """Make sure the local environment and project supports deployment to Digital Ocean.

        Returns:
            None
        Raises:
            DSDCommandError: If we find any reason deployment won't work.
        """
        pass


    def _prep_automate_all(self):
        """Take any further actions needed if using automate_all."""
        pass


    def _update_server(self):
        """Update the server.

        This should be idempotent, if at all possible.
        """
        plugin_utils.write_output("Updating server (this may take a few minutes)...")

        # client = paramiko.SSHClient()
        # client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        cmd = "sudo apt-get update && sudo DEBIAN_FRONTEND=noninteractive apt-get full-upgrade -y"
        plugin_utils.write_output(f"  Update command: $ {cmd}")
        # try:
        #     client.connect(
        #         hostname = os.environ.get("DSD_HOST_IPADDR"),
        #         username = os.environ.get("DSD_HOST_USERNAME"),
        #         password = os.environ.get("DSD_HOST_PW"),
        #     )
        #     _stdin, _stdout, _stderr = client.exec_command(cmd)
        #     stdout = _stdout.read().decode().strip()
        #     stderr = _stderr.read().decode().strip()
        # finally:
        #     client.close()
        stdout, stderr = do_utils.run_server_cmd_ssh(cmd)

        if stdout:
            plugin_utils.write_output(stdout)
        if stderr:
            plugin_utils.write_output(stderr)

        plugin_utils.write_output("  Finished updating server.")

        breakpoint()

        # Reboot if required. If so, call this function again. Add messages.




    def _conclude_automate_all(self):
        """Finish automating the push to Digital Ocean.

        - Commit all changes.
        - ...
        """
        # Making this check here lets deploy() be cleaner.
        if not dsd_config.automate_all:
            return

        plugin_utils.commit_changes()

        # Push project.
        plugin_utils.write_output("  Deploying to Digital Ocean...")

        # Should set self.deployed_url, which will be reported in the success message.
        pass

    def _show_success_message(self):
        """After a successful run, show a message about what to do next.

        Describe ongoing approach of commit, push, migrate.
        """
        if dsd_config.automate_all:
            msg = platform_msgs.success_msg_automate_all(self.deployed_url)
        else:
            msg = platform_msgs.success_msg(log_output=dsd_config.log_output)
        plugin_utils.write_output(msg)
