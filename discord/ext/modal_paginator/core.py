from __future__ import annotations
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Coroutine,
    Dict,
    List,
    Optional,
    Sequence,
    Literal,
    TypeVar,
    Union,
)

import discord
from discord.ext import commands as _commands
from .default_buttons import BUTTONS as DEFAULT_BUTTONS


from .errors import InvalidButtonKey, NoModals, NotAModal
from .custom_button import CustomButton

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
ButtonKeysLiteral = Literal["NEXT", "PREVIOUS", "OPEN", "FINISH", "CANCEL"]
CustomButtons = Dict[ButtonKeysLiteral, Optional[discord.ui.Button[Any]]]


__all__ = (
    "PaginatorModal",
    "ModalPaginator",
)


class PaginatorModal(discord.ui.Modal):
    """Represents a modal that can be used in a :class:`.ModalPaginator`.

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
    callback: Optional[Callable[[:class:`PaginatorModal`, :class:`discord.Interaction`], Coroutine[Any, Any, Any]]]
        A callback that is run when the modal is interacted with (``on_submit``). Defaults to ``None``.
    required: :class:`bool`
        Whether the modal is required to be filled out before the paginator can be finished / user
        can go to the next/previous page. Defaults to ``False``.
    """

    _paginator: ModalPaginator

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

    @property
    def paginator(self) -> ModalPaginator:
        """:class:`ModalPaginator`: The paginator of the modal."""
        return self._paginator

    @classmethod
    def _to_self(cls, paginator: ModalPaginator, modal: discord.ui.Modal) -> Self:
        if isinstance(modal, cls):
            modal._paginator = paginator
            return modal

        inst = cls(
            title=modal.title,
            custom_id=modal.custom_id,
            timeout=modal.timeout or 180.0,
            *modal._children,  # pyright: ignore [reportGeneralTypeIssues]
        )
        inst._paginator = paginator
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
        :meth:`discord.ui.Modal.add_item` but this returns the text input
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
        interaction: :class:`discord.Interaction`
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

        #. Increment the current page of the paginator.
        #. Stop the paginator using the ``stop`` method.

        * If a ``callback`` was passed to the modal, run it.

        else:

        * Call the default implementation of :meth:`discord.ui.Modal.on_submit`.

        Parameters
        -----------
        interaction: :class:`discord.Interaction`
            The interaction to use for the paginator.
        """
        self.paginator.current_page += 1
        self.stop()
        await self.paginator.update(interaction)
        if self._callback:
            return await discord.utils.maybe_coroutine(self._callback, self, interaction)

        return await super().on_submit(interaction)


class ModalPaginator(discord.ui.View):
    """A paginator for :class:`discord.ui.Modal`

    Parameters
    -----------
    modals: Optional[Sequence[:class:`discord.ui.Modal`]]
        The modals to add to the paginator.
        Modals can be added later using :meth:`ModalPaginator.add_modal`.
    author_id: Optional[:class:`int`]
        ID of the author that can interact with the paginator. Defaults to everyone can interact.
    auto_finish: :class:`bool`
        Whether the paginator should automatically finish when all required modals are filled in. Defaults to ``False``.
        All modals must be required if this is ``True``.

        This changes the following:

        #. Remove the "Finish" button.
        #. Call :meth:`ModalPaginator.on_finish` when all required modals are filled in.

        .. versionadded:: 1.1
    check: Optional[Callable[[:class:`ModalPaginator`, :class:`discord.Interaction`], :class:`bool`]]
        A check that is run when the paginator is interacted with (``interaction_check``). Defaults to ``None``.
    finish_callback: Optional[Callable[[:class:`ModalPaginator`, :class:`discord.Interaction`], Coroutine[Any, Any, Any]]]
        A callback that is run when the paginator is finished (``on_finish``). Defaults to ``None``.
    can_go_back: :class:`bool`
        Whether the user can go back to previous pages using the "Previous" button. Defaults to ``True``.
    disable_after: :class:`bool`
        Whether the paginator should disable all buttons after it's finished or cancelled. Defaults to ``True``.
    timeout: :class:`float`
        The timeout of the paginator. Defaults to ``None``. Timeouts aren't really handled.
    sort_modals: :class:`bool`
        Whether the modals should be sorted by required. Defaults to ``True``.
    buttons: Optional[Dict[:class:`str`, Optional[:class:`discord.ui.Button`]]]
        A dictionary of buttons to customize the default buttons of the paginator with.

        Valid keys are: ``"OPEN"``, ``"NEXT"``, ``"PREVIOUS"``, ``"CANCEL"`` and ``"FINISH"``.
        It's recommended to use :class:`.CustomButton` instead of :class:`discord.ui.Button` to customize the buttons.

        Example:

        .. code-block:: python
            :linenos:

            buttons = {
                # change the previous button's style to red
                "PREVIOUS": CustomButton(style=discord.ButtonStyle.red),
                # change the finish button's label to "Done"
                "FINISH": CustomButton(label="Done"),
                # remove the cancel button
                "CANCEL": None,
            }

        See :class:`.CustomButton` for more info.


    Attributes
    -----------
    author_id: Optional[:class:`int`]
        ID of the author that can interact with the paginator. Defaults to everyone can interact.
    auto_finish: :class:`bool`
        Whether the paginator should automatically finish when all required modals are filled in. Defaults to ``False``.

        .. versionadded:: 1.1

    Example
    --------
    .. code-block:: python
        :linenos:

        paginator = ModalPaginator(
            modals=[
                discord.ui.Modal(title="Modal 1", custom_id="modal1"),
                discord.ui.Modal(title="Modal 2", custom_id="modal2"),
                ...
            ],
            author_id=000000000000000000,
        )
        await paginator.send(<messageable or Interaction>)
        # don't want to use the send method? and want to send it yourself?
        # call paginator.validate_pages() before sending the view (paginator):
        # paginator.validate_pages()
        # await messageable.send("...", view=paginator)

    """  # noqa: E501

    _message: Optional[MessageT] = None

    def __init__(
        self,
        modals: Optional[Sequence[discord.ui.Modal]] = None,
        *,
        author_id: Optional[int] = None,
        auto_finish: bool = False,
        check: Optional[PaginatorCallable[Self, bool]] = None,
        finish_callback: Optional[PaginatorCallable[Self, Any]] = None,
        timeout: Optional[Union[int, float]] = None,
        can_go_back: bool = True,
        disable_after: bool = True,
        sort_modals: bool = True,
        buttons: Optional[CustomButtons] = None,
    ) -> None:
        super().__init__(timeout=timeout)
        if modals is None:
            modals = []

        self._modals: list[PaginatorModal] = [
            PaginatorModal._to_self(self, modal) for modal in modals  # pyright: ignore [reportPrivateUsage]
        ]
        self._max_pages: int = len(self._modals) - 1
        self._finish_callback: Optional[PaginatorCallable[Self, Any]] = finish_callback
        self._check: Optional[PaginatorCallable[Self, bool]] = check
        self._disable_after: bool = disable_after
        self._can_go_back = can_go_back
        self._sort_modals = sort_modals
        self.auto_finish = auto_finish

        self.author_id: Optional[int] = author_id
        self.current_page: int = 0
        self._current_modal: Optional[PaginatorModal] = None

        self.__methods_map: Dict[str, discord.ui.Button[Self]] = {
            "OPEN": self.open_button,
            "NEXT": self.next_page,
            "PREVIOUS": self.previous_page,
            "FINISH": self.finish_button,
            "CANCEL": self.cancel_button,
        }

        if buttons is not None:
            for name in buttons:
                if name not in DEFAULT_BUTTONS:
                    raise InvalidButtonKey(name, tuple(DEFAULT_BUTTONS.keys()))
        else:
            buttons = {}

        self._buttons: Dict[ButtonKeysLiteral, Optional[CustomButton]] = self._set_buttons(buttons)

    @classmethod
    def from_text_inputs(
        cls,
        *inputs: discord.ui.TextInput[Any],
        author_id: Optional[int] = None,
        auto_finish: bool = False,
        check: Optional[PaginatorCallable[Self, bool]] = None,
        finish_callback: Optional[PaginatorCallable[Self, Any]] = None,
        timeout: Optional[Union[int, float]] = None,
        can_go_back: bool = True,
        disable_after: bool = True,
        sort_modals: bool = True,
        buttons: Optional[CustomButtons] = None,
        titles: Union[str, Sequence[str]] = discord.utils.MISSING,
        default_title: str = "Enter your input",
    ) -> ModalPaginator:
        """A shortcut method to create a :class:`ModalPaginator` with a list of text inputs.

        Parameters
        -----------
        *inputs: :class:`discord.ui.TextInput`
            The text inputs to add to the modals.
        default_title: :class:`str`
            The default title of the modals.
            This is used as the title of the modals if ``modal_titles`` is
            not given or is less than the amount of modals required.

            Defaults to "Enter your input".
        titles: Union[:class:`str`, Sequence[:class:`str`]]
            The title(s) of the modals.
            This can be a single string which will be used for all modals or
            a tuple of strings in the same order as the text inputs per 5.

            Defaults to ``default_title`` for all modals if not given.

            Example:

            .. code-block:: python
                :linenos:

                # All modals with the ``default_title`` title
                paginator = ModalPaginator.from_text_inputs(
                    ..., # text inputs
                    # other parameters
                )
                # All modals with the same title "Waiting for input"
                paginator = ModalPaginator.from_text_inputs(
                    ..., # text inputs
                    modal_titles="Waiting for input",
                    # other parameters
                )
                # First modal with title "Personal questions" and second modal with title "Hobbies questions"
                # and the others modals with the ``default_title`` title
                paginator = ModalPaginator.from_text_inputs(
                    *[
                        # text inputs for first modal
                        text_input1, text_input2, text_input3, text_input4, text_input5,
                        # text inputs for second modal
                        text_input6, text_input7, text_input8, text_input9, text_input10,
                    ],
                    modal_titles=("Personal questions", "Hobbies questions"),
                    # other parameters
                )
                # Changing the default title
                paginator = ModalPaginator.from_text_inputs(
                    ..., # text inputs
                    default_title="Please answer the following questions",
                    # other parameters
                )


        Other parameters are the same as :class:`ModalPaginator`.

        .. versionadded:: 1.1

        Returns
        --------
        :class:`ModalPaginator`
            The constructed paginator with the modals.
        """

        def get_title(idx: int) -> str:
            if titles is discord.utils.MISSING:
                return default_title

            if isinstance(titles, str):
                return titles

            try:
                return titles[idx]
            except IndexError:
                return default_title

        modals: List[PaginatorModal] = []
        for idx, text_inputs in enumerate(discord.utils.as_chunks(inputs, 5)):
            modal = PaginatorModal(*text_inputs, title=get_title(idx), required=True)
            modals.append(modal)

        return cls(
            modals=modals,
            author_id=author_id,
            auto_finish=auto_finish,
            check=check,
            finish_callback=finish_callback,
            timeout=timeout,
            can_go_back=can_go_back,
            disable_after=disable_after,
            sort_modals=sort_modals,
            buttons=buttons,
        )

    @property
    def modals(self) -> list[PaginatorModal]:
        """List[:class:`PaginatorModal`]: The modals in the paginator."""
        return self._modals

    @property
    def text_inputs(self) -> list[discord.ui.TextInput[PaginatorModal]]:
        """List[:class:`discord.ui.TextInput`]: The text inputs in the paginator.

        This basically gets all TextInput's from the modal's :attr:`~discord.ui.Modal.children`.

        .. versionadded:: 1.1
        """
        return [inp for modal in self.modals for inp in modal.children if isinstance(inp, discord.ui.TextInput)]

    @property
    def current_modal(self) -> Optional[PaginatorModal]:
        """Optional[:class:`PaginatorModal`]: The current modal of the paginator."""
        return self._current_modal

    @property
    def page_string(self) -> str:
        r""":class:`str`: String that represents the current page.

        By default, this is ``{current_modal.title}\n\n{current_page + 1}/{len(modals)}``
        if the current modal is not ``None`` else ``{current_page + 1}/{len(modals)}``.
        """
        base = f"{self.current_page + 1}/{len(self.modals)}"
        if self.current_modal:
            return f"{self.current_modal.title}\n\n{base}"
        else:
            return base

    @property
    def message(self) -> Optional[MessageT]:
        """Optional[Union[:class:`~discord.Message`, :class:`~discord.WebhookMessage`, :class:`~discord.InteractionMessage`]]:
        The message that the paginator is attached to. This is set in :meth:`ModalPaginator.send`.

        This is ``None`` if the paginator is not sent using :meth:`ModalPaginator.send`.
        """
        return self._message

    def _handle_button_states(self) -> None:
        """Handles the button states. E.g, change the Open button's name to *Open
        if the current modal is required and not finished.

        This is called in :meth:`ModalPaginator.update` and :meth:`ModalPaginator.validate_pages`.
        """
        modal: Optional[PaginatorModal] = self.current_modal

        self.open_button.disabled = not modal or modal.is_finished()
        self.next_page.disabled = self.current_page >= self._max_pages or self._is_locked()
        self.previous_page.disabled = not self._can_go_back or self.current_page <= 0
        self.finish_button.disabled = not all(m.is_finished() for m in self._modals if m.required)
        if modal:
            for button in self._buttons.values():
                if not button:
                    continue

                if modal.required and not modal.is_finished():
                    button.on_required_modal(button)
                else:
                    button.on_optional_modal(button)

    def _is_locked(self) -> bool:
        """:class:`bool`: Whether the current modal is required but not filled in by the user.

        This is called in the "Next" and "Previous" buttons.
        """
        if not self.current_modal:
            return False

        return self.current_modal.required and not self.current_modal.is_finished()

    def _set_buttons(self, custom_buttons: CustomButtons) -> Dict[ButtonKeysLiteral, Optional[CustomButton]]:
        res: Dict[ButtonKeysLiteral, Optional[CustomButton]] = {}

        for name, default_button_data in DEFAULT_BUTTONS.items():
            default_button = self.__methods_map[name]
            custom_button = custom_buttons.get(name, discord.utils.MISSING)

            if custom_button is None:
                res[name] = None
                self.remove_item(default_button)
                continue

            # fmt: off
            res[name] = CustomButton._copy_attrs(  # pyright: ignore [reportPrivateUsage]
                default_button,
                custom_button if custom_button is not discord.utils.MISSING else default_button_data
            )
            # fmt: on

        if self.auto_finish:
            self.remove_item(self.__methods_map["FINISH"])
            res["FINISH"] = None
        if not self._can_go_back:
            self.remove_item(self.__methods_map["PREVIOUS"])
            res["PREVIOUS"] = None

        return res

    def validate_pages(self) -> None:
        """Validates all modals in the paginator. Basically checks if all modals are
        instances of :class:`discord.ui.Modal` and
        outputs a friendly error message if not.

        This is called in :meth:`ModalPaginator.send`.

        This does the following:

        #. Checks if all modals are instances of :class:`discord.ui.Modal`.
        #. Checks whether ``auto_finish`` is ``True`` and if so, checks if each modal is required.
        #. Sorts the modals by required if ``sort_modals`` is ``True``.
        #. Sets the :attr:`ModalPaginator.current_modal` to the first modal in the list.
        #. Handles the button states.

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

            if self.auto_finish and not modal.required:
                raise ValueError(
                    f"Modal at index {idx} is not required but auto_finish is True. "
                    "All modals must be required if auto_finish is True."
                )

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

        * Check if a check was passed to the paginator. If so, run it.

        else:

        * Check if the author ID is set. If so, check if the interaction's user ID is the same as the author ID.

        else:

        * Call the default implementation of :meth:`discord.ui.View.interaction_check`.

        Parameters
        -----------
        interaction: :class:`discord.Interaction`
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

    async def __cancel_impl(self, interaction: discord.Interaction[Any]) -> None:
        self.stop()
        await self.on_cancel(interaction)
        if self._disable_after:
            await self.disable_all_buttons(interaction)

        return

    async def on_cancel(self, interaction: discord.Interaction[Any]) -> None:
        """A callback that is called when the paginator is cancelled. This is called when the
        "Cancel" button is pressed.

        The default implementation does nothing.

        Parameters
        -----------
        interaction: :class:`discord.Interaction`
            The last interaction that was used for the paginator.
        """
        pass

    async def __finish_impl(self, interaction: discord.Interaction[Any]) -> None:
        self.stop()
        await self.on_finish(interaction)
        if self._finish_callback:
            await discord.utils.maybe_coroutine(self._finish_callback, self, interaction)
        if self._disable_after:
            await self.disable_all_buttons(interaction)

        return

    async def on_finish(self, interaction: discord.Interaction[Any]) -> None:
        """A callback that is called when the paginator is finished. This is called when the "Finish" button is pressed.

        The default implementation does nothing.

        Parameters
        -----------
        interaction: :class:`discord.Interaction`
            The last interaction that was used for the paginator.
        """
        pass

    def get_modal(self) -> PaginatorModal:
        """Returns the current modal according to the current page.

        This is called in :meth:`ModalPaginator.update`,
        :meth:`ModalPaginator.validate_pages` and the "Open" button.

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

    async def update(self, interaction: discord.Interaction[Any]) -> None:
        """Updates the paginator's message.

        Parameters
        -----------
        interaction: :class:`discord.Interaction`
            The interaction to use for the paginator.
        """
        self._current_modal = self.get_modal()
        self._handle_button_states()
        await interaction.response.edit_message(view=self, content=self.page_string)

        if self.auto_finish and all(m.is_finished() for m in self._modals if m.required):
            self.stop()
            await self.on_finish(interaction)
            return

    async def disable_all_buttons(self, interaction: discord.Interaction[Any]) -> None:
        """Disables all buttons.

        Uses the interaction if not responded else calls ``.edit`` on the :attr:`ModalPaginator.message`.

        Parameters
        -----------
        interaction: :class:`discord.Interaction`
            The interaction to edit.
        """
        self.next_page.disabled = True
        self.previous_page.disabled = True
        self.open_button.disabled = True
        self.finish_button.disabled = True
        self.cancel_button.disabled = True
        if not interaction.response.is_done():
            await interaction.response.edit_message(view=self)
        elif self.message:
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
        obj: Union[:class:`~discord.abc.Messageable`, :class:`~discord.Interaction`, :class:`~discord.ext.commands.Context`]
            The desination to send the paginator to. if :class:`~discord.Interaction` is passed, the paginator will be sent
            as a response to the interaction or as a followup if the interaction is already responded to.
        ephemeral: :class:`bool`
            Whether the paginator should be ephemeral. Defaults to ``False``. This is only used if ``obj`` is an interaction.
        **kwargs: Any
            Additional keyword arguments to the destination's sending method.

        Returns
        --------
        Union[:class:`~discord.Message`, :class:`~discord.WebhookMessage`, :class:`~discord.InteractionMessage`]
            The message that was sent.

            :meth:`discord.Interaction.original_response` is used if ``obj`` is an :class:`discord.Interaction` and the
            interaction was not responded to. Subclass to change this behaviour.

        """  # noqa: E501
        self.validate_pages()

        if isinstance(obj, discord.Interaction):
            self.interaction = obj
            if not obj.response.is_done():
                await obj.response.send_message(self.page_string, view=self)
                self._message = await obj.original_response()
            else:
                self._message = await obj.followup.send(self.page_string, view=self, wait=True)
        else:
            self._message = await obj.send(self.page_string, view=self)

        return self.message  # type: ignore # shouldn't be None here...

    async def __send_error_message(
        self, interaction: discord.Interaction[Any], to_call: Callable[[], Dict[str, Any]]
    ) -> None:
        kwrgs = await discord.utils.maybe_coroutine(to_call)
        ERROR_MESSAGE = (
            "The error message must be a dictionary with the same keys as discord.InteractionResponse.send_message."
        )
        if not kwrgs or not isinstance(kwrgs, dict):  # pyright: ignore [reportUnnecessaryIsInstance]
            raise TypeError(ERROR_MESSAGE)

        try:
            await interaction.response.send_message(**kwrgs)
        except TypeError as e:
            raise TypeError(ERROR_MESSAGE) from e

    def get_previous_button_error_message(self) -> Dict[str, Any]:
        """The error message to send when the user tries
        to go back to a previous page but has to complete the current modal first.

        You can override this to change the error message that is sent using a
        dictonary with the same keys as :meth:`interaction.response.send_message <discord.InteractionResponse.send_message>`.

        This is called in the "Previous" button.

        The default implementation is the following:

        ``{"content": "Please complete the current modal before going back.", "ephemeral": True, "delete_after": 5}``

        This should be overriden in a subclass and is optional async.

        .. versionadded:: 1.1

        Returns
        --------
        :class:`dict`
            The error message to send.
        """
        return {
            "content": "Please complete the current modal before going back.",
            "ephemeral": True,
            "delete_after": 5,
        }

    def get_next_button_error_message(self) -> Dict[str, Any]:
        """The error message to send when the user tries
        to go to the next page but has to complete the current modal first.

        You can override this to change the error message that is sent using a
        dictonary with the same keys as :meth:`interaction.response.send_message <discord.InteractionResponse.send_message>`.

        This is called in the "Next" button.

        The default implementation is the following:

        ``{"content": "Please complete the current modal before going to the next one.", "ephemeral": True, "delete_after": 5}``

        This should be overriden in a subclass and is optional async.

        .. versionadded:: 1.1

        Returns
        --------
        :class:`dict`
            The error message to send.
        """
        return {
            "content": "Please complete the current modal before going to the next one.",
            "ephemeral": True,
            "delete_after": 5,
        }

    def get_open_button_error_message(self) -> Dict[str, Any]:
        """The error message to send when the user tries
        to open the modal but :attr:`ModalPaginator.current_modal` is ``None``.

        You can override this to change the error message that is sent using a
        dictonary with the same keys as :meth:`interaction.response.send_message <discord.InteractionResponse.send_message>`.

        This is called in the "Open" button.

        The default implementation is the following:

        ``{"content": "Please complete the current modal before going to the next one.", "ephemeral": True, "delete_after": 5}``

        This should be overriden in a subclass and is optional async.

        .. versionadded:: 1.1

        Returns
        --------
        :class:`dict`
            The error message to send.
        """
        return {
            "content": "Something went wrong... there is no current modal. Please report this to the developer.",
            "ephemeral": True,
            "delete_after": 5,
        }

    def get_finish_button_error_message(self) -> Dict[str, Any]:
        """The error message to send when the user tries to press the "Finish" button
        but not all required modals are finished.

        You can override this to change the error message that is sent using a
        dictonary with the same keys as :meth:`interaction.response.send_message <discord.InteractionResponse.send_message>`.

        This is called in the "Finish" button.

        The default implementation is the following:

        ``{"content": "You shouldn't be able to press this button... please finish all required modals.", "ephemeral": True, "delete_after": 5}``

        This should be overriden in a subclass and is optional async.

        .. versionadded:: 1.1

        Returns
        --------
        :class:`dict`
            The error message to send.
        """
        return {
            "content": "You shouldn't be able to press this button... please finish all required modals.",
            "ephemeral": True,
            "delete_after": 5,
        }

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.blurple, row=1, custom_id="PREVIOUS")
    async def previous_page(self, interaction: discord.Interaction[Any], button: discord.ui.Button[Self]) -> None:
        if self._is_locked():
            await self.__send_error_message(interaction, self.get_previous_button_error_message)
            return

        self.current_page -= 1
        await self.update(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple, row=1, custom_id="NEXT")
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button[Self]) -> None:
        if self._is_locked():
            await self.__send_error_message(interaction, self.get_next_button_error_message)
            return

        self.current_page += 1
        await self.update(interaction)

    @discord.ui.button(label="Open", row=0, custom_id="OPEN")
    async def open_button(self, interaction: discord.Interaction[Any], button: discord.ui.Button[Self]) -> None:
        self._current_modal = self.get_modal()
        if not self.current_modal:
            await self.__send_error_message(interaction, self.get_open_button_error_message)
            return

        await interaction.response.send_modal(self.current_modal)

    @discord.ui.button(label="Finish", style=discord.ButtonStyle.green, row=2, custom_id="FINISH")
    async def finish_button(self, interaction: discord.Interaction[Any], button: discord.ui.Button[Self]) -> None:
        if not all(m.is_finished() for m in self._modals if m.required):
            await self.__send_error_message(interaction, self.get_finish_button_error_message)
            return

        await self.__finish_impl(interaction)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, row=2, custom_id="CANCEL")
    async def cancel_button(self, interaction: discord.Interaction[Any], button: discord.ui.Button[Self]) -> None:
        await self.__cancel_impl(interaction)
