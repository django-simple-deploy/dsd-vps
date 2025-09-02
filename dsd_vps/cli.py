"""Extend the core django-simple-deploy CLI to support deployment to VPS instances."""

class PluginCLI:
    def __init__(self, parser):
        """Extends the CLI for django-simple-deploy."""

        parser.add_argument(
            "--ssh-key",
            help="Path to private SSH key for accessing VPS instance.",
        )