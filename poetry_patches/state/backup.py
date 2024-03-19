import shutil
from pathlib import Path

from poetry_patches import BACKUPS
from poetry_patches.state.meta import Meta


class Backup:
    def __init__(self, meta: Meta, backups: Path):
        self.meta = meta
        self.backups = backups

    @classmethod
    def get(cls):
        return cls(Meta.get(), BACKUPS)

    def edit_or_delete(self, file: Path) -> None:
        """
        Create a backup for an edited or deleted file.
        """
        backup = self.backups / file.name
        if backup.exists():
            # If the file got edited multiple times,
            # a backup file may already exist.
            return

        # Copy the file to './poetry-patches/backups/'.
        src, dst = str(file.resolve()), str(backup.resolve())
        shutil.copy(src, dst)

        # Store the backup entry in './poetry-patches/meta.json'.
        self.meta.load()
        self.meta.set_backup(src, dst)
        self.meta.dump()

    def create_or_rename(self, file: Path) -> None:
        """
        Create a backup for a created or renamed file.
        """
        path = str(file.resolve())
        self.meta.load()
        if not self.meta.has_backup(path):
            self.meta.set_backup(path, None)
            self.meta.dump()
