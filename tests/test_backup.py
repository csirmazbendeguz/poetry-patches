from pathlib import Path

import pytest

from poetry_patches.state.backup import Backup
from tests.conftest import assert_meta


class TestBackup:
    @pytest.fixture(autouse=True)
    def set_up(
        self, backup: Backup, backups_path: Path, meta_path: Path, tmp_path: Path
    ) -> None:
        self.backup = backup
        self.backups_path = backups_path
        self.meta_path = meta_path
        self.tmp_path = tmp_path

    def test_edit_or_delete(self) -> None:
        file = self.tmp_path / "edit_or_delete.txt"
        file.write_text("1")

        self.backup.edit_or_delete(file)
        file.write_text("2")

        backups = list(self.backups_path.glob("*"))
        assert len(backups) == 1
        backup = backups[0]
        assert backup.name.startswith("edit_or_delete_")
        assert backup.name.endswith(".txt")
        assert backup.read_text() == "1"
        assert_meta(
            self.meta_path, {"backups": {str(file.resolve()): str(backup.resolve())}}
        )

    def test_create_or_rename(self) -> None:
        file = self.tmp_path / "create_or_rename.txt"
        file.write_text("create_or_rename")

        self.backup.create_or_rename(file)

        assert list(self.backups_path.glob("*")) == []
        assert_meta(self.meta_path, {"backups": {str(file.resolve()): None}})

    def test_revert_create_or_rename(self) -> None:
        file = self.tmp_path / "revert_create_or_rename.txt"
        file.write_text("revert_create_or_rename")

        self.backup.create_or_rename(file)
        self.backup.revert()

        assert not file.exists()
        assert list(self.backups_path.glob("*")) == []
        assert_meta(self.meta_path, {"backups": {}})

    def test_revert_edit_or_delete(self) -> None:
        file = self.tmp_path / "revert_edit_or_delete.txt"
        file.write_text("1")

        self.backup.edit_or_delete(file)
        file.write_text("2")
        self.backup.revert()

        assert file.read_text() == "1"
        assert list(self.backups_path.glob("*")) == []
        assert_meta(self.meta_path, {"backups": {}})
