import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..")))
print(sys.path)

import jigsaw


def test_initializing_jigsaw_with_no_plugin_path_specified():
    j = jigsaw.PluginLoader()
    assert j.plugin_path == os.path.join(os.getcwd(), "plugins")


def test_initializing_jigsaw_with_custom_plugin_path():
    j = jigsaw.PluginLoader(os.path.join(os.getcwd(), "custom_plugins"))
    assert j.plugin_path == os.path.join(os.getcwd(), "custom_plugins")


def test_loading_manifests():
    j = jigsaw.PluginLoader(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")))
    j.load_manifests()
    assert j.get_manifest("Basic Test") is not None
    assert j.get_manifest("Dependency Test") is not None
    assert j.get_manifest("Missing Dependency Test") is not None


def test_getting_manifests():
    j = jigsaw.PluginLoader(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")))
    j.load_manifests()
    assert j.get_manifest("Basic Test") is not None


def test_getting_manifest_for_missing_plugin():
    j = jigsaw.PluginLoader(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")))
    j.load_manifests()
    assert j.get_manifest("This should never exist") is None


def test_loading_specific_manifest():
    j = jigsaw.PluginLoader(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")))
    j.load_manifest(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins", "BasicTest")))
    assert j.get_manifest("Basic Test") is not None


def test_load_plugins():
    j = jigsaw.PluginLoader(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")))
    j.load_manifests()
    j.load_plugins()
    assert j.get_plugin_loaded("Dependency Test")
    assert j.get_plugin_loaded("Basic Test")
    assert not j.get_plugin_loaded("Missing Dependency Test")


def test_load_specific_plugin():
    j = jigsaw.PluginLoader(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")))
    j.load_manifests()
    j.load_plugin(j.get_manifest("Basic Test"))
    assert j.get_plugin_loaded("Basic Test")


def test_loading_dependencies():
    j = jigsaw.PluginLoader(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")))
    j.load_manifests()
    j.load_plugin(j.get_manifest("Dependency Test"))
    assert j.get_plugin_loaded("Dependency Test")
    assert j.get_plugin_loaded("Basic Test")


def test_loading_with_missing_dependencies():
    j = jigsaw.PluginLoader(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")))
    j.load_manifests()
    j.load_plugin(j.get_manifest("Missing Dependency Test"))
    assert not j.get_plugin_loaded("Missing Dependency Test")


def test_getting_plugin():
    j = jigsaw.PluginLoader(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")))
    j.load_manifests()
    j.load_plugin(j.get_manifest("Basic Test"))
    assert isinstance(j.get_plugin("Basic Test"), jigsaw.JigsawPlugin)


def test_getting_missing_plugin():
    j = jigsaw.PluginLoader(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")))
    assert not isinstance(j.get_plugin("This should never exist"), jigsaw.JigsawPlugin)


def test_getting_module():
    j = jigsaw.PluginLoader(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")))
    j.load_manifests()
    j.load_plugin(j.get_manifest("Basic Test"))
    assert issubclass(j.get_module("Basic Test").Plugin, jigsaw.JigsawPlugin)


def test_getting_module_of_missing_plugin():
    j = jigsaw.PluginLoader(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")))
    with pytest.raises(AttributeError):
        assert not issubclass(j.get_module("This should never exist").Plugin, jigsaw.JigsawPlugin)


def test_getting_all_plugins():
    j = jigsaw.PluginLoader(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")))
    j.load_manifests()
    j.load_plugins()
    for item in j.get_all_plugins():
        if item["manifest"]["name"] in ["Missing Dependency Test", "Invalid Baseclass Test", "Error Test"]:
            assert isinstance(item["manifest"], dict)
            assert not isinstance(item["plugin"], jigsaw.JigsawPlugin)
        else:
            assert isinstance(item["manifest"], dict)
            assert isinstance(item["plugin"], jigsaw.JigsawPlugin)


def test_disable_all_plugins():
    j = jigsaw.PluginLoader(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")))
    j.load_manifests()
    j.load_plugins()
    j.disable_all_plugins()


def test_enable_all_plugins():
    j = jigsaw.PluginLoader(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")))
    j.load_manifests()
    j.load_plugins()
    j.enable_all_plugins()


def test_reload_all_plugins():
    j = jigsaw.PluginLoader(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")))
    j.load_manifests()
    j.load_plugins()
    j.reload_all_plugins()


def test_reload_specific_plugin():
    j = jigsaw.PluginLoader(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")))
    j.load_manifests()
    j.load_plugin(j.get_manifest("Basic Test"))
    j.reload_plugin("Basic Test")


def test_load_invalid_plugin_manifest():
    j = jigsaw.PluginLoader(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")))
    j.load_manifest(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins", "InvalidManifestTest")))
    assert j.get_manifest("Invalid Manifest Test") is None


def test_loading_plugin_already_loaded():
    j = jigsaw.PluginLoader(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")))
    j.load_manifests()
    j.load_plugin(j.get_manifest("Basic Test"))
    j.load_plugin(j.get_manifest("Basic Test"))


def test_invalid_baseclass():
    j = jigsaw.PluginLoader(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")))
    j.load_manifests()
    j.load_plugin(j.get_manifest("Invalid Baseclass Test"))
    assert not j.get_plugin_loaded("Invalid Baseclass Test")


def test_error_on_plugin_load():
    j = jigsaw.PluginLoader(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")))
    j.load_manifests()
    j.load_plugin(j.get_manifest("Error Test"))
    assert os.path.isfile(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins", "ErrorTest", "error.log")))


def test_oserror_on_load_plugin_manifest():
    j = jigsaw.PluginLoader(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")))
    os.mkdir(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins", "OSErrorTest", "plugin.json")))
    j.load_manifest(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins", "OSErrorTest")))
    os.rmdir(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins", "OSErrorTest", "plugin.json")))
    assert j.get_manifest("OS Error Test") is None


def test_unload_plugin():
    j = jigsaw.PluginLoader(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")))
    j.load_manifests()
    j.load_plugin(j.get_manifest("Basic Test"))
    j.unload_plugin("Basic Test")
    assert not j.get_plugin_loaded("Basic Test")


def test_reload_specific_manifest():
    j = jigsaw.PluginLoader(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")))
    j.load_manifests()
    j.reload_manifest(j.get_manifest("Basic Test"))
    assert j.get_manifest("Basic Test") is not None


def test_reload_all_manifests():
    j = jigsaw.PluginLoader(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")))
    j.load_manifests()
    j.reload_all_manifests()
    assert j.get_manifest("Basic Test") is not None
