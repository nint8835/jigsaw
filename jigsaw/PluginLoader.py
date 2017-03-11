import importlib.util
import json
import json.decoder
import logging
import os
import traceback
from typing import List

from .Plugin import JigsawPlugin


class PluginLoader(object):
    """
    Class that handles all of jigsaw's plugin management functions
    """

    def __init__(self, plugin_path: str="", log_level=logging.INFO, plugin_class=JigsawPlugin) -> None:
        """
        Initializes the plugin loader

        :param plugin_path: Path to load plugins from
        :param log_level: Log level
        :param plugin_class: Parent class of all plugins
        """
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

    def load_manifests(self) -> None:
        """
        Loads all plugin manifests on the plugin path
        """
        for item in os.listdir(self.plugin_path):
            item_path = os.path.join(self.plugin_path, item)
            if os.path.isdir(item_path):
                self.load_manifest(item_path)

    def load_manifest(self, path: str) -> None:
        """
        Loads a plugin manifest from a given path

        :param path: The folder to load the plugin manifest from
        """
        manifest_path = os.path.join(path, "plugin.json")
        self._logger.debug("Attempting to load plugin manifest from {}.".format(manifest_path))
        try:
            with open(manifest_path) as f:
                manifest = json.load(f)
            manifest["path"] = path
            self._manifests.append(manifest)
            self._logger.debug("Loaded plugin manifest from {}.".format(manifest_path))
        except json.decoder.JSONDecodeError:
            self._logger.error("Failed to decode plugin manifest at {}.".format(manifest_path))
        except OSError:
            self._logger.error("Failed to load plugin manifest at {}.".format(manifest_path))

    def get_manifest(self, plugin_name: str) -> dict:
        """
        Gets the manifest for a specified plugin

        :param plugin_name: The name of the plugin
        :return: The manifest for the specified plugin
        """
        for manifest in self._manifests:
            if manifest["name"] == plugin_name:
                return manifest

    def get_plugin_loaded(self, plugin_name: str) -> bool:
        """
        Returns if a given plugin is loaded

        :param plugin_name: The plugin to check to loaded status for
        :return: Whether the specified plugin is loaded
        """
        return plugin_name in self._plugins

    def load_plugin(self, manifest: dict, *args) -> None:
        """
        Loads a plugin from the given manifest

        :param manifest: The manifest to use to load the plugin
        :param args: Arguments to pass to the plugin
        """
        if self.get_plugin_loaded(manifest["name"]):
            self._logger.debug("Plugin {} is already loaded.".format(manifest["name"]))
            return
        try:
            self._logger.debug("Attempting to load plugin {}.".format(manifest["name"]))
            for dependency in manifest.get("dependencies", []):
                if not self.get_plugin_loaded(dependency):
                    self._logger.debug("Must load dependency {} first.".format(dependency))
                    if self.get_manifest(dependency) is None:
                        self._logger.error("Dependency {} could not be found.".format(dependency))
                    else:
                        self.load_plugin(self.get_manifest(dependency), *args)

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

    def load_plugins(self, *args) -> None:
        """
        Loads all plugins

        :param args: Arguments to pass to the plugins
        """
        for manifest in self._manifests:
            self.load_plugin(manifest, *args)

    def get_plugin(self, name: str) -> JigsawPlugin:
        """
        Gets a loaded plugin

        :param name: Name of the plugin
        :return: The plugin
        """
        try:
            return self._plugins[name]
        except KeyError:
            return None

    def get_module(self, name: str):
        """
        Gets the module for a plugin

        :param name: Name of the plugin
        :return: The module
        """
        try:
            return self._modules[name]
        except KeyError:
            return None

    def get_all_plugins(self) -> List[dict]:
        """
        Gets all loaded plugins

        :return: List of all plugins
        """
        return [{
            "manifest": i,
            "plugin": self.get_plugin(i["name"]),
            "module": self.get_module(i["name"])
        } for i in self._manifests]

    def disable_all_plugins(self) -> None:
        """
        Calls the disable method on all initialized plugins
        """
        for plugin in self._plugins:
            self._plugins[plugin].disable()

    def enable_all_plugins(self) -> None:
        """
        Calls the enable method on all initialized plugins
        """
        for plugin in self._plugins:
            self._plugins[plugin].enable()

    def reload_plugin(self, name: str, *args) -> None:
        """
        Reloads a given plugin

        :param name: The name of the plugin
        :param args: The args to pass to the plugin
        """
        self._logger.debug("Reloading {}.".format(name))

        self._logger.debug("Disabling {}.".format(name))
        self.get_plugin(name).disable()

        self._logger.debug("Removing plugin instance.")
        del self._plugins[name]

        self._logger.debug("Unloading module.")
        del self._modules[name]

        self._logger.debug("Reloading manifest.")
        old_manifest = self.get_manifest(name)
        self._manifests.remove(old_manifest)
        self.load_manifest(old_manifest["path"])

        self._logger.debug("Loading {}.".format(name))
        self.load_plugin(self.get_manifest(name), *args)

        self._logger.debug("Enabling {}.".format(name))
        self.get_plugin(name).enable()

        self._logger.debug("Plugin {} reloaded.".format(name))

    def reload_all_plugins(self, *args) -> None:
        """
        Reloads all initialized plugins
        """
        for manifest in self._manifests[:]:
            if self.get_plugin(manifest["name"]) is not None:
                self.reload_plugin(manifest["name"], *args)

    def unload_plugin(self, name: str) -> None:
        """
        Unloads a specified plugin
        :param name: The name of the plugin
        """
        self._logger.debug("Unloading {}.".format(name))

        self._logger.debug("Removing plugin instance.")
        del self._plugins[name]

        self._logger.debug("Unloading module.")
        del self._modules[name]

        self._logger.debug("Unloading manifest...")
        manifest = self.get_manifest(name)
        self._manifests.remove(manifest)

        self._logger.debug("{} unloaded.".format(name))