import json
from pathlib import Path

import pytest
from cleo.application import Application
from cleo.io.io import IO
from cleo.io.outputs.output import Verbosity

from poetry_patches.patcher import PoetryPatcher
from poetry_patches.state.backup import Backup
from poetry_patches.state.meta import Meta


@pytest.fixture
def io() -> IO:
    io = Application().create_io()
    io.set_verbosity(Verbosity.DEBUG)
    return io


@pytest.fixture
def meta_path(tmp_path: Path) -> Path:
    return tmp_path / "meta.json"


@pytest.fixture
def meta(meta_path: Path) -> Meta:
    return Meta(meta_path)


@pytest.fixture
def backups_path(tmp_path: Path) -> Path:
    backups = tmp_path / "backups"
    backups.mkdir(parents=True, exist_ok=True)
    return backups


@pytest.fixture
def backup(meta: Meta, backups_path: Path) -> Backup:
    return Backup(meta, backups_path)


@pytest.fixture
def poetry_patcher(io: IO, backup: Backup) -> PoetryPatcher:
    return PoetryPatcher(None, io, backup)


def assert_meta(path: Path, obj) -> None:
    assert path.read_text() == json.dumps(obj, indent=4)
