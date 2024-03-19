from poetry.console.commands.command import Command
from poetry.plugins import ApplicationPlugin

from poetry_patches.commands import PatchesApplyCommand


class PoetryPatchesPlugin(ApplicationPlugin):
    @property
    def commands(self) -> list[type[Command]]:
        return [PatchesApplyCommand]
