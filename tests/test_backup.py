import json
from pathlib import Path

from poetry_patches.state.backup import Backup


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
    assert meta_path.read_text() == json.dumps(
        {"backups": {str(file.resolve()): str(backup.resolve())}}, indent=4
    )


def test_create_or_rename(
    backup: Backup, backups: Path, meta_path: Path, tmp_path: Path
) -> None:
    file = tmp_path / "create_or_rename.txt"
    file.write_text("create_or_rename")

    backup.create_or_rename(file)

    assert list(backups.glob("*")) == []
    assert meta_path.read_text() == json.dumps(
        {"backups": {str(file.resolve()): None}}, indent=4
    )


def test_revert(backup: Backup, backups: Path, meta_path: Path, tmp_path: Path) -> None:
    file = tmp_path / "revert.txt"
    file.write_text("revert")

    backup.create_or_rename(file)
    backup.revert()

    assert not file.exists()
    assert meta_path.read_text() == json.dumps({"backups": {}}, indent=4)
    assert list(backups.glob("*")) == []
