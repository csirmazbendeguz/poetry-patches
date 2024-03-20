from pathlib import Path

from poetry_patches.patcher import PoetryPatcher
from tests import PATCHES
from tests.conftest import assert_meta


def get_diffs(dir: Path) -> list[str]:
    return [str(path) for path in dir.glob("*.diff")]


def test_pass(
    poetry_patcher: PoetryPatcher, tmp_path: Path, backups: Path, meta_path: Path
) -> None:
    diffs = get_diffs(PATCHES / "pass")

    poetry_patcher.apply_patches(tmp_path, diffs)

    assert not (tmp_path / "pass.txt").exists()
    assert not (tmp_path / "pass_2.txt").exists()

    # backups
    assert list(backups.glob("*")) == []
    assert_meta(
        meta_path,
        {
            "backups": {
                str((tmp_path / "pass.txt").resolve()): None,
                str((tmp_path / "pass_2.txt").resolve()): None,
            }
        },
    )


def test_fail_on_create_if_exists(
    poetry_patcher: PoetryPatcher, tmp_path: Path, backups: Path, meta_path: Path
) -> None:
    diffs = get_diffs(PATCHES / "fail_on_create_if_exists")

    poetry_patcher.apply_patches(tmp_path, diffs)

    assert 0 < poetry_patcher.errors
    assert (tmp_path / "fail_on_create_if_exists.txt").exists()

    # backups
    assert list(backups.glob("*")) == []
    assert_meta(
        meta_path,
        {
            "backups": {
                str((tmp_path / "fail_on_create_if_exists.txt").resolve()): None,
            },
        },
    )


def test_fail_on_update_if_doesnt_exist(
    poetry_patcher: PoetryPatcher, tmp_path: Path, backups: Path, meta_path: Path
) -> None:
    diffs = get_diffs(PATCHES / "fail_on_update_if_doesnt_exist")

    poetry_patcher.apply_patches(tmp_path, diffs)

    assert 0 < poetry_patcher.errors
    assert not (tmp_path / "fail_on_update_if_doesnt_exist.txt").exists()

    # backups
    assert list(backups.glob("*")) == []
    assert not meta_path.exists()


def test_fail_on_delete_if_doesnt_exist(
    poetry_patcher: PoetryPatcher, tmp_path: Path, backups: Path, meta_path: Path
) -> None:
    diffs = get_diffs(PATCHES / "fail_on_delete_if_doesnt_exist")

    poetry_patcher.apply_patches(tmp_path, diffs)

    assert 0 < poetry_patcher.errors
    assert not (tmp_path / "fail_on_delete_if_doesnt_exist.txt").exists()

    # backups
    assert list(backups.glob("*")) == []
    assert not meta_path.exists()


def test_fail_on_rename_if_doesnt_exist(
    poetry_patcher: PoetryPatcher, tmp_path: Path, backups: Path, meta_path: Path
) -> None:
    diffs = get_diffs(PATCHES / "fail_on_rename_if_doesnt_exist")

    poetry_patcher.apply_patches(tmp_path, diffs)

    assert 0 < poetry_patcher.errors
    assert not (tmp_path / "fail_on_rename_if_doesnt_exist.txt").exists()

    # backups
    assert list(backups.glob("*")) == []
    assert not meta_path.exists()


def test_fail_on_rename_if_exists(
    poetry_patcher: PoetryPatcher, tmp_path: Path, backups: Path, meta_path: Path
) -> None:
    diffs = get_diffs(PATCHES / "fail_on_rename_if_exists")

    poetry_patcher.apply_patches(tmp_path, diffs)

    assert 0 < poetry_patcher.errors
    assert (tmp_path / "fail_on_rename_if_exists.txt").exists()
    assert (tmp_path / "fail_on_rename_if_exists_2.txt").exists()

    # backups
    assert list(backups.glob("*")) == []
    assert_meta(
        meta_path,
        {
            "backups": {
                str((tmp_path / "fail_on_rename_if_exists.txt").resolve()): None,
                str((tmp_path / "fail_on_rename_if_exists_2.txt").resolve()): None,
            },
        },
    )


def test_pass_on_line_remove(
    poetry_patcher: PoetryPatcher, tmp_path: Path, backups: Path, meta_path: Path
) -> None:
    diffs = get_diffs(PATCHES / "pass_on_line_remove")

    poetry_patcher.apply_patches(tmp_path, diffs)

    path = tmp_path / "pass_on_line_remove.txt"
    assert path.exists()
    assert "nostrud" not in path.read_text()

    # backups
    assert list(backups.glob("*")) == []
    assert_meta(
        meta_path,
        {
            "backups": {
                str((tmp_path / "pass_on_line_remove.txt").resolve()): None,
            },
        },
    )


def test_pass_on_line_add(
    poetry_patcher: PoetryPatcher, tmp_path: Path, backups: Path, meta_path: Path
) -> None:
    diffs = get_diffs(PATCHES / "pass_on_line_add")

    poetry_patcher.apply_patches(tmp_path, diffs)

    path = tmp_path / "pass_on_line_add.txt"
    assert path.exists()
    assert "velit" in path.read_text()

    # backups
    assert list(backups.glob("*")) == []
    assert_meta(
        meta_path,
        {
            "backups": {
                str((tmp_path / "pass_on_line_add.txt").resolve()): None,
            },
        },
    )


def test_pass_on_line_break(
    poetry_patcher: PoetryPatcher, tmp_path: Path, backups: Path, meta_path: Path
) -> None:
    diffs = get_diffs(PATCHES / "pass_on_line_break")

    poetry_patcher.apply_patches(tmp_path, diffs)

    path = tmp_path / "pass_on_line_break.txt"
    assert path.exists()
    assert "aliqua" in path.read_text()

    # backups
    assert list(backups.glob("*")) == []
    assert_meta(
        meta_path,
        {
            "backups": {
                str((tmp_path / "pass_on_line_break.txt").resolve()): None,
            },
        },
    )


def test_pass_on_line_adds(
    poetry_patcher: PoetryPatcher, tmp_path: Path, backups: Path, meta_path: Path
) -> None:
    diffs = get_diffs(PATCHES / "pass_on_line_adds")

    poetry_patcher.apply_patches(tmp_path, diffs)

    path = tmp_path / "pass_on_line_adds.txt"
    assert path.exists()
    text = path.read_text()
    assert "maxime" in text
    assert "delectus" in text

    # backups
    assert list(backups.glob("*")) == []
    assert_meta(
        meta_path,
        {
            "backups": {
                str((tmp_path / "pass_on_line_adds.txt").resolve()): None,
            },
        },
    )
