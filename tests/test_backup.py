import json
from pathlib import Path

from poetry_patches.state.backup import Backup
from poetry_patches.state.meta import Meta


def test_backup__edit_or_delete(tmp_path: Path):
    file = tmp_path / "edit_or_delete.txt"
    file.write_text("edit_or_delete")

    meta = tmp_path / "meta.json"
    backups = tmp_path / "backups"
    backups.mkdir(parents=True, exist_ok=True)

    Backup(Meta(meta), backups).edit_or_delete(file)

    backups = list(backups.glob("*"))
    assert len(backups) == 1
    backup = backups[0]
    assert backup.name.startswith("edit_or_delete_")
    assert backup.name.endswith(".txt")
    assert backup.read_text() == "edit_or_delete"
    assert meta.read_text() == json.dumps(
        {"backups": {str(file.resolve()): str(backup.resolve())}}, indent=4
    )


def test_backup__create_or_rename(tmp_path: Path):
    file = tmp_path / "create_or_rename.txt"
    file.write_text("create_or_rename")

    meta = tmp_path / "meta.json"
    backups = tmp_path / "backups"
    backups.mkdir(parents=True, exist_ok=True)

    Backup(Meta(meta), backups).create_or_rename(file)

    assert not (backups / "create_or_rename.txt").exists()
    assert meta.read_text() == json.dumps(
        {"backups": {str(file.resolve()): None}}, indent=4
    )
