import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..")))
print(sys.path)

import jigsaw


def test_initializing_jigsaw_with_no_plugin_path_specified():
    j = jigsaw.PluginLoader()
    assert j.plugin_paths == (os.path.join(os.getcwd(), "plugins"), )


def test_initializing_jigsaw_with_custom_plugin_path():
    j = jigsaw.PluginLoader((os.path.join(os.getcwd(), "custom_plugins"),))
    assert j.plugin_paths == (os.path.join(os.getcwd(), "custom_plugins"), )


def test_loading_manifests():
    j = jigsaw.PluginLoader((os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")),))
    j.load_manifests()
    assert j.get_manifest("tests.basic") is not None
    assert j.get_manifest("tests.dependency") is not None
    assert j.get_manifest("tests.missing_dependency") is not None


def test_getting_manifests():
    j = jigsaw.PluginLoader((os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")),))
    j.load_manifests()
    assert j.get_manifest("tests.basic") is not None


def test_getting_manifest_for_missing_plugin():
    j = jigsaw.PluginLoader((os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")),))
    j.load_manifests()
    assert j.get_manifest("This should never exist") is None


def test_loading_specific_manifest():
    j = jigsaw.PluginLoader((os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")),))
    j.load_manifest(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins", "BasicTest")))
    assert j.get_manifest("tests.basic") is not None


def test_load_plugins():
    j = jigsaw.PluginLoader((os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")),))
    j.load_manifests()
    j.load_plugins()
    assert j.get_plugin_loaded("tests.dependency")
    assert j.get_plugin_loaded("tests.basic")
    assert not j.get_plugin_loaded("tests.missing_dependency")


def test_load_specific_plugin():
    j = jigsaw.PluginLoader((os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")),))
    j.load_manifests()
    j.load_plugin(j.get_manifest("tests.basic"))
    assert j.get_plugin_loaded("tests.basic")


def test_loading_dependencies():
    j = jigsaw.PluginLoader((os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")),))
    j.load_manifests()
    j.load_plugin(j.get_manifest("tests.dependency"))
    assert j.get_plugin_loaded("tests.dependency")
    assert j.get_plugin_loaded("tests.basic")


def test_loading_with_missing_dependencies():
    j = jigsaw.PluginLoader((os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")),))
    j.load_manifests()
    j.load_plugin(j.get_manifest("tests.missing_dependency"))
    assert not j.get_plugin_loaded("tests.missing_dependency")


def test_getting_plugin():
    j = jigsaw.PluginLoader((os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")),))
    j.load_manifests()
    j.load_plugin(j.get_manifest("tests.basic"))
    assert isinstance(j.get_plugin("tests.basic"), jigsaw.JigsawPlugin)


def test_getting_missing_plugin():
    j = jigsaw.PluginLoader((os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")),))
    assert not isinstance(j.get_plugin("This should never exist"), jigsaw.JigsawPlugin)


def test_getting_module():
    j = jigsaw.PluginLoader((os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")),))
    j.load_manifests()
    j.load_plugin(j.get_manifest("tests.basic"))
    assert issubclass(j.get_module("tests.basic").Plugin, jigsaw.JigsawPlugin)


def test_getting_module_of_missing_plugin():
    j = jigsaw.PluginLoader((os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")),))
    with pytest.raises(AttributeError):
        assert not issubclass(j.get_module("This should never exist").Plugin, jigsaw.JigsawPlugin)


def test_getting_all_plugins():
    j = jigsaw.PluginLoader((os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")),))
    j.load_manifests()
    j.load_plugins()
    for item in j.get_all_plugins():
        if item["manifest"].meta.id in ["tests.missing_dependency", "tests.invalid_baseclass", "tests.error"]:
            assert isinstance(item["manifest"], jigsaw.Manifest)
            assert not isinstance(item["plugin"], jigsaw.JigsawPlugin)
        else:
            assert isinstance(item["manifest"], jigsaw.Manifest)
            assert isinstance(item["plugin"], jigsaw.JigsawPlugin)


def test_disable_all_plugins():
    j = jigsaw.PluginLoader((os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")),))
    j.load_manifests()
    j.load_plugins()
    j.disable_all_plugins()


def test_enable_all_plugins():
    j = jigsaw.PluginLoader((os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")),))
    j.load_manifests()
    j.load_plugins()
    j.enable_all_plugins()


def test_reload_all_plugins():
    j = jigsaw.PluginLoader((os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")),))
    j.load_manifests()
    j.load_plugins()
    j.reload_all_plugins()


def test_reload_specific_plugin():
    j = jigsaw.PluginLoader((os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")),))
    j.load_manifests()
    j.load_plugin(j.get_manifest("tests.basic"))
    j.reload_plugin("tests.basic")


def test_load_invalid_plugin_manifest():
    j = jigsaw.PluginLoader((os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")),))
    j.load_manifest(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins", "InvalidManifestTest")))
    assert j.get_manifest("Invalid Manifest Test") is None


def test_loading_plugin_already_loaded():
    j = jigsaw.PluginLoader((os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")),))
    j.load_manifests()
    j.load_plugin(j.get_manifest("tests.basic"))
    j.load_plugin(j.get_manifest("tests.basic"))


def test_invalid_baseclass():
    j = jigsaw.PluginLoader((os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")),))
    j.load_manifests()
    j.load_plugin(j.get_manifest("tests.invalid_baseclass"))
    assert not j.get_plugin_loaded("tests.invalid_baseclass")


def test_error_on_plugin_load():
    j = jigsaw.PluginLoader((os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")),))
    j.load_manifests()
    j.load_plugin(j.get_manifest("tests.error"))
    assert os.path.isfile(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins", "ErrorTest", "error.log")))


def test_oserror_on_load_plugin_manifest():
    j = jigsaw.PluginLoader((os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")),))
    os.mkdir(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins", "OSErrorTest", "plugin.toml")))
    j.load_manifest(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins", "OSErrorTest")))
    os.rmdir(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins", "OSErrorTest", "plugin.toml")))
    assert j.get_manifest("OS Error Test") is None


def test_unload_plugin():
    j = jigsaw.PluginLoader((os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")),))
    j.load_manifests()
    j.load_plugin(j.get_manifest("tests.basic"))
    j.unload_plugin("tests.basic")
    assert not j.get_plugin_loaded("tests.basic")


def test_reload_specific_manifest():
    j = jigsaw.PluginLoader((os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")),))
    j.load_manifests()
    j.reload_manifest(j.get_manifest("tests.basic"))
    assert j.get_manifest("tests.basic") is not None


def test_reload_all_manifests():
    j = jigsaw.PluginLoader((os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")),))
    j.load_manifests()
    j.reload_all_manifests()
    assert j.get_manifest("tests.basic") is not None


def test_quickload():
    j = jigsaw.PluginLoader((os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "plugins")),))
    j.quickload()
    assert j.get_plugin_loaded("tests.basic")
