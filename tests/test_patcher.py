import json
from pathlib import Path

import pytest
from cleo.application import Application
from cleo.io.io import IO
from cleo.io.outputs.output import Verbosity
from poetry.exceptions import PoetryException

from poetry_patches.patcher import PoetryPatcher

PATCHES_DIR = Path("./patches")


def get_diffs(dir: Path) -> list[str]:
    return [str(path) for path in dir.glob("*.diff")]


def test_pass(poetry_patcher: PoetryPatcher, tmp_path: Path) -> None:
    patches_dir = PATCHES_DIR / "pass"
    diffs = get_diffs(patches_dir)

    poetry_patcher.apply_patches(tmp_path, diffs)

    assert not (tmp_path / "pass.txt").exists()
    assert not (tmp_path / "pass_2.txt").exists()
    assert not (tmp_path / "backups" / "pass.txt").exists()
    assert not (tmp_path / "backups" / "pass_2.txt").exists()
    assert (tmp_path / "meta.json").read_text() == json.dumps(
        {
            "backups": {
                str((tmp_path / "pass.txt").resolve()): None,
                str((tmp_path / "pass_2.txt").resolve()): None,
            }
        },
        indent=4,
    )


def test_fail_on_create_if_exists(
    poetry_patcher: PoetryPatcher, tmp_path: Path
) -> None:
    patches_dir = PATCHES_DIR / "fail_on_create_if_exists"
    diffs = get_diffs(patches_dir)

    with pytest.raises(PoetryException):
        poetry_patcher.apply_patches(tmp_path, diffs)

    assert (tmp_path / "fail_on_create_if_exists.txt").exists()


def test_fail_on_update_if_doesnt_exist(
    poetry_patcher: PoetryPatcher, tmp_path: Path
) -> None:
    patches_dir = PATCHES_DIR / "fail_on_update_if_doesnt_exist"
    diffs = get_diffs(patches_dir)

    with pytest.raises(PoetryException):
        poetry_patcher.apply_patches(tmp_path, diffs)

    assert not (tmp_path / "fail_on_update_if_doesnt_exist.txt").exists()


def test_fail_on_delete_if_doesnt_exist(
    poetry_patcher: PoetryPatcher, tmp_path: Path
) -> None:
    patches_dir = PATCHES_DIR / "fail_on_delete_if_doesnt_exist"
    diffs = get_diffs(patches_dir)

    with pytest.raises(PoetryException):
        poetry_patcher.apply_patches(tmp_path, diffs)

    assert not (tmp_path / "fail_on_delete_if_doesnt_exist.txt").exists()


def test_fail_on_rename_if_doesnt_exist(
    poetry_patcher: PoetryPatcher, tmp_path: Path
) -> None:
    patches_dir = PATCHES_DIR / "fail_on_rename_if_doesnt_exist"
    diffs = get_diffs(patches_dir)

    with pytest.raises(PoetryException):
        poetry_patcher.apply_patches(tmp_path, diffs)

    assert not (tmp_path / "fail_on_rename_if_doesnt_exist.txt").exists()


def test_fail_on_rename_if_exists(
    poetry_patcher: PoetryPatcher, tmp_path: Path
) -> None:
    patches_dir = PATCHES_DIR / "fail_on_rename_if_exists"
    diffs = get_diffs(patches_dir)

    with pytest.raises(PoetryException):
        poetry_patcher.apply_patches(tmp_path, diffs)

    assert (tmp_path / "fail_on_rename_if_exists.txt").exists()
    assert (tmp_path / "fail_on_rename_if_exists_2.txt").exists()


def test_pass_on_line_remove(poetry_patcher: PoetryPatcher, tmp_path: Path) -> None:
    patches_dir = PATCHES_DIR / "pass_on_line_remove"
    diffs = get_diffs(patches_dir)

    poetry_patcher.apply_patches(tmp_path, diffs)

    path = tmp_path / "pass_on_line_remove.txt"
    assert path.exists()
    assert "nostrud" not in path.read_text()


def test_pass_on_line_add(poetry_patcher: PoetryPatcher, tmp_path: Path) -> None:
    patches_dir = PATCHES_DIR / "pass_on_line_add"
    diffs = get_diffs(patches_dir)

    poetry_patcher.apply_patches(tmp_path, diffs)

    path = tmp_path / "pass_on_line_add.txt"
    assert path.exists()
    assert "velit" in path.read_text()


def test_pass_on_line_break(poetry_patcher: PoetryPatcher, tmp_path: Path) -> None:
    patches_dir = PATCHES_DIR / "pass_on_line_break"
    diffs = get_diffs(patches_dir)

    poetry_patcher.apply_patches(tmp_path, diffs)

    path = tmp_path / "pass_on_line_break.txt"
    assert path.exists()
    assert "aliqua" in path.read_text()


def test_pass_on_line_adds(poetry_patcher: PoetryPatcher, tmp_path: Path) -> None:
    patches_dir = PATCHES_DIR / "pass_on_line_adds"
    diffs = get_diffs(patches_dir)

    poetry_patcher.apply_patches(tmp_path, diffs)

    path = tmp_path / "pass_on_line_adds.txt"
    assert path.exists()
    text = path.read_text()
    assert "maxime" in text
    assert "delectus" in text
