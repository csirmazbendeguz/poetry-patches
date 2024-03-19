import json
from pathlib import Path

from poetry_patches.state.meta import Meta


def test_meta__set_backup(tmp_path: Path) -> None:
    path = tmp_path / "meta.json"

    meta = Meta(path)
    meta.load()
    meta.set_backup("/a/b/c", "/d/e/f")
    meta.dump()

    assert path.read_text() == json.dumps({"backups": {"/a/b/c": "/d/e/f"}}, indent=4)
