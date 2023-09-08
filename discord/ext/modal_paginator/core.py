from __future__ import annotations
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Coroutine,
    Optional,
    Sequence,
    TypeVar,
    Union,
)

import discord
from discord.ext import commands as _commands

from .errors import NoModals, NotAModal

if TYPE_CHECKING:
    from typing_extensions import Self
else:
    Self = Any

MessageT = Union[discord.Message, discord.WebhookMessage, discord.InteractionMessage]
TextInpT = TypeVar("TextInpT", bound=discord.ui.TextInput[Any])
ClsT = TypeVar(
    "ClsT",
)
ReturnType = TypeVar("ReturnType")
PaginatorCallable = Callable[[ClsT, discord.Interaction[Any]], Union[Coroutine[Any, Any, ReturnType], ReturnType]]


__all__ = (
    "PaginatorModal",
    "ModalPaginator",
)


class PaginatorModal(discord.ui.Modal):
    """Represents a modal that can be used in a :class:`ModalPaginator`.

    Parameters
    -----------
    *inputs: :class:`discord.ui.TextInput`
        The inputs to add to the modal.
    title: :class:`str`
        The title of the modal.
    custom_id: Optional[:class:`str`]
        The custom ID of the modal. Defaults to ``discord.utils.MISSING``.
    timeout: :class:`float`
        The timeout of the modal. Defaults to ``180.0``.
    callback: Optional[Callable[[:class:`PaginatorModal`, :class:`discord.Interaction[Any]`], Coroutine[Any, Any, Any]]]
        A callback that is run when the modal is interacted with (``on_submit``). Defaults to ``None``.
    required: :class:`bool`
        Whether the modal is required to be filled out before the paginator can be finished / user
        can go to the next/previous page. Defaults to ``False``.

    Attributes
    -----------
    paginator: :class:`ModalPaginator`
        The paginator.
    required: :class:`bool`
        Whether the modal is required to be filled out before the paginator can be finished / user
        can go to the next page.
    """

    paginator: ModalPaginator

    def __init__(
        self,
        *inputs: discord.ui.TextInput[Self],
        title: str,
        custom_id: str = discord.utils.MISSING,
        timeout: float = 180.0,
        callback: Optional[PaginatorCallable[Self, Any]] = None,
        required: bool = False,
    ) -> None:
        super().__init__(title=title, custom_id=custom_id, timeout=timeout)
        self._callback: Optional[PaginatorCallable[Self, Any]] = callback
        self.required: bool = required
        self._inputs: tuple[discord.ui.TextInput[Self], ...] = inputs
        for inp in inputs:
            self.add_item(inp)

    @classmethod
    def _to_self(cls, paginator: ModalPaginator, modal: discord.ui.Modal) -> Self:
        if isinstance(modal, cls):
            modal.paginator = paginator
            return modal

        inst = cls(
            title=modal.title,
            custom_id=modal.custom_id,
            timeout=modal.timeout or 180.0,
            *modal._children,
        )
        inst.paginator = paginator
        return inst

    def add_input(
        self,
        *,
        label: str,
        style: discord.TextStyle = discord.TextStyle.short,
        custom_id: str = discord.utils.MISSING,
        placeholder: Optional[str] = None,
        default: Optional[str] = None,
        required: bool = True,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        row: Optional[int] = None,
    ) -> discord.ui.TextInput[Self]:
        """Adds a text input to the modal. This an easy way to add a text input to the modal.

        The added text input is returned.

        Parameters below are copied from :class:`discord.ui.TextInput`.

        Parameters
        ------------
        label: :class:`str`
            The label to display above the text input.
        custom_id: :class:`str`
            The ID of the text input that gets received during an interaction.
            If not given then one is generated for you.
        style: :class:`discord.TextStyle`
            The style of the text input.
        placeholder: Optional[:class:`str`]
            The placeholder text to display when the text input is empty.
        default: Optional[:class:`str`]
            The default value of the text input.
        required: :class:`bool`
            Whether the text input is required.
        min_length: Optional[:class:`int`]
            The minimum length of the text input.
        max_length: Optional[:class:`int`]
            The maximum length of the text input.
        row: Optional[:class:`int`]
            The relative row this text input belongs to. A Discord component can only have 5
            rows. By default, items are arranged automatically into those 5 rows. If you'd
            like to control the relative positioning of the row then passing an index is advised.
            For example, row=1 will show up before row=2. Defaults to ``None``, which is automatic
            ordering. The row number must be between 0 and 4 (i.e. zero indexed).

        Returns
        --------
        :class:`discord.ui.TextInput`
            The text input that was added.
        """
        text_input: discord.ui.TextInput[Self] = discord.ui.TextInput(
            label=label,
            style=style,
            custom_id=custom_id,
            placeholder=placeholder,
            default=default,
            required=required,
            min_length=min_length,
            max_length=max_length,
            row=row,
        )
        self.add_item(text_input)
        return text_input

    def append_input(self, text_input: TextInpT, /) -> TextInpT:
        """Appends a text input to the modal. Technically an alias for
        :meth:`ModalPaginator.add_item` but this returns the text input
        instead of the modal.

        Parameters
        -----------
        text_input: :class:`discord.ui.TextInput`
            The text input to append.

        Returns
        --------
        :class:`discord.ui.TextInput`
            The text input that was appended.
        """
        self.add_item(text_input)
        return text_input

    async def interaction_check(self, interaction: discord.Interaction[Any]) -> bool:
        """This is called by the library when the modal is interacted with.

        The default implementation calls :class:`ModalPaginator.interaction_check`.

        Parameters
        -----------
        interaction: :class:`discord.Interaction[Any]`
            The interaction to check.

        Returns
        --------
        :class:`bool`
            Whether the interaction should be processed.
        """
        return await self.paginator.interaction_check(interaction)

    async def on_submit(self, interaction: discord.Interaction[Any]) -> None:
        """Called when the modal is submitted.

        The default implementation is the following:
        - Increment the current page of the paginator.
        - Stop the paginator using the ``stop`` method.
        - If a ``callback`` was passed to the modal, run it.
        else
        - Call the default implementation of :meth:`discord.ui.Modal.on_submit`.

        Parameters
        -----------
        interaction: :class:`discord.Interaction[Any]`
            The interaction to use for the paginator.
        """
        self.paginator.current_page += 1
        self.stop()
        await self.paginator.update(interaction)
        if self._callback:
            return await discord.utils.maybe_coroutine(self._callback, self, interaction)

        return await super().on_submit(interaction)


