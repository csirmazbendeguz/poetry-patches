from pathlib import Path

from poetry_patches.state.backup import Backup
from tests.conftest import assert_meta


def test_edit_or_delete(
    backup: Backup, backups: Path, meta_path: Path, tmp_path: Path
) -> None:
    file = tmp_path / "edit_or_delete.txt"
    file.write_text("edit_or_delete")

    backup.edit_or_delete(file)

    backups = list(backups.glob("*"))
    assert len(backups) == 1
    backup = backups[0]
    assert backup.name.startswith("edit_or_delete_")
    assert backup.name.endswith(".txt")
    assert backup.read_text() == "edit_or_delete"
    assert_meta(meta_path, {"backups": {str(file.resolve()): str(backup.resolve())}})


def test_create_or_rename(
    backup: Backup, backups: Path, meta_path: Path, tmp_path: Path
) -> None:
    file = tmp_path / "create_or_rename.txt"
    file.write_text("create_or_rename")

    backup.create_or_rename(file)

    assert list(backups.glob("*")) == []
    assert_meta(meta_path, {"backups": {str(file.resolve()): None}})


def test_revert(backup: Backup, backups: Path, meta_path: Path, tmp_path: Path) -> None:
    file = tmp_path / "revert.txt"
    file.write_text("revert")

    backup.create_or_rename(file)
    backup.revert()

    assert not file.exists()
    assert list(backups.glob("*")) == []
    assert_meta(meta_path, {"backups": {}})
