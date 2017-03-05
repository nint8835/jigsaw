from jigsaw import JigsawPlugin


class Plugin(JigsawPlugin):
    def __init__(self, manifest: dict, *args) -> None:
        super(Plugin, self).__init__(manifest, *args)
        x = 1/0
