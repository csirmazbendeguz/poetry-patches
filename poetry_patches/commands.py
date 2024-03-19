from poetry.console.commands.group_command import GroupCommand

from poetry_patches.patcher import PoetryPatcher


class PatchesApplyCommand(GroupCommand):
    name = "patches apply"
    description = "Apply the patches."

    def handle(self) -> int:
        PoetryPatcher(self.poetry, self.io).apply()
        return 0
