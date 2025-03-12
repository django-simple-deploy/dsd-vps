"""Manages all VPS-specific aspects of the deployment process.

VPS notes:

- All actions taken against the server should be idempotent if at all possible. If an
  action is not idempotent, that should be noted.
"""

import sys, os, re, json
import time
from pathlib import Path
import tempfile
import webbrowser

from django.utils.safestring import mark_safe

import requests

from . import deploy_messages as platform_msgs
from . import utils as do_utils

from django_simple_deploy.management.commands.utils import plugin_utils
from django_simple_deploy.management.commands.utils.plugin_utils import dsd_config
from django_simple_deploy.management.commands.utils.command_errors import DSDCommandError


class PlatformDeployer:
    """Perform the initial deployment.

    If --automate-all is used, carry out an actual deployment.
    If not, do all configuration work so the user only has to commit changes, and ...
    """

    def __init__(self):
        self.templates_path = Path(__file__).parent / "templates"

    # --- Public methods ---

    def deploy(self, *args, **options):
        """Coordinate the overall configuration and deployment."""
        plugin_utils.write_output("\nConfiguring project for deployment...")

        self._validate_platform()
        self._prep_automate_all()

        # Configure server.
        self._connect_server()
        self._update_server()
        self._setup_server()
        
        # Configure project for deployment.
        self._add_requirements()
        self._modify_settings()
        self._add_serve_project_file()

        self._add_caddyfile()
        self._configure_gunicorn()

        self._conclude_automate_all()
        self._show_success_message()

    # --- Helper methods for deploy() ---

    def _validate_platform(self):
        """Make sure the local environment and project supports deployment to a VPS.

        Returns:
            None
        Raises:
            DSDCommandError: If we find any reason deployment won't work.
        """
        pass


    def _prep_automate_all(self):
        """Take any further actions needed if using automate_all."""
        pass


    def _connect_server(self):
        """Make sure we can connect to the server, with an appropriate username."""
        do_utils.set_server_username()
        do_utils.configure_firewall()


    def _update_server(self):
        """Update the server."""
        # Don't update during unit and integration testing.
        plugin_utils.write_output("Updating server (this may take a few minutes)...")
        if dsd_config.unit_testing:
            plugin_utils.write_output("  (skipped during testing)")
            return

        # Run update command.
        cmd = "sudo apt-get update && sudo DEBIAN_FRONTEND=noninteractive apt-get full-upgrade -y"
        stdout, stderr = do_utils.run_server_cmd_ssh(cmd)
        plugin_utils.write_output("  Finished updating server.")

        # See if we need to reboot. If rebooted, check for updates again. This is most
        # likely needed with a fresh VM, after its first round of updates.
        rebooted = do_utils.reboot_if_required()
        if rebooted:
            self._update_server()

    def _setup_server(self):
        """Run initial server setup.

        Roughly follows a standard Ubuntu server setup guide, such as:
        - https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu
        """
        # DEV: Disable during development.
        do_utils.install_uv()
        do_utils.install_python()
        do_utils.configure_git(self.templates_path)
        do_utils.install_caddy()

    def _add_requirements(self):
        """Add server-specific requirements."""
        plugin_utils.write_output("  Adding server-specific requirements...")
        requirements = ["gunicorn"]
        plugin_utils.add_packages(requirements)

    def _modify_settings(self):
        # Add do-specific settings.
        template_path = self.templates_path / "settings.py"
        context = {
            "deployed_project_name": dsd_config.local_project_name,
            "ip_addr": os.environ.get("DSD_HOST_IPADDR"),
        }
        plugin_utils.modify_settings_file(template_path, context)

    def _add_serve_project_file(self):
        # Add a bash script to start server process after code pushes.
        # template_path = self.templates_path / "dockerfile_example"
        # context = {
        #     "django_project_name": dsd_config.local_project_name,
        # }
        # contents = plugin_utils.get_template_string(template_path, context)

        # # Write file to project.
        # path = dsd_config.project_root / "Dockerfile"
        # plugin_utils.add_file(path, contents)


        template_path = self.templates_path / "serve_project.sh"
        project_path = Path(f"/home/{dsd_config.server_username}/{dsd_config.local_project_name}")
        context = {
            "project_path": project_path,
            "uv_path": f"/home/{dsd_config.server_username}/.local/bin/uv",
        }
        contents = plugin_utils.get_template_string(template_path, context)

        # Write file to project.
        path = dsd_config.project_root / "serve_project.sh"
        plugin_utils.add_file(path, contents)

    def _add_caddyfile(self):
        """Add a Caddyfile to the project.

        This configures Caddy, for serving static files.
        """
        template_path = self.templates_path / "Caddyfile"
        context = {
            "server_ip_address": os.environ.get("DSD_HOST_IPADDR")
        }
        contents = plugin_utils.get_template_string(template_path, context)

        with tempfile.NamedTemporaryFile() as tmp:
            path_local = Path(tmp.name)

            # Write to the local project during testing, so we can test the contents.
            if dsd_config.unit_testing:
                path_local = dsd_config.project_root / "Caddyfile"
            
            path_local.write_text(contents)

            path_remote = f"/home/{dsd_config.server_username}/Caddyfile"
            do_utils.copy_to_server(path_local, path_remote)

            cmd = f"sudo mv /home/{dsd_config.server_username}/Caddyfile /etc/caddy/Caddyfile"
            do_utils.run_server_cmd_ssh(cmd)





    def _configure_gunicorn(self):
        """Configure gunicorn to run as a system service.

        DEV: This should probably go somewhere else.
        """
        plugin_utils.write_output("  Configuring gunicorn to run as a service.")

        # Write gunicorn.socket to accessible location, then move it to appropriate location.
        template_path = self.templates_path / "gunicorn.socket"
        # cmd = f"scp {template_path} {dsd_config.server_username}@{os.environ.get("DSD_HOST_IPADDR")}:/home/{dsd_config.server_username}/gunicorn.socket"
        # plugin_utils.write_output(cmd)
        # plugin_utils.run_quick_command(cmd)

        path_local = self.templates_path / "gunicorn.socket"
        path_remote = f"/home/{dsd_config.server_username}/gunicorn.socket"
        do_utils.copy_to_server(path_local, path_remote)

        cmd = f"sudo mv /home/{dsd_config.server_username}/gunicorn.socket /etc/systemd/system/gunicorn.socket"
        do_utils.run_server_cmd_ssh(cmd)

        # gunicorn.service
        template_path = self.templates_path / "gunicorn.service"
        project_path = Path(f"/home/{dsd_config.server_username}/{dsd_config.local_project_name}")
        context = {
            "server_username": dsd_config.server_username,
            "project_path": project_path,
            "project_name": dsd_config.local_project_name,
        }
        contents = plugin_utils.get_template_string(template_path, context)
        with tempfile.NamedTemporaryFile() as tmp:
            path_local = Path(tmp.name)

            # Write to the local project during testing, so we can test the contents.
            if dsd_config.unit_testing:
                path_local = dsd_config.project_root / "gunicorn.service"
            
            path_local.write_text(contents)

            # cmd = f"scp {path.as_posix()} {dsd_config.server_username}@{os.environ.get("DSD_HOST_IPADDR")}:/etc/systemd/system/gunicorn.service"
            # plugin_utils.write_output(cmd)
            # plugin_utils.run_quick_command(cmd)

            # cmd = f"scp {path} {dsd_config.server_username}@{os.environ.get("DSD_HOST_IPADDR")}:/home/{dsd_config.server_username}/gunicorn.service"
            # plugin_utils.write_output(cmd)
            # plugin_utils.run_quick_command(cmd)

            path_remote = f"/home/{dsd_config.server_username}/gunicorn.service"
            do_utils.copy_to_server(path_local, path_remote)



            cmd = f"sudo mv /home/{dsd_config.server_username}/gunicorn.service /etc/systemd/system/gunicorn.service"
            do_utils.run_server_cmd_ssh(cmd)




    def _conclude_automate_all(self):
        """Finish automating the push.

        - Commit all changes.
        - ...
        """
        # Making this check here lets deploy() be cleaner.
        if not dsd_config.automate_all:
            return

        plugin_utils.commit_changes()

        # Push project.
        plugin_utils.write_output("  Deploying project...")

        do_utils.push_project()
        # Make serve script executable.
        project_path = Path(f"/home/{dsd_config.server_username}/{dsd_config.local_project_name}")
        serve_script_path = f"{project_path}/serve_project.sh"
        cmd = f"chmod +x {serve_script_path}"
        do_utils.run_server_cmd_ssh(cmd)

        do_utils.serve_project()

        # Should set self.deployed_url, which will be reported in the success message.
        self.deployed_url = f"http://{os.environ.get('DSD_HOST_IPADDR')}/"
        webbrowser.open(self.deployed_url)


    def _show_success_message(self):
        """After a successful run, show a message about what to do next.

        Describe ongoing approach of commit, push, migrate.
        """
        if dsd_config.automate_all:
            msg = platform_msgs.success_msg_automate_all(self.deployed_url)
        else:
            msg = platform_msgs.success_msg(log_output=dsd_config.log_output)
        plugin_utils.write_output(msg)
