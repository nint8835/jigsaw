import os
import json
import json.decoder
import logging


class PluginLoader(object):

    def __init__(self, plugin_path="", log_level=logging.INFO):
        logging.basicConfig(format="{%(asctime)s} (%(name)s) [%(levelname)s]: %(message)s",
                            datefmt="%x, %X",
                            level=log_level)
        self.logger = logging.getLogger("Jigsaw")

        if plugin_path == "":
            self.plugin_path = os.path.join(os.getcwd(), "plugins")
            self.logger.debug("No plugin path specified, using {}.".format(self.plugin_path))
        else:
            self.plugin_path = plugin_path
            self.logger.debug("Using specified plugin path of {}.".format(self.plugin_path))

        self._manifests = []

    def load_manifests(self):
        for item in os.listdir(self.plugin_path):
            item_path = os.path.join(self.plugin_path, item)
            if os.path.isdir(item_path):
                manifest_path = os.path.join(self.plugin_path, item, "plugin.json")
                self.logger.debug("Attempting to load plugin manifest from {}.".format(manifest_path))
                if os.path.isfile(manifest_path):
                    try:
                        with open(manifest_path) as f:
                            manifest = json.load(f)
                        self._manifests.append(manifest)
                        self.logger.debug("Loaded plugin manifest from {}.".format(manifest_path))
                    except json.decoder.JSONDecodeError:
                        self.logger.error("Failed to decode plugin manifest at {}.".format(manifest_path))
                    except OSError:
                        self.logger.error("Failed to load plugin manifest at {}.".format(manifest_path))
                else:
                    self.logger.debug("No plugin manifest found at {}.".format(manifest_path))

    def get_manifests_for_plugin(self, plugin_name):
        return [i for i in self._manifests if i["name"] == plugin_name]
