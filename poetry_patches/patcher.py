import os
from pathlib import Path

import requests
import whatthepatch
from cleo.io.io import IO
from cleo.io.outputs.output import Verbosity
from poetry.poetry import Poetry
from poetry.utils.env import EnvManager
from whatthepatch.exceptions import WhatThePatchException

from poetry_patches.state.backup import Backup


class Diff:
    def __init__(
        self,
        header: whatthepatch.patch.header,
        changes: list[whatthepatch.patch.Change],
        text: str,
    ):
        self.header = header
        self.changes = changes
        self.text = text

    @classmethod
    def from_diffobj(cls, diffobj: whatthepatch.patch.diffobj):
        return cls(header=diffobj.header, changes=diffobj.changes, text=diffobj.text)

    def to_diffobj(self) -> whatthepatch.patch.diffobj:
        return whatthepatch.patch.diffobj(
            header=self.header, changes=self.changes, text=self.text
        )

    @property
    def old_path(self) -> str:
        old_path = self.header.old_path
        if old_path.startswith("a/"):
            old_path = old_path[2:]
        return old_path

    @property
    def new_path(self) -> str:
        new_path = self.header.new_path
        if new_path.startswith("b/"):
            new_path = new_path[2:]
        return new_path

    def __str__(self) -> str:
        return f"Diff(header={self.header}, changes={self.changes}, text={self.text})"


class PoetryPatcher:
    def __init__(self, poetry: Poetry, io: IO, backup: Backup):
        self.poetry = poetry
        self.io = io
        self.backup = backup
        self.errors = 0

    def debug(self, message: str) -> None:
        self.io.write_line(message, Verbosity.DEBUG)

    def error(self, message: str) -> None:
        self.errors += 1
        self.io.write_error_line(message)

    @property
    def poetry_patches_config(self) -> dict[str, list[str]]:
        tool = self.poetry.pyproject.data["tool"]
        config = tool.get("poetry-patches", {})
        return config

    def apply(self) -> None:
        env = EnvManager(self.poetry, self.io).get()

        for key, value in self.poetry_patches_config.items():
            if dist := env.site_packages.find_distribution(key):
                self.apply_patches(dist._path.parent, value)

    def apply_patches(self, target_dir: Path, patch_uris: list[str]) -> None:
        for patch_uri in patch_uris:
            self.apply_patch(target_dir, patch_uri)

    def apply_patch(self, target_dir: Path, patch_uri: str) -> None:
        self.debug(f"'{patch_uri}' applying...")
        text = self.read(patch_uri)
        diffs = [Diff.from_diffobj(diff) for diff in whatthepatch.parse_patch(text)]

        for diff in diffs:
            self.apply_diff(target_dir, diff)

    def apply_diff(self, target_dir: Path, diff: Diff) -> None:
        old_path, new_path = diff.old_path, diff.new_path
        old_file, new_file = target_dir / old_path, target_dir / new_path

        if self.is_empty(new_path) and old_path != new_path:
            self.delete(old_file)
        elif not self.is_empty(old_path) and old_path != new_path:
            self.rename(old_file, new_file)
            new_path = old_path

        if self.is_empty(old_path) and old_path != new_path:
            self.create(new_file, diff)
        if not self.is_empty(old_path) and old_path == new_path and diff.changes:
            self.update(new_file, diff)

    def delete(self, file: Path) -> None:
        if not file.exists():
            self.error(f"'{file}' can't delete, doesn't exist")
            return

        self.backup.edit_or_delete(file)
        file.unlink()
        self.debug(f"{file} deleted")

    def rename(self, old: Path, new: Path) -> None:
        if not old.exists():
            self.error(f"'{old}' -> '{new}' can't rename, '{old}' doesn't exist")
            return
        if new.exists():
            self.error(f"'{old}' -> '{new}' can't rename, '{new}' already exists")
            return

        self.backup.create_or_rename(new)
        os.rename(old, new)
        self.debug(f"{old} -> {new}")

    def create(self, file: Path, diff: Diff) -> None:
        if file.exists():
            self.error(f"'{file}' can't create, already exists")
            return

        self.backup.create_or_rename(file)
        lines = whatthepatch.apply_diff(diff.to_diffobj(), "")
        file.write_text("\n".join(lines))
        self.debug(f"'{file}' created")

    def update(self, file: Path, diff: Diff) -> None:
        if not file.exists():
            self.error(f"'{file}' can't update, doesn't exist")
            return

        text = file.read_bytes().decode()

        try:
            lines = whatthepatch.apply_diff(diff.to_diffobj(), text)
        except WhatThePatchException as e:
            self.error(f"'{file}' can't update, failed to apply: {e}")
            return

        self.backup.edit_or_delete(file)
        file.write_text("\n".join(lines))
        self.debug(f"'{file}' updated")

    @staticmethod
    def read(uri: str) -> str:
        if uri.startswith("http://") or uri.startswith("https://"):
            return requests.get(uri).content.decode()
        else:
            return Path(uri).read_bytes().decode()

    @staticmethod
    def is_empty(path: str) -> bool:
        return path in (None, "", "/dev/null")
