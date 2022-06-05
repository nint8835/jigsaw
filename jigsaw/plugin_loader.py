import importlib.util
import logging
import os
import traceback
from importlib.abc import Loader
from types import ModuleType
from typing import Any, Dict, List, Optional, Tuple, Type, Union

import tomli

from .plugin import JigsawPlugin
from .types import Manifest


class PluginLoader:
    """
    The main plugin loader class
    """

    def __init__(
        self,
        plugin_paths: Tuple[str, ...] = (),
        log_level: int = logging.INFO,
        plugin_class: Type[JigsawPlugin] = JigsawPlugin,
    ):
        """
        Initializes the plugin loader

        :param plugin_paths: Paths to load plugins from
        :param log_level: Log level
        :param plugin_class: Parent class of all plugins
        """
        logging.basicConfig(
            format="{%(asctime)s} (%(name)s) [%(levelname)s]: %(message)s",
            datefmt="%x, %X",
            level=log_level,
        )
        self._logger = logging.getLogger("Jigsaw")

        if len(plugin_paths) == 0:
            self.plugin_paths: Tuple[str, ...] = (os.path.join(os.getcwd(), "plugins"),)
            self._logger.debug(
                "No plugin path specified, using {}.".format(self.plugin_paths)
            )
        else:
            self.plugin_paths = plugin_paths
            self._logger.debug(
                "Using specified plugin paths of {}.".format(
                    ", ".join(self.plugin_paths)
                )
            )

        self._plugin_class = plugin_class

        self._manifests: List[Manifest] = []
        self._plugins: Dict[str, Any] = {}
        self._modules: Dict[str, ModuleType] = {}

    def load_manifests(self) -> None:
        """
        Loads all plugin manifests on the plugin path
        """
        for path in self.plugin_paths:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    self.load_manifest(item_path)

    def load_manifest(self, path: str) -> None:
        """
        Loads a plugin manifest from a given path

        :param path: The folder to load the plugin manifest from
        """
        manifest_path = os.path.join(path, "plugin.toml")
        self._logger.debug(
            "Attempting to load plugin manifest from {}.".format(manifest_path)
        )
        try:
            with open(manifest_path, "rb") as f:
                manifest = tomli.load(f)

            manifest.get("meta", {})["path"] = path
            self._manifests.append(Manifest.parse_obj(manifest))
            self._logger.debug("Loaded plugin manifest from {}.".format(manifest_path))
        except ValueError:
            self._logger.exception(
                "Failed to decode plugin manifest at {}.".format(manifest_path)
            )
        except (OSError, IOError) as e:
            self._logger.exception(
                "Failed to load plugin manifest at {}.".format(manifest_path)
            )

    def get_manifest(self, plugin_id: str) -> Optional[Manifest]:
        """
        Gets the manifest for a specified plugin

        :param plugin_id: The ID of the plugin
        :return: The manifest for the specified plugin
        """
        for manifest in self._manifests:
            if manifest.meta.id == plugin_id:
                return manifest
        return None

    def get_plugin_loaded(self, plugin_id: str) -> bool:
        """
        Returns if a given plugin is loaded

        :param plugin_id: The plugin to check to loaded status for
        :return: Whether the specified plugin is loaded
        """
        return plugin_id in self._plugins

    def load_plugin(self, manifest: Manifest, *args: Any) -> None:
        """
        Loads a plugin from the given manifest

        :param manifest: The manifest to use to load the plugin
        :param args: Arguments to pass to the plugin
        """
        if self.get_plugin_loaded(manifest.meta.id):
            self._logger.debug("Plugin {} is already loaded.".format(manifest.meta.id))
            return
        try:
            self._logger.debug("Attempting to load plugin {}.".format(manifest.meta.id))
            for dependency in manifest.meta.dependencies:
                if not self.get_plugin_loaded(dependency):
                    self._logger.debug(
                        "Must load dependency {} first.".format(dependency)
                    )
                    if self.get_manifest(dependency) is None:
                        self._logger.error(
                            "Dependency {} could not be found.".format(dependency)
                        )
                    else:
                        dep_manifest = self.get_manifest(dependency)
                        assert dep_manifest is not None

                        self.load_plugin(dep_manifest, *args)

            not_loaded = [
                i for i in manifest.meta.dependencies if not self.get_plugin_loaded(i)
            ]
            if len(not_loaded) != 0:
                self._logger.error(
                    "Plugin {} failed to load due to missing dependencies. Dependencies: {}".format(
                        manifest.meta.id, ", ".join(not_loaded)
                    )
                )
                return

            spec = importlib.util.spec_from_file_location(
                manifest.meta.name.replace(" ", "_"),
                os.path.join(manifest.meta.path, manifest.meta.main_file),
            )
            assert spec is not None

            module = importlib.util.module_from_spec(spec)
            assert isinstance(spec.loader, Loader)
            spec.loader.exec_module(module)

            module_class = manifest.meta.main_class
            plugin_class = getattr(module, module_class)
            if issubclass(plugin_class, self._plugin_class):
                plugin = plugin_class(manifest, *args)
            else:
                self._logger.error(
                    "Failed to load {} due to invalid baseclass.".format(
                        manifest.meta.id
                    )
                )
                return
            self._plugins[manifest.meta.id] = plugin
            self._modules[manifest.meta.id] = module

            self._logger.debug("Plugin {} loaded.".format(manifest.meta.name))

        except:
            exc_path = os.path.join(manifest.meta.path, "error.log")
            with open(exc_path, "w") as f:
                f.write(traceback.format_exc(5))
            self._logger.error(
                "Failed to load plugin {}. Error log written to {}.".format(
                    manifest.meta.id, exc_path
                )
            )

    def load_plugins(self, *args: Any) -> None:
        """
        Loads all plugins

        :param args: Arguments to pass to the plugins
        """
        for manifest in self._manifests:
            self.load_plugin(manifest, *args)

    def get_plugin(self, id: str) -> Optional[Any]:
        """
        Gets a loaded plugin

        :param id: ID of the plugin
        :return: The plugin
        """
        try:
            return self._plugins[id]
        except KeyError:
            return None

    def get_module(self, id: str) -> Optional[ModuleType]:
        """
        Gets the module for a plugin

        :param id: ID of the plugin
        :return: The module
        """
        try:
            return self._modules[id]
        except KeyError:
            return None

    def get_all_plugins(
        self,
    ) -> List[Dict[str, Union[None, Manifest, ModuleType, Any]]]:
        """
        Gets all loaded plugins

        :return: List of all plugins
        """
        return [
            {
                "manifest": i,
                "plugin": self.get_plugin(i.meta.id),
                "module": self.get_module(i.meta.id),
            }
            for i in self._manifests
        ]

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

    def reload_manifest(self, manifest: Manifest) -> None:
        """
        Reloads a manifest from the disk
        :param manifest: The manifest to reload
        """
        self._logger.debug("Reloading manifest for {}.".format(manifest.meta.id))
        self._manifests.remove(manifest)
        self.load_manifest(manifest.meta.path)
        self._logger.debug("Manifest reloaded.")

    def reload_all_manifests(self) -> None:
        """
        Reloads all loaded manifests, and loads any new manifests
        """
        self._logger.debug("Reloading all manifests.")
        self._manifests = []
        self.load_manifests()
        self._logger.debug("All manifests reloaded.")

    def reload_plugin(self, id: str, *args: Any) -> None:
        """
        Reloads a given plugin

        :param id: The ID of the plugin
        :param args: The args to pass to the plugin
        """
        self._logger.debug("Reloading {}.".format(id))

        self._logger.debug("Disabling {}.".format(id))
        plugin = self.get_plugin(id)
        assert plugin is not None
        plugin.disable()

        self._logger.debug("Removing plugin instance.")
        del self._plugins[id]

        self._logger.debug("Unloading module.")
        del self._modules[id]

        self._logger.debug("Reloading manifest.")
        old_manifest = self.get_manifest(id)
        assert old_manifest is not None
        self._manifests.remove(old_manifest)
        self.load_manifest(old_manifest.meta.path)

        self._logger.debug("Loading {}.".format(id))
        new_manifest = self.get_manifest(id)
        assert new_manifest is not None
        self.load_plugin(new_manifest, *args)

        self._logger.debug("Enabling {}.".format(id))
        plugin = self.get_plugin(id)
        assert plugin is not None
        plugin.enable()

        self._logger.debug("Plugin {} reloaded.".format(id))

    def reload_all_plugins(self, *args: Any) -> None:
        """
        Reloads all initialized plugins
        """
        for manifest in self._manifests[:]:
            if self.get_plugin(manifest.meta.name) is not None:
                self.reload_plugin(manifest.meta.name, *args)

    def unload_plugin(self, id: str) -> None:
        """
        Unloads a specified plugin
        :param id: The ID of the plugin
        """
        self._logger.debug("Unloading {}.".format(id))

        self._logger.debug("Removing plugin instance.")
        del self._plugins[id]

        self._logger.debug("Unloading module.")
        del self._modules[id]

        self._logger.debug("Unloading manifest...")
        manifest = self.get_manifest(id)
        assert manifest is not None
        self._manifests.remove(manifest)

        self._logger.debug("{} unloaded.".format(id))

    def quickload(self, *args: Any) -> None:
        """
        Loads all manifests, loads all plugins, and then enables all plugins
        :param args: The args to pass to the plugin
        """
        self.load_manifests()
        self.load_plugins(args)
        self.enable_all_plugins()
