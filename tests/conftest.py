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
def meta(tmp_path: Path) -> Meta:
    return Meta(tmp_path / "meta.json")


@pytest.fixture
def backup(meta: Meta, tmp_path) -> Backup:
    backups = tmp_path / "backups"
    backups.mkdir(parents=True, exist_ok=True)
    return Backup(meta, backups)


@pytest.fixture
def poetry_patcher(io: IO, backup: Backup) -> PoetryPatcher:
    return PoetryPatcher(None, io, backup)
