from typing import TYPE_CHECKING, Any, Dict

import discord

from .custom_button import CustomButton

if TYPE_CHECKING:
    from .core import ModalPaginator, ButtonKeysLiteral
else:
    ModalPaginator = Any
    ButtonKeysLiteral = str


__all__ = (
    "OpenButton",
    "NextButton",
    "PreviousButton",
    "CancelButton",
    "FinishButton",
)


class _OpenButton(CustomButton):
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


OpenButton = _OpenButton(style=discord.ButtonStyle.gray, label="Open", row=0)
"""Represents the default open button for :class:`.ModalPaginator`.

Default implementation is, ``(style=discord.ButtonStyle.gray, label="Open", row=0)``.

This overrides the ``on_optional_modal`` and ``on_required_modal`` methods to change the label and style.
"""
NextButton = CustomButton(label="Next", style=discord.ButtonStyle.green, row=1)
"""Represents the default next button for :class:`.ModalPaginator`.

Default implementation is, ``(label="Next", style=discord.ButtonStyle.green, row=1)``.
"""

PreviousButton = CustomButton(label="Previous", style=discord.ButtonStyle.green, row=1)
"""Represents the default previous button for :class:`.ModalPaginator`.

Default implementation is, ``(label="Previous", style=discord.ButtonStyle.green, row=1)``.
"""

CancelButton = CustomButton(label="Cancel", style=discord.ButtonStyle.red, row=2)
"""Represents the default cancel button for :class:`.ModalPaginator`.

Default implementation is, ``(label="Cancel", style=discord.ButtonStyle.red, row=2)``.
"""

FinishButton = CustomButton(label="Finish", style=discord.ButtonStyle.green, row=2)
"""Represents the default finish button for :class:`.ModalPaginator`.

Default implementation is, ``(label="Finish", style=discord.ButtonStyle.green, row=2)``.
"""

BUTTONS: Dict[ButtonKeysLiteral, CustomButton] = {
    "OPEN": OpenButton,
    "NEXT": NextButton,
    "PREVIOUS": PreviousButton,
    "FINISH": FinishButton,
    "CANCEL": CancelButton,
}
