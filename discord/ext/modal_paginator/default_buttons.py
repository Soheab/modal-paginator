from __future__ import annotations
from typing import TYPE_CHECKING, Any

import discord

from .custom_button import CustomButton

if TYPE_CHECKING:
    from .core import ModalPaginator, CustomButtons
else:
    ModalPaginator = Any


__all__ = (
    "OpenButton",
    "NextButton",
    "PreviousButton",
    "CancelButton",
    "FinishButton",
)


class _OpenButton(CustomButton):
    def __init__(self) -> None:
        super().__init__(style=discord.ButtonStyle.gray, label="Open", row=0)
        self._is_default: bool = True

    def on_optional_modal(self, button: discord.ui.Button[ModalPaginator]) -> None:
        """Called when the modal is optional.

        This changes the label to ``"Open"`` and the style to ``discord.ButtonStyle.gray``.
        """
        button.label = "Open"
        button.style = discord.ButtonStyle.gray

    def on_required_modal(self, button: discord.ui.Button[ModalPaginator]) -> None:
        """Called when the modal is required.

        This changes the label to ``"*Open"`` and the style to ``discord.ButtonStyle.blurple``.
        """
        button.label = "*Open"
        button.style = discord.ButtonStyle.blurple


OpenButton = _OpenButton()
"""Represents the default open button for :class:`.ModalPaginator`.

Default implementation is, ``(style=discord.ButtonStyle.gray, label="Open", row=0)``.

This overrides the ``on_optional_modal`` and ``on_required_modal`` methods to change the label and style.
"""
NextButton = CustomButton(label="Next", style=discord.ButtonStyle.green, row=1)
"""Represents the default next button for :class:`.ModalPaginator`.

Default implementation is, ``(label="Next", style=discord.ButtonStyle.green, row=1)``.
"""
NextButton._is_default = True  # pyright: ignore [reportPrivateUsage]

PreviousButton = CustomButton(label="Previous", style=discord.ButtonStyle.green, row=1)
"""Represents the default previous button for :class:`.ModalPaginator`.

Default implementation is, ``(label="Previous", style=discord.ButtonStyle.green, row=1)``.
"""
PreviousButton._is_default = True  # pyright: ignore [reportPrivateUsage]

CancelButton = CustomButton(label="Cancel", style=discord.ButtonStyle.red, row=2)
"""Represents the default cancel button for :class:`.ModalPaginator`.

Default implementation is, ``(label="Cancel", style=discord.ButtonStyle.red, row=2)``.
"""
CancelButton._is_default = True  # pyright: ignore [reportPrivateUsage]

FinishButton = CustomButton(label="Finish", style=discord.ButtonStyle.green, row=2)
"""Represents the default finish button for :class:`.ModalPaginator`.

Default implementation is, ``(label="Finish", style=discord.ButtonStyle.green, row=2)``.
"""
FinishButton._is_default = True  # pyright: ignore [reportPrivateUsage]

BUTTONS: CustomButtons = {
    "OPEN": OpenButton,
    "NEXT": NextButton,
    "PREVIOUS": PreviousButton,
    "CANCEL": CancelButton,
    "FINISH": FinishButton,
}
