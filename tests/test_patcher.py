from pathlib import Path

import pytest
from cleo.application import Application
from cleo.io.io import IO
from cleo.io.outputs.output import Verbosity

from poetry_patches.patcher import PoetryPatcher


@pytest.fixture
def io() -> IO:
    io = Application().create_io()
    io.set_verbosity(Verbosity.DEBUG)
    return io


def test_apply_patches(io: IO) -> None:
    target_dir = Path("./patches")
    PoetryPatcher(None, io).apply_patches(
        target_dir,
        [
            "./patches/dummy_1.diff",
            "./patches/dummy_2.diff",
            "./patches/dummy_3.diff",
            "./patches/dummy_4.diff",
        ],
    )

    assert not (target_dir / "dummy.txt").exists()
    assert not (target_dir / "dummy_2.txt").exists()
