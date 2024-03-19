import copy
import json
from pathlib import Path

from poetry_patches import META


class Meta:
    """
    A class for the `.poetry-caches/meta.json` file.
    """

    DEFAULT = {"backups": {}}

    def __init__(self, meta: Path):
        self.meta = meta
        self.data = copy.deepcopy(self.DEFAULT)

    @classmethod
    def get(cls):
        return cls(META)

    def load(self) -> None:
        if self.meta.exists():
            text = self.meta.read_text()
            self.data = json.loads(text)

    def dump(self) -> None:
        text = json.dumps(self.data, indent=4)
        self.meta.write_text(text)

    def set_backup(self, key: str, value: str | None) -> None:
        self.data["backups"][key] = value

    def has_backup(self, key: str) -> bool:
        return key in self.data["backups"]
