"""Icon-specific instruction variants for Eve."""

from __future__ import annotations

from scaling_evolve.algorithms.eve.instructions import default


class Phase2EntrypointInstruction(default.Phase2EntrypointInstruction):
    def __init__(self, *, file_list: list[str]) -> None:
        super().__init__(file_list=file_list)


class Phase2ReadmeInstruction(default.Phase2ReadmeInstruction):
    def __init__(self, *, file_list: list[str]) -> None:
        super().__init__(file_list=file_list)
