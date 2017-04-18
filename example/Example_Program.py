import os

from jigsaw import PluginLoader

# Initialize the main jigsaw loader class
loader = PluginLoader(
    (os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugins")), )  # The folder(s) that plugins will be loaded from
)

# Discover and load all the information required to load plugins
loader.load_manifests()

# Load all plugins
loader.load_plugins()

# Call the enable method on all plugins
loader.enable_all_plugins()
