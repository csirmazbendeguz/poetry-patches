from importlib.metadata import Distribution

from poetry_patches.patcher import PoetryPatcher


def test_patcher():
    distribution = Distribution.at("poetry_patches")
    print("files", distribution.files)
    PoetryPatcher.apply_patches()
