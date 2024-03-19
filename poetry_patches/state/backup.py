import os
import shutil
import uuid
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

    @staticmethod
    def init_dir() -> None:
        if not BACKUPS.exists():
            BACKUPS.mkdir(parents=True, exist_ok=True)

    def edit_or_delete(self, file: Path) -> None:
        """
        Create a backup for an edited or deleted file.
        """
        src = str(file.resolve())
        self.meta.load()
        if self.meta.has_backup(src):
            return

        backup = self.backups / self.get_backup_name(file)
        if backup.exists():
            # If the file got edited multiple times,
            # a backup file may already exist.
            return

        # Copy the file to './poetry-patches/backups/'.
        dst = str(backup.resolve())
        shutil.copy(src, dst)

        # Store the backup entry in './poetry-patches/meta.json'.
        self.meta.set_backup(src, dst)
        self.meta.dump()

    @staticmethod
    def get_backup_name(file: Path) -> str:
        root, ext = os.path.splitext(file.name)
        suffix = str(uuid.uuid4())[:8]
        return f"{root}_{suffix}{ext}"

    def create_or_rename(self, file: Path) -> None:
        """
        Create a backup for a created or renamed file.
        """
        path = str(file.resolve())
        self.meta.load()
        if not self.meta.has_backup(path):
            self.meta.set_backup(path, None)
            self.meta.dump()

    def revert(self) -> None:
        """
        Revert the patches.
        """
        self.meta.load()

        for key, value in self.meta.get_backups().items():
            file = Path(key)

            if value is None:
                file.unlink(missing_ok=True)
            else:
                backup = Path(value).read_bytes()
                file.write_bytes(backup)

        self.meta.clear()
