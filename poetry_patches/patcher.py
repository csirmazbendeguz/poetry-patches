import os
from pathlib import Path

import requests
import whatthepatch
from cleo.io.io import IO
from cleo.io.outputs.output import Verbosity
from poetry.exceptions import PoetryException
from poetry.poetry import Poetry
from poetry.utils.env import EnvManager
from whatthepatch.exceptions import HunkApplyException

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

    def debug(self, message: str) -> None:
        self.io.write_line(message, Verbosity.DEBUG)

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
            old_path, new_path = diff.old_path, diff.new_path
            old_file, new_file = target_dir / old_path, target_dir / new_path

            # delete
            if self.is_empty(new_path) and old_path != new_path:
                if not old_file.exists():
                    raise PoetryException(
                        f"{patch_uri} deletes '{old_path}', "
                        f"but '{old_path}' doesn't exist in {target_dir}."
                    )

                self.backup.edit_or_delete(old_file)
                old_file.unlink()
                self.debug(f"{old_path} deleted")
                continue

            # rename
            if not self.is_empty(old_path) and old_path != new_path:
                if not old_file.exists():
                    raise PoetryException(
                        f"'{patch_uri}' renames '{old_path}' -> '{new_path}', "
                        f"but '{old_path}' doesn't exist in '{target_dir}'."
                    )
                if new_file.exists():
                    raise PoetryException(
                        f"'{patch_uri}' renames '{old_path}' -> '{new_path}', "
                        f"but '{new_path}' already exists in '{target_dir}'."
                    )

                self.backup.create_or_rename(new_file)
                os.rename(old_file, new_file)
                self.debug(f"{old_path} -> {new_path}")
                new_path = old_path

            # create
            if self.is_empty(old_path) and old_path != new_path:
                if new_file.exists():
                    raise PoetryException(
                        f"'{patch_uri}' creates '{new_path}', "
                        f"but '{new_path}' already exists in '{target_dir}'."
                    )

                self.backup.create_or_rename(new_file)
                data = "\n".join(whatthepatch.apply_diff(diff, ""))
                new_file.write_text(data)
                self.debug(f"'{new_path}' created")

            # update
            if not self.is_empty(old_path) and old_path == new_path and diff.changes:
                if not old_file.exists():
                    raise PoetryException(
                        f"'{patch_uri}' updates '{old_path}', "
                        f"but '{old_path}' doesn't exist in '{target_dir}'."
                    )

                text = old_file.read_bytes().decode()
                try:
                    data = "\n".join(whatthepatch.apply_diff(diff, text))
                except HunkApplyException as e:
                    raise PoetryException(
                        f"'{patch_uri}' failed to apply to '{old_path}' "
                        f"in '{target_dir}': {e}."
                    )
                self.backup.edit_or_delete(new_file)
                new_file.write_text(data)
                self.debug(f"'{new_path}' updated")

    @staticmethod
    def read(uri: str) -> str:
        if uri.startswith("http://") or uri.startswith("https://"):
            return requests.get(uri).content.decode()
        else:
            return Path(uri).read_bytes().decode()

    @staticmethod
    def is_empty(path: str) -> bool:
        return path in (None, "", "/dev/null")
