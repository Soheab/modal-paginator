from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union

import discord
from discord.enums import ButtonStyle

if TYPE_CHECKING:
    from .core import ModalPaginator
else:
    ModalPaginator = Any

__all__ = ("CustomButton",)


class CustomButton(discord.ui.Button[Any]):
    """Custom button class to pass to the ``buttons`` kwarg in :class:`.ModalPaginator`.

    This can be used to override things of the default buttons.
    like the label, style, row, etc.

    Parameters docs below is partially copied from :class:`discord.ui.Button`.

    Parameters
    ------------
    style: :class:`discord.ButtonStyle`]
        The new style of the button.
    label: :class:`str`
        The new label of the button.
    emoji: Union[:class:`discord.PartialEmoji`, :class:`discord.Emoji`, :class:`str`]
        The new emoji of the button. (If any)
    row: :class:`int`
        The new row of the button. See :class:`discord.ui.Button` for more info.
    override_callback: Optional[:class:`bool`]
        Whether to override the callback of the button. Defaults to ``False``.
        If ``True``, your callback will be called instead of the one on the paginator.
    """

    def __init__(
        self,
        *,
        style: discord.ButtonStyle = discord.utils.MISSING,
        label: str = discord.utils.MISSING,
        emoji: Union[str, discord.Emoji, discord.PartialEmoji] = discord.utils.MISSING,
        row: int = discord.utils.MISSING,
        override_callback: bool = False,
    ) -> None:
        self._original_kwargs: dict[str, Any] = {
            "style": style,
            "label": label,
            "emoji": emoji,
            "row": row,
        }
        super().__init__(
            style=ButtonStyle.secondary if style is discord.utils.MISSING else style,
            label=None if label is discord.utils.MISSING else label,
            emoji=None if emoji is discord.utils.MISSING else emoji,
            row=None if row is discord.utils.MISSING else row,
        )
        self._override_callback: bool = override_callback
        self._is_default: bool = False

    def on_required_modal(self, button: discord.ui.Button[ModalPaginator]) -> Any:
        """This method is called when
        the :attr:`~.ModalPaginator.current_modal`
        is required but :meth:`discord.ui.Modal.is_finished` is ``False``.

        This can be used to change the button's style, label, etc.
        This should be used in conjunction with :meth:`on_optional_modal`.

        Parameters
        -----------
        button: :class:`~discord.ui.Button`
            The button that was used.
        """
        pass

    def on_optional_modal(self, button: discord.ui.Button[ModalPaginator]) -> Any:
        """This method is called when
        the :attr:`~.ModalPaginator.current_modal`
        is optional.

        This can be used to change the button's style, label, etc.
        Might want to use this to revert the changes made in :meth:`on_required_modal`.

        Parameters
        -----------
        button: :class:`~discord.ui.Button`
            The button that was used.
        """
        pass
