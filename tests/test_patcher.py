from pathlib import Path

import pytest
from cleo.application import Application
from cleo.io.io import IO
from cleo.io.outputs.output import Verbosity
from poetry.exceptions import PoetryException

from poetry_patches.patcher import PoetryPatcher


PATCHES_DIR = Path("./patches")


@pytest.fixture
def io() -> IO:
    io = Application().create_io()
    io.set_verbosity(Verbosity.DEBUG)
    return io


def get_diffs(dir: Path) -> list[str]:
    return [str(path) for path in dir.glob("*.diff")]


def test_pass(io: IO, tmp_path: Path) -> None:
    patches_dir = PATCHES_DIR / "pass"
    diffs = get_diffs(patches_dir)

    PoetryPatcher(None, io).apply_patches(tmp_path, diffs)

    assert not (tmp_path / "pass.txt").exists()
    assert not (tmp_path / "pass_2.txt").exists()


def test_fail_on_create_if_exists(io: IO, tmp_path: Path) -> None:
    patches_dir = PATCHES_DIR / "fail_on_create_if_exists"
    diffs = get_diffs(patches_dir)

    with pytest.raises(PoetryException):
        PoetryPatcher(None, io).apply_patches(tmp_path, diffs)

    assert (tmp_path / "fail_on_create_if_exists.txt").exists()


def test_fail_on_update_if_doesnt_exist(io: IO, tmp_path: Path) -> None:
    patches_dir = PATCHES_DIR / "fail_on_update_if_doesnt_exist"
    diffs = get_diffs(patches_dir)

    with pytest.raises(PoetryException):
        PoetryPatcher(None, io).apply_patches(tmp_path, diffs)

    assert not (tmp_path / "fail_on_update_if_doesnt_exist.txt").exists()


def test_fail_on_delete_if_doesnt_exist(io: IO, tmp_path: Path) -> None:
    patches_dir = PATCHES_DIR / "fail_on_delete_if_doesnt_exist"
    diffs = get_diffs(patches_dir)

    with pytest.raises(PoetryException):
        PoetryPatcher(None, io).apply_patches(tmp_path, diffs)

    assert not (tmp_path / "fail_on_delete_if_doesnt_exist.txt").exists()


def test_fail_on_rename_if_doesnt_exist(io: IO, tmp_path: Path) -> None:
    patches_dir = PATCHES_DIR / "fail_on_rename_if_doesnt_exist"
    diffs = get_diffs(patches_dir)

    with pytest.raises(PoetryException):
        PoetryPatcher(None, io).apply_patches(tmp_path, diffs)

    assert not (tmp_path / "fail_on_rename_if_doesnt_exist.txt").exists()


def test_fail_on_rename_if_exists(io: IO, tmp_path: Path) -> None:
    patches_dir = PATCHES_DIR / "fail_on_rename_if_exists"
    diffs = get_diffs(patches_dir)

    with pytest.raises(PoetryException):
        PoetryPatcher(None, io).apply_patches(tmp_path, diffs)

    assert (tmp_path / "fail_on_rename_if_exists.txt").exists()
    assert (tmp_path / "fail_on_rename_if_exists_2.txt").exists()
