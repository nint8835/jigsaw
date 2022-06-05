from typing import List, Optional

from pydantic import BaseModel


class ManifestMeta(BaseModel):
    id: str
    name: str

    version: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
    dependencies: List[str] = []
    main_file: str = "__init__.py"
    main_class: str = "Plugin"
    path: str = ""


class Manifest(BaseModel):
    meta: ManifestMeta
