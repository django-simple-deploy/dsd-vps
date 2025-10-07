"""Helper functions specific to {{PlatformmName}}.

Some Fly.io functions are included as an example.
"""

import re, time
import json
import subprocess
import shlex
from pathlib import Path

import pytest

from tests.e2e_tests.utils.it_helper_functions import make_sp_call


# def create_project():
#     """Create a project on Fly.io."""
#     print("\n\nCreating a project on Fly.io...")
#     output = (
#         make_sp_call(f"fly apps create --generate-name", capture_output=True)
#         .stdout.decode()
#         .strip()
#     )
#     print("create_project output:", output)

#     re_app_name = r"New app created: (.*)"
#     app_name = re.search(re_app_name, output).group(1)
#     print(f"  App name: {app_name}")

#     return app_name


# def deploy_project(app_name):
#     """Make a non-automated deployment."""
#     # Consider pausing before the deployment. Some platforms need a moment
#     #   for the newly-created resources to become fully available.
#     # time.sleep(30)

#     print("Deploying to Fly.io...")
#     make_sp_call("fly deploy")

#     # Open project and get URL.
#     output = (
#         make_sp_call(f"fly apps open -a {app_name}", capture_output=True)
#         .stdout.decode()
#         .strip()
#     )
#     print("fly open output:", output)

#     re_url = r"opening (http.*) \.\.\."
#     project_url = re.search(re_url, output).group(1)
#     if "https" not in project_url:
#         project_url = project_url.replace("http", "https")

#     print(f"  Project URL: {project_url}")

#     return project_url


# def get_project_url_name():
#     """Get project URL and app name of a deployed project.
#     This is used when testing the automate_all workflow.
#     """
#     output = (
#         make_sp_call("fly status --json", capture_output=True).stdout.decode().strip()
#     )
#     status_json = json.loads(output)

#     app_name = status_json["Name"]
#     project_url = f"https://{app_name}.fly.dev"

#     print(f"  Found app name: {app_name}")
#     print(f"  Project URL: {project_url}")

#     return project_url, app_name

def validate_do_cli():
    """Make sure the DO CLI is installed, and authenticated.

    DEV: This may be generalized by a parent that makes sure some host platform's 
    CLI is installed, or otherwise verify we'll be able to make a vps instance.
    """
    # Make sure doctl is installed.
    cmd = "doctl version"
    cmd_parts = shlex.split(cmd)
    print(f"Checking that DO CLI is installed: {cmd}")
    try:
        output = subprocess.run(cmd_parts, capture_output=True).stdout.decode().strip()
    except FileNotFoundError:
        msg = "  DO CLI is not installed; cannot create a VPS instance for testing."
        print(msg)
        pytest.exit(msg)
    else:
        print(f"  DO CLI version: {output}")

    # Make sure it's authenticated.
    cmd = "doctl account get"
    cmd_parts = shlex.split(cmd)
    print(f"Checking that CLI is authenticated: {cmd}")

    output = subprocess.run(cmd_parts, capture_output=True)
    stderr = output.stderr.decode()
    if "Unable to initialize DigitalOcean API client" in stderr:
        msg = "  DO CLI is not authenticated; maybe run `doctl auth init`?"
        print(msg)
        pytest.exit(msg)
    else:
        stdout = output.stdout.decode()
        print(f"  {stdout}")

def create_vps_instance():
    """Create a vps instance to test against."""
    ...


def check_log(tmp_proj_dir):
    """Check the log that was generated during a full deployment.

    Checks that log file exists, and that DATABASE_URL is not logged.
    """
    path = tmp_proj_dir / "simple_deploy_logs"
    if not path.exists():
        return False

    log_files = list(path.glob("simple_deploy_*.log"))
    if not log_files:
        return False

    log_str = log_files[0].read_text()
    if "DATABASE_URL" in log_str:
        return False

    return True

def destroy_project(request):
    """Destroy the deployed project, and all remote resources."""
    print("\nCleaning up:")

    droplet_id = request.config.cache.get("droplet_id", None)
    if not droplet_id:
        print("  No droplet id found; can't destroy any remote resources.")
        return None

    print(f"  Destroying DO droplet {droplet_id}...")
    make_sp_call(f"doctl compute droplet delete {droplet_id}")

    # Remove relevant block from ~/.ssh/config
    print("  Removing config for Git push to this server.")

    from django_simple_deploy.management.commands.utils import plugin_utils
    from dsd_vps import templates as dsd_vps_templates

    # Build the config block, just like it's done in plugin.
    path_templates = Path(dsd_vps_templates.__path__[0])
    path_template = path_templates / "git_ssh_config_block.txt"
    context = {
        "server_ip": request.config.cache.get("deployed_ip_address", None),
        "server_username": "django_user",
    }
    lines_config_block = plugin_utils.get_template_string(path_template, context).splitlines()
    lines_config_block = [l.strip() for l in lines_config_block]

    # Remove this block from .ssh/config.
    path_ssh_config = Path.home() / ".ssh" / "config"
    lines_ssh_config = path_ssh_config.read_text().splitlines()

    new_lines_ssh_config = []
    for line in lines_ssh_config:
        if line.strip() in lines_config_block:
            continue
        else:
            new_lines_ssh_config.append(line)

    new_contents_ssh_config = "\n".join(new_lines_ssh_config)
    path_ssh_config.write_text(new_contents_ssh_config)
