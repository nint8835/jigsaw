import importlib.util
import os
import json
import json.decoder
import logging
import traceback
from typing import List

from .Plugin import JigsawPlugin


class PluginLoader(object):

    def __init__(self, plugin_path: str="", log_level=logging.INFO, plugin_class = JigsawPlugin):
        logging.basicConfig(format="{%(asctime)s} (%(name)s) [%(levelname)s]: %(message)s",
                            datefmt="%x, %X",
                            level=log_level)
        self._logger = logging.getLogger("Jigsaw")

        if plugin_path == "":
            self.plugin_path = os.path.join(os.getcwd(), "plugins")
            self._logger.debug("No plugin path specified, using {}.".format(self.plugin_path))
        else:
            self.plugin_path = plugin_path
            self._logger.debug("Using specified plugin path of {}.".format(self.plugin_path))

        self._plugin_class = plugin_class

        self._manifests = []
        self._plugins = {}
        self._modules = {}

    def load_manifests(self):
        for item in os.listdir(self.plugin_path):
            item_path = os.path.join(self.plugin_path, item)
            if os.path.isdir(item_path):
                manifest_path = os.path.join(self.plugin_path, item, "plugin.json")
                self._logger.debug("Attempting to load plugin manifest from {}.".format(manifest_path))
                if os.path.isfile(manifest_path):
                    try:
                        with open(manifest_path) as f:
                            manifest = json.load(f)
                        manifest["path"] = item_path
                        self._manifests.append(manifest)
                        self._logger.debug("Loaded plugin manifest from {}.".format(manifest_path))
                    except json.decoder.JSONDecodeError:
                        self._logger.error("Failed to decode plugin manifest at {}.".format(manifest_path))
                    except OSError:
                        self._logger.error("Failed to load plugin manifest at {}.".format(manifest_path))
                else:
                    self._logger.debug("No plugin manifest found at {}.".format(manifest_path))

    def get_manifest_for_plugin(self, plugin_name: str) -> dict:
        for manifest in self._manifests:
            if manifest["name"] == plugin_name:
                return manifest

    def get_plugin_loaded(self, plugin_name: str) -> bool:
        return plugin_name in self._plugins

    def load_plugin(self, manifest: dict, *args):
        if self.get_plugin_loaded(manifest["name"]):
            self._logger.debug("Plugin {} is already loaded.".format(manifest["name"]))
            return
        try:
            self._logger.debug("Attempting to load plugin {}.".format(manifest["name"]))
            for dependency in manifest.get("dependencies", []):
                if not self.get_plugin_loaded(dependency):
                    self._logger.debug("Must load dependency {} first.".format(dependency))
                    if self.get_manifest_for_plugin(dependency) is None:
                        self._logger.error("Dependency {} could not be found.".format(dependency))
                    else:
                        self.load_plugin(self.get_manifest_for_plugin(dependency), *args)

            not_loaded = [i for i in manifest.get("dependencies", []) if not self.get_plugin_loaded(i)]
            if len(not_loaded) != 0:
                self._logger.error("Plugin {} failed to load due to missing dependencies. Dependencies: {}".format(
                    manifest["name"], ", ".join(not_loaded)
                ))
                return

            spec = importlib.util.spec_from_file_location(
                manifest.get("module_name", manifest["name"].replace(" ", "_")),
                os.path.join(manifest["path"], manifest.get("main_path", "__init__.py"))
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            module_class = manifest.get("main_class", "Plugin")
            plugin_class = getattr(module, module_class)
            if issubclass(plugin_class, self._plugin_class):
                plugin = plugin_class(manifest, *args)
            else:
                self._logger.error("Failed to load {} due to invalid baseclass.".format(manifest["name"]))
                return
            self._plugins[manifest["name"]] = plugin
            self._modules[manifest["name"]] = module

            self._logger.debug("Plugin {} loaded.".format(manifest["name"]))

        except:
            exc_path = os.path.join(manifest["path"], "error.log")
            with open(exc_path, "w") as f:
                f.write(traceback.format_exc(5))
            self._logger.error("Failed to load plugin {}. Error log written to {}.".format(manifest["name"], exc_path))

    def load_plugins(self, *args):
        for manifest in self._manifests:
            self.load_plugin(manifest, *args)

    def get_plugin(self, name: str) -> JigsawPlugin:
        return self._plugins[name]

    def get_module(self, name: str):
        return self._modules[name]

    def get_all_plugins(self) -> List[dict]:
        return [{
            "manifest": i,
            "plugin": self.get_plugin(i["name"]),
            "module": self.get_module(i["name"])
        } for i in self._manifests]
