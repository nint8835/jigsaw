from typing import Any, Dict


class JigsawPlugin:
    """
    Base class for all jigsaw plugins
    """

    def __init__(self, manifest: Dict[str, Any], *args: Any):
        """
        Initializes the plugin

        :param manifest: The plugin manifest
        :param args: Any other arguments passed to the plugin
        """
        self.manifest = manifest

    def enable(self) -> None:
        """
        Handles the setup of a plugin on enable
        """
        pass

    def disable(self) -> None:
        """
        Handles cleaning up before disabling/unloading a plugin
        """
        pass
