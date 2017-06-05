class JigsawPlugin(object):
    """
    Base class for all jigsaw plugins
    """

    def __init__(self, manifest, *args):
        """
        Initializes the plugin

        :param manifest: The plugin manifest
        :param args: Any other arguments passed to the plugin
        """
        self.manifest = manifest

    def enable(self):
        """
        Handles the setup of a plugin on enable
        """
        pass

    def disable(self):
        """
        Handles cleaning up before disabling/unloading a plugin
        """
        pass
