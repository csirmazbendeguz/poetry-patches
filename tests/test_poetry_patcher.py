from pathlib import Path

import pytest

from poetry_patches.patcher import PoetryPatcher
from tests import PATCHES
from tests.conftest import assert_meta


def get_diffs(directory: Path) -> list[str]:
    return [str(path) for path in directory.glob("*.diff")]


class TestPoetryPatcher:
    @pytest.fixture(autouse=True)
    def set_up(
        self,
        poetry_patcher: PoetryPatcher,
        tmp_path: Path,
        backups_path: Path,
        meta_path: Path,
    ) -> None:
        self.poetry_patcher = poetry_patcher
        self.tmp_path = tmp_path
        self.backups_path = backups_path
        self.meta_path = meta_path

    def test_pass(self) -> None:
        diffs = get_diffs(PATCHES / "pass")

        self.poetry_patcher.apply_patches(self.tmp_path, diffs)

        file_1 = self.tmp_path / "pass.txt"
        file_2 = self.tmp_path / "pass_2.txt"
        assert not file_1.exists()
        assert not file_2.exists()

        # backups
        assert list(self.backups_path.glob("*")) == []
        assert_meta(
            self.meta_path,
            {"backups": {str(file_1.resolve()): None, str(file_2.resolve()): None}},
        )

    def test_fail_on_create_if_exists(self) -> None:
        diffs = get_diffs(PATCHES / "fail_on_create_if_exists")

        self.poetry_patcher.apply_patches(self.tmp_path, diffs)

        file = self.tmp_path / "fail_on_create_if_exists.txt"
        assert 0 < self.poetry_patcher.errors
        assert file.exists()

        # backups
        assert list(self.backups_path.glob("*")) == []
        assert_meta(self.meta_path, {"backups": {str(file.resolve()): None}})

    def test_fail_on_create_if_exists_file_exists(self) -> None:
        file = self.tmp_path / "fail_on_create_if_exists_file_exists.txt"
        file.write_text("fail_on_create_if_exists_file_exists")

        diffs = get_diffs(PATCHES / "fail_on_create_if_exists_file_exists")

        self.poetry_patcher.apply_patches(self.tmp_path, diffs)

        assert 0 < self.poetry_patcher.errors
        assert file.read_text() == "fail_on_create_if_exists_file_exists"

        # backups
        assert list(self.backups_path.glob("*")) == []
        assert not self.meta_path.exists()

    def test_fail_on_update_if_doesnt_exist(self) -> None:
        diffs = get_diffs(PATCHES / "fail_on_update_if_doesnt_exist")

        self.poetry_patcher.apply_patches(self.tmp_path, diffs)

        assert 0 < self.poetry_patcher.errors
        assert not (self.tmp_path / "fail_on_update_if_doesnt_exist.txt").exists()

        # backups
        assert list(self.backups_path.glob("*")) == []
        assert not self.meta_path.exists()

    def test_fail_on_delete_if_doesnt_exist(self) -> None:
        diffs = get_diffs(PATCHES / "fail_on_delete_if_doesnt_exist")

        self.poetry_patcher.apply_patches(self.tmp_path, diffs)

        assert 0 < self.poetry_patcher.errors
        assert not (self.tmp_path / "fail_on_delete_if_doesnt_exist.txt").exists()

        # backups
        assert list(self.backups_path.glob("*")) == []
        assert not self.meta_path.exists()

    def test_fail_on_rename_if_doesnt_exist(self) -> None:
        diffs = get_diffs(PATCHES / "fail_on_rename_if_doesnt_exist")

        self.poetry_patcher.apply_patches(self.tmp_path, diffs)

        assert 0 < self.poetry_patcher.errors
        assert not (self.tmp_path / "fail_on_rename_if_doesnt_exist.txt").exists()

        # backups
        assert list(self.backups_path.glob("*")) == []
        assert not self.meta_path.exists()

    def test_fail_on_rename_if_exists(self) -> None:
        diffs = get_diffs(PATCHES / "fail_on_rename_if_exists")

        self.poetry_patcher.apply_patches(self.tmp_path, diffs)

        file_1 = self.tmp_path / "fail_on_rename_if_exists.txt"
        file_2 = self.tmp_path / "fail_on_rename_if_exists_2.txt"
        assert 0 < self.poetry_patcher.errors
        assert file_1.exists()
        assert file_2.exists()

        # backups
        assert list(self.backups_path.glob("*")) == []
        assert_meta(
            self.meta_path,
            {"backups": {str(file_1.resolve()): None, str(file_2.resolve()): None}},
        )

    def test_pass_on_line_remove(self) -> None:
        diffs = get_diffs(PATCHES / "pass_on_line_remove")

        self.poetry_patcher.apply_patches(self.tmp_path, diffs)

        file = self.tmp_path / "pass_on_line_remove.txt"
        assert file.exists()
        assert "nostrud" not in file.read_text()

        # backups
        assert list(self.backups_path.glob("*")) == []
        assert_meta(self.meta_path, {"backups": {str(file.resolve()): None}})

    def test_pass_on_line_add(self) -> None:
        diffs = get_diffs(PATCHES / "pass_on_line_add")

        self.poetry_patcher.apply_patches(self.tmp_path, diffs)

        file = self.tmp_path / "pass_on_line_add.txt"
        assert file.exists()
        assert "velit" in file.read_text()

        # backups
        assert list(self.backups_path.glob("*")) == []
        assert_meta(self.meta_path, {"backups": {str(file.resolve()): None}})

    def test_pass_on_line_break(self) -> None:
        diffs = get_diffs(PATCHES / "pass_on_line_break")

        self.poetry_patcher.apply_patches(self.tmp_path, diffs)

        file = self.tmp_path / "pass_on_line_break.txt"
        assert file.exists()
        assert "aliqua" in file.read_text()

        # backups
        assert list(self.backups_path.glob("*")) == []
        assert_meta(self.meta_path, {"backups": {str(file.resolve()): None}})

    def test_pass_on_line_adds(self) -> None:
        diffs = get_diffs(PATCHES / "pass_on_line_adds")

        self.poetry_patcher.apply_patches(self.tmp_path, diffs)

        file = self.tmp_path / "pass_on_line_adds.txt"
        assert file.exists()
        text = file.read_text()
        assert "maxime" in text
        assert "delectus" in text

        # backups
        assert list(self.backups_path.glob("*")) == []
        assert_meta(self.meta_path, {"backups": {str(file.resolve()): None}})

    def test_pass_on_rename_and_update(self) -> None:
        diffs = get_diffs(PATCHES / "pass_on_rename_and_update")

        self.poetry_patcher.apply_patches(self.tmp_path, diffs)

        file_1 = self.tmp_path / "pass_on_rename_and_update.txt"
        file_2 = self.tmp_path / "pass_on_rename_and_update_2.txt"
        assert not file_1.exists()
        assert file_2.exists()
        text = file_2.read_text()
        assert "labore" not in text
        assert "minim" not in text
        assert "veniam" not in text

        # backups
        assert list(self.backups_path.glob("*")) == []
        assert_meta(
            self.meta_path,
            {"backups": {str(file_1.resolve()): None, str(file_2.resolve()): None}},
        )
