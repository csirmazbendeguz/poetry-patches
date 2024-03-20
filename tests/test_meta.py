from pathlib import Path

from poetry_patches.state.meta import Meta
from tests.conftest import assert_meta


def test_set_backup(meta: Meta, meta_path: Path) -> None:
    meta.load()
    meta.set_backup("/a/b/c", "/d/e/f")
    meta.dump()

    assert_meta(meta_path, {"backups": {"/a/b/c": "/d/e/f"}})


def test_clear(meta: Meta, meta_path: Path) -> None:
    meta.clear()
    assert_meta(meta_path, {"backups": {}})
