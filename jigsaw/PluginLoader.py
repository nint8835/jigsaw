import importlib.util
import os
import json
import json.decoder
import logging
import traceback
from typing import List


class PluginLoader(object):

    def __init__(self, plugin_path:str="", log_level=logging.INFO):
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
        self._plugins = {}

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
                        manifest["path"] = item_path
                        self._manifests.append(manifest)
                        self.logger.debug("Loaded plugin manifest from {}.".format(manifest_path))
                    except json.decoder.JSONDecodeError:
                        self.logger.error("Failed to decode plugin manifest at {}.".format(manifest_path))
                    except OSError:
                        self.logger.error("Failed to load plugin manifest at {}.".format(manifest_path))
                else:
                    self.logger.debug("No plugin manifest found at {}.".format(manifest_path))

    def get_manifest_for_plugin(self, plugin_name: str) -> dict:
        for manifest in self._manifests:
            if manifest["name"] == plugin_name:
                return manifest

    def get_plugin_loaded(self, plugin_name: str) -> bool:
        return plugin_name in self._plugins

    def load_plugin(self, manifest: dict, *args):
        if self.get_plugin_loaded(manifest["name"]):
            self.logger.debug("Plugin {} is already loaded.".format(manifest["name"]))
            return
        try:
            self.logger.debug("Attempting to load plugin {}.".format(manifest["name"]))
            for dependency in manifest.get("dependencies", []):
                if not self.get_plugin_loaded(dependency):
                    self.logger.debug("Must load dependency {} first.".format(dependency))
                    self.load_plugin(self.get_manifest_for_plugin(dependency), *args)

            spec = importlib.util.spec_from_file_location(
                manifest.get("module_name", manifest["name"].replace(" ", "_")),
                os.path.join(manifest["path"], manifest.get("main_path", "__init__.py"))
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            module_class = manifest.get("main_class", "Plugin")
            plugin = getattr(module, module_class)(*args)
            self._plugins[manifest["name"]] = plugin

            self.logger.debug("Plugin {} loaded.".format(manifest["name"]))

        except:
            exc_path = os.path.join(manifest["path"], "error.log")
            with open(exc_path, "w") as f:
                f.write(traceback.format_exc(5))
            self.logger.error("Failed to load plugin {}. Error log written to {}.".format(manifest["name"], exc_path))

    def load_plugins(self, *args):
        for manifest in self._manifests:
            self.load_plugin(manifest, *args)