class ModalPaginator(discord.ui.View):
    """A paginator for :class:`~discord.ui.Modal`

    Parameters
    -----------
    modals: Optional[Sequence[:class:`discord.ui.Modal`]]
        The modals to add to the paginator.
        Modals can also be added later using :meth:`ModalPaginator.add_modal`.
    author_id: Optional[:class:`int`]
        ID of the author that can interact with the paginator. Defaults to everyone can interact.
    check: Optional[Callable[[:class:`ModalPaginator`, :class:`discord.Interaction[Any]`], :class:`bool`]]
        A check that is run when the paginator is interacted with (``interaction_check``). Defaults to ``None``.
    finish_callback: Optional[Callable[[:class:`ModalPaginator`, :class:`discord.Interaction[Any]`], Coroutine[Any, Any, Any]]]
        A callback that is run when the paginator is finished (``on_finish``). Defaults to ``None``.
    can_go_back: :class:`bool`
        Whether the user can go back to previous pages using the "Previous" button. Defaults to ``True``.
    disable_after: :class:`bool`
        Whether the paginator should disable all buttons after it's finished or cancelled. Defaults to ``True``.
    timeout: :class:`float`
        The timeout of the paginator. Defaults to ``None``. Timeouts aren't really handled.
    sort_modals: :class:`bool`
        Whether the modals should be sorted by required. Defaults to ``True``.

    Attributes
    -----------
    author_id: Optional[:class:`int`]
        ID of the author that can interact with the paginator. Defaults to everyone can interact.
    """  # noqa: E501

    message: MessageT

    def __init__(
        self,
        modals: Optional[Sequence[discord.ui.Modal]] = None,
        *,
        author_id: Optional[int] = None,
        check: Optional[PaginatorCallable[Self, bool]] = None,
        finish_callback: Optional[PaginatorCallable[Self, Any]] = None,
        timeout: Optional[Union[int, float]] = None,
        can_go_back: bool = True,
        disable_after: bool = True,
        sort_modals: bool = True,
    ) -> None:
        super().__init__(timeout=timeout)
        if modals is None:
            modals = []

        if not can_go_back:
            self.remove_item(self.preview_page)

        self._modals: list[PaginatorModal] = [
            PaginatorModal._to_self(self, modal) for modal in modals  # pyright: ignore [reportPrivateUsage]
        ]
        self._max_pages: int = len(self._modals) - 1
        self._finish_callback: Optional[PaginatorCallable[Self, Any]] = finish_callback
        self._check: Optional[PaginatorCallable[Self, bool]] = check
        self._disable_after: bool = disable_after
        self._can_go_back = can_go_back
        self._sort_modals = sort_modals

        self.author_id: Optional[int] = author_id
        self.current_page: int = 0
        self._current_modal: Optional[PaginatorModal] = None

    @property
    def modals(self) -> list[PaginatorModal]:
        """List[:class:`PaginatorModal`]: The modals in the paginator."""
        return self._modals

    @property
    def current_modal(self) -> Optional[PaginatorModal]:
        """Optional[:class:`PaginatorModal`]: The current modal of the paginator."""
        return self._current_modal

    @property
    def page_string(self) -> str:
        """:class:`str`: String that represents the current page.

        By default, this is ``{current_modal.title}\n\n{current_page + 1}/{len(modals)}``
        if the current modal is not ``None`` else ``{current_page + 1}/{len(modals)}``.
        """
        base = f"{self.current_page + 1}/{len(self.modals)}"
        if self.current_modal:
            return f"{self.current_modal.title}\n\n{base}"
        else:
            return base

    def validate_pages(self) -> None:
        """Validates all modals in the paginator. Basically checks if all modals are
        instances of :class:`discord.ui.Modal` and
        outputs a friendly error message if not.

        This is called in :meth:`ModalPaginator.send`.

        This does the following:
        - Checks if all modals are instances of :class:`discord.ui.Modal`.
        - Sorts the modals by required if ``sort_modals`` is ``True``.
        - Sets the :attr:`ModalPaginator.current_modal` to the first modal in the list.
        - Handles the button states.

        This should be called before sending the paginator if subclassing and overriding ``send``.

        Raises
        -------
        NotAModal
            A modal is not an instance/subclass of :class:`discord.ui.Modal`.
        NoModals
            There are no modals in the paginator.
        """
        modals: list[PaginatorModal] = []
        for idx, modal in enumerate(self._modals.copy()):
            # just in case
            if not isinstance(modal, discord.ui.Modal):  # pyright: ignore [reportUnnecessaryIsInstance]
                raise NotAModal(modal, index=idx, param_name="all modals")  # bit of a hack but it works

            # just in case
            # and maybe faster than doing this always?
            if not isinstance(modal, PaginatorModal):  # pyright: ignore [reportUnnecessaryIsInstance]
                modal = PaginatorModal._to_self(self, modal)  # pyright: ignore [reportPrivateUsage]

            modals.append(modal)

        if not modals:
            raise NoModals()

        self._modals = modals
        self._max_pages = len(self._modals) - 1
        # sort by required if sort_modals is True
        if self._sort_modals:
            self._modals.sort(key=lambda m: m.required, reverse=True)

        self._current_modal = self.get_modal()
        self._handle_button_states()

    def add_modal(self, modal: discord.ui.Modal) -> None:
        """Adds a modal to the paginator.

        Parameters
        -----------
        modal: :class:`discord.ui.Modal`
            The modal to add.

        Raises
        -------
        NotAModal
            The modal is not an instance/subclass of :class:`discord.ui.Modal`.
        """
        if not isinstance(
            modal, discord.ui.Modal
        ):  # pyright: ignore [reportUnnecessaryIsInstance] # no, that's just the type...
            raise NotAModal(modal, param_name="modal")

        self._modals.append(PaginatorModal._to_self(self, modal))  # pyright: ignore [reportPrivateUsage]
        self._max_pages += 1

    def remove_modal(self, modal: PaginatorModal) -> None:
        """Removes a modal from the paginator. Nothing happens if the modal is not in the paginator.

        Parameters
        -----------
        modal: :class:`PaginatorModal`
            The modal to remove.
        """
        try:
            self._modals.remove(modal)
        except ValueError:
            pass
        else:
            self._max_pages -= 1

    async def interaction_check(self, interaction: discord.Interaction[Any]) -> bool:
        """This is called by the library when the paginator is interacted with and
        when the modals are interacted with.

        The default implementation is the following:
        - Check if a check was passed to the paginator. If so, run it.
        else:
        - Check if the author ID is set. If so, check if the interaction's user ID is the same as the author ID.
        else:
        - Call the default implementation of :meth:`discord.ui.View.interaction_check`.

        Parameters
        -----------
        interaction: :class:`discord.Interaction[Any]`
            The interaction to check.

        Returns
        --------
        :class:`bool`
            Whether the interaction should be processed.
        """
        if self._check:
            return await discord.utils.maybe_coroutine(self._check, self, interaction)
        elif self.author_id:
            return interaction.user.id == self.author_id
        else:
            return await super().interaction_check(interaction)

    async def on_cancel(self, interaction: discord.Interaction[Any]) -> None:
        """A callback that is called when the paginator is cancelled. This is called when the
        "Cancel" button is pressed.

        The default implementation is the following:
        - If ``disable_after`` is ``True``, disable all buttons using :meth:`ModalPaginator.disable_all_buttons`.

        Parameters
        -----------
        interaction: :class:`discord.Interaction[Any]`
            The last interaction that was used for the paginator.
        """
        if self._disable_after:
            await self.disable_all_buttons(interaction)

    async def on_finish(self, interaction: discord.Interaction[Any]) -> None:
        """A callback that is called when the paginator is finished. This is called when the "Finish" button is pressed.

        The default implementation is the following:
        - If a finish callback was passed to the paginator, run it.
        - If ``disable_after`` is ``True``, disable all buttons using :meth:`ModalPaginator.disable_all_buttons`.

        Parameters
        -----------
        interaction: :class:`discord.Interaction[Any]`
            The last interaction that was used for the paginator.
        """
        if self._finish_callback:
            await discord.utils.maybe_coroutine(self._finish_callback, self, interaction)
        if self._disable_after:
            await self.disable_all_buttons(interaction)

    def get_modal(self) -> PaginatorModal:
        """Returns the current modal according to the current page.

        This is called in :meth:`ModalPaginator.update` and :meth:`ModalPaginator.send

        Returns
        --------
        :class:`PaginatorModal`
            The modal.
        """
        if self.current_page >= self._max_pages:
            self.current_page = self._max_pages
        elif self.current_page < 0:
            self.current_page = 0

        return self._modals[self.current_page]

    def _handle_button_states(self) -> None:
        """Handles the button states.

        This is called in :meth:`ModalPaginator.update` and :meth:`ModalPaginator.send`.
        """
        modal: Optional[PaginatorModal] = self.current_modal

        self.open_button.disabled = not modal or modal.is_finished()
        if modal and modal.required and not modal.is_finished():
            self.open_button.label = "*Open"
            self.open_button.style = discord.ButtonStyle.red
        else:
            self.open_button.label = "Open"
            self.open_button.style = discord.ButtonStyle.blurple

        self.next_page.disabled = self.current_page >= self._max_pages or self._is_locked()
        self.preview_page.disabled = not self._can_go_back or self.current_page <= 0
        self.finish_button.disabled = not all(m.is_finished() for m in self._modals if m.required)

    def _is_locked(self) -> bool:
        """:class:`bool`: Whether the current modal is required but not filled in by the user.

        This is called in the "Next" and "Previous" buttons.
        """
        if not self.current_modal:
            return False

        return self.current_modal.required and not self.current_modal.is_finished()

    async def update(self, interaction: discord.Interaction[Any]) -> None:
        """Updates the paginator's message.

        Parameters
        -----------
        interaction: :class:`discord.Interaction[Any]`
            The interaction to use for the paginator.
        """
        self._current_modal = self.get_modal()
        self._handle_button_states()
        await interaction.response.edit_message(view=self, content=self.page_string)

    async def disable_all_buttons(self, interaction: discord.Interaction[Any]) -> None:
        """Disables all buttons.

        Uses the interaction if not responded else calls ``edit`` on the :attr:`ModalPaginator.message`.

        Parameters
        -----------
        interaction: :class:`discord.Interaction[Any]`
            The interaction to edit.
        """
        self.next_page.disabled = True
        self.preview_page.disabled = True
        self.open_button.disabled = True
        self.finish_button.disabled = True
        self.cancel_button.disabled = True
        if not interaction.response.is_done():
            await interaction.response.edit_message(view=self)
        else:
            await self.message.edit(view=self)

    async def send(
        self,
        obj: Union[discord.abc.Messageable, discord.Interaction[Any], _commands.Context[Any]],
        **kwargs: Any,
    ) -> MessageT:
        """Sends the paginator.

        This calls :meth:`ModalPaginator.validate_pages` before sending the paginator.
        Make sure to call said method if subclassing and overriding this method.

        Parameters
        -----------
        obj: Union[:class:`~discord.abc.Messageable`, :class:`~discord.Interaction[Any]`, :class:`~discord.ext.commands.Context`]
            The desination to send the paginator to. if :class:`~discord.Interaction` is passed, the paginator will be sent
            as a response to the interaction or as a followup if the interaction is already responded to.
        ephemeral: :class:`bool`
            Whether the paginator should be ephemeral. Defaults to ``False``. This is only used if ``obj`` is an interaction.
        **kwargs: Any
            Additional keyword arguments to the destination's ``send`` method.

        Returns
        --------
        Union[:class:`~discord.Message`, :class:`~discord.WebhookMessage`, :class:`~discord.InteractionMessage`]
            The message that was sent.

            :meth:`discord.Interaction.original_response` is used if ``obj`` is an interaction and the
            interaction was not responded to. Subclass to change this behaviour.

        """  # noqa: E501
        self.validate_pages()

        if isinstance(obj, discord.Interaction):
            self.interaction = obj
            if not obj.response.is_done():
                await obj.response.send_message(self.page_string, view=self)
                self.message = await obj.original_response()
            else:
                self.message = await obj.followup.send(self.page_string, view=self, wait=True)
        else:
            self.message = await obj.send(self.page_string, view=self)

        return self.message

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.blurple, row=1)
    async def preview_page(self, interaction: discord.Interaction[Any], _: discord.ui.Button[Self]) -> None:
        if self._is_locked():
            await interaction.response.send_message(
                "Please complete the current modal before going back.", ephemeral=True, delete_after=5
            )
            return

        self.current_page -= 1
        await self.update(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple, row=1)
    async def next_page(self, interaction: discord.Interaction, _: discord.ui.Button[Self]) -> None:
        if self._is_locked():
            await interaction.response.send_message(
                "Please complete the current modal before going to the next one.", ephemeral=True, delete_after=5
            )
            return

        self.current_page += 1
        await self.update(interaction)

    @discord.ui.button(label="Open", row=0)
    async def open_button(self, interaction: discord.Interaction[Any], _: discord.ui.Button[Self]) -> None:
        self._current_modal = self.get_modal()
        # for typing purposes, it shouldn't be None
        if not self.current_modal:
            await interaction.response.send_message(
                "Something went wrong... there is no current modal. Please report this to the developer.",
                ephemeral=True,
                delete_after=5,
            )
            return

        await interaction.response.send_modal(self.current_modal)

    @discord.ui.button(label="Finish", style=discord.ButtonStyle.green, row=2)
    async def finish_button(self, interaction: discord.Interaction[Any], _: discord.ui.Button[Self]) -> None:
        if not all(m.is_finished() for m in self._modals if m.required):
            await interaction.response.send_message(
                "You shouldn't be able to press this button... please finish all required modals.",
                ephemeral=True,
                delete_after=5,
            )
            return

        self.stop()
        await self.on_finish(interaction)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, row=2)
    async def cancel_button(self, interaction: discord.Interaction[Any], _: discord.ui.Button[Self]) -> None:
        self.stop()
        await self.on_cancel(interaction)
