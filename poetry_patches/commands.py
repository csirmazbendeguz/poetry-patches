from poetry.console.commands.group_command import GroupCommand

from poetry_patches.patcher import PoetryPatcher
from poetry_patches.state.backup import Backup


class PatchesApplyCommand(GroupCommand):
    name = "patches apply"
    description = "Apply the patches."

    def handle(self) -> int:
        PoetryPatcher(self.poetry, self.io).apply()
        return 0


class PatchesRevertCommand(GroupCommand):
    name = "patches revert"
    description = "Revert the patches."

    def handle(self) -> int:
        Backup.get().revert()
        return 0
