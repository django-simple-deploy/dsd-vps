"""Extend the core django-simple-deploy CLI to support deployment to VPS instances."""

class PluginCLI:
    def __init__(self, parser):
        """Extends the CLI for django-simple-deploy."""

        # # Define groups of arguments. These groups help generate a clean
        # #   output for `manage.py deploy --help`
        # help_group = parser.add_argument_group("Get help")
        # required_group = parser.add_argument_group("Required arguments")
        # behavior_group = parser.add_argument_group(
        #     "Customize django-simple-deploy's behavior"
        # )
        # deployment_config_group = parser.add_argument_group(
        #     "Customize deployment configuration"
        # )

        # # Show our own help message.
        # help_group.add_argument(
        #     "--help", "-h", action="help", help="Show this help message and exit."
        # )




        parser.add_argument(
            "--ssh-key",
            help="Path to private SSH key for accessing VPS instance.",
        )