from poetry.console.application import Application
from poetry.console.commands.command import Command
from poetry.plugins import ApplicationPlugin

from poetry_patches.commands import PatchesApplyCommand, PatchesRevertCommand
from poetry_patches.state.backup import Backup


class PoetryPatchesPlugin(ApplicationPlugin):
    @property
    def commands(self) -> list[type[Command]]:
        return [PatchesApplyCommand, PatchesRevertCommand]

    def activate(self, application: Application) -> None:
        Backup.init_dir()
        super().activate(application)
