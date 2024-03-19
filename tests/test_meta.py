import json
from pathlib import Path

from poetry_patches.state.meta import Meta


def test_set_backup(meta: Meta, meta_path: Path) -> None:
    meta.load()
    meta.set_backup("/a/b/c", "/d/e/f")
    meta.dump()

    assert meta_path.read_text() == json.dumps(
        {"backups": {"/a/b/c": "/d/e/f"}}, indent=4
    )


def test_clear(meta: Meta, meta_path: Path) -> None:
    meta.clear()
    assert meta_path.read_text() == json.dumps({"backups": {}}, indent=4)
