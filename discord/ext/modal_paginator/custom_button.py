from typing import TYPE_CHECKING, Any, Union

import discord

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
            style=discord.ButtonStyle.secondary if style is discord.utils.MISSING else style,
            label=None if label is discord.utils.MISSING else label,
            emoji=None if emoji is discord.utils.MISSING else emoji,
            row=None if row is discord.utils.MISSING else row,
        )
        self._override_callback: bool = override_callback

    @staticmethod
    def _copy_attrs(original_button: discord.ui.Button[Any], custom_button: discord.ui.Button[Any]) -> None:
        # since we store the original kwargs that were passed to the constructor
        # we know exactly what the user wants to change
        if isinstance(custom_button, CustomButton):
            kwargs = custom_button._original_kwargs
            style = kwargs["style"]
            row = kwargs["row"]
            label = kwargs["label"]
            emoji = kwargs["emoji"]

            if style is not discord.utils.MISSING and style != original_button.style:
                original_button.style = style
            if row is not discord.utils.MISSING and row != original_button.row:
                original_button.row = row
            if label is not discord.utils.MISSING and label != original_button.label:
                original_button.label = label
            if emoji is not discord.utils.MISSING and emoji != original_button.emoji:
                original_button.emoji = emoji
            if custom_button._override_callback:
                original_button.callback = custom_button.callback
        else:
            # we have to rely on the instance because we don't know what kwargs were passed to the constructor
            if custom_button.style != original_button.style:
                original_button.style = custom_button.style
            if custom_button.row and custom_button.row != original_button.row:
                original_button.row = custom_button.row

            if custom_button.label != original_button.label:
                if custom_button.label is None and custom_button.emoji:
                    original_button.label = custom_button.label

            if custom_button.emoji and custom_button.emoji != original_button.emoji:
                original_button.emoji = custom_button.emoji

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

    async def callback(self, interaction: discord.Interaction[Any]) -> Any:
        """The callback for the button.

        This is called if ``override_callback`` is set to ``True``.

        Parameters
        -----------
        interaction: :class:`~discord.Interaction`
            The interaction that triggered the callback.
        """
        pass
