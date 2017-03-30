from jigsaw import JigsawPlugin


class ExamplePlugin(JigsawPlugin):
    def __init__(self, manifest: dict, *args) -> None:
        super().__init__(manifest, *args)

        print("Hi! I am an example plugin that was just initialized!")

    def enable(self) -> None:
        print("Hi! I am an example plugin that was just enabled!")
