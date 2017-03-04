plugin.json (Plugin Manifest)
=============================

The plugin.json file (also known as the plugin manifest) is the file that defines all information a plugin requires to be loaded.
While jigsaw specifies it's own options that go in the manifest, the software that implements jigsaw is welcome to implement their own.

The options specified by jigsaw are:

:name: Required. The name of the plugin. This value **MUST** be unique.
:dependencies: A list of strings containing names of plugins that will be loaded before this plugin is loaded. If any plugins listed cannot be found or loaded, this plugin will not be loaded.
:module_name: The name the plugin will be imported as. Used for internal import workings. Defaults to plugin name with spaces replaced with underscores.
:path: The name of the file that contains the main plugin class. Defaults to __init__.py
:main_class: The main plugin class. Defaults to Plugin

Example plugin.json:

.. highlight:: json
::

    {
        "name": "Example Plugin",
        "dependencies": ["Example Plugin", "Library Plugin"],
        "main_class": "ExamplePlugin"
    }
