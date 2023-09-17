from typing import Optional, Tuple

import discord


__all__ = (
    "ModalPaginatorException",
    "NotAModal",
    "NoModals",
    "InvalidButtonKey",
)


class ModalPaginatorException(discord.DiscordException):
    """Base exception class for this extension."""

    pass


class NotAModal(ModalPaginatorException):
    """Raised when input modal is not an instance/subclass of :class:`discord.ui.Modal`."""

    def __init__(
        self,
        input_value: type,
        /,
        *,
        index: Optional[int] = None,
        param_name: Optional[str] = None,
    ) -> None:
        self.input_value: type = input_value
        self.index: Optional[int] = index

        base_message = f"an instance/subclass of discord.ui.Modal, not {input_value!r}"
        message = "Expected " + (f"{param_name} to be {base_message}" if param_name else base_message)

        if index is not None:
            message += f" at index {index}"

        super().__init__(f"{message}.")


class NoModals(ModalPaginatorException):
    """Raised when no modals are added to the paginator."""

    def __init__(self) -> None:
        super().__init__("No modals have been added to the paginator.")


class InvalidButtonKey(ModalPaginatorException):
    """Raised when a button key does not exist."""

    def __init__(self, key: str, valid_keys: Tuple[str, ...]) -> None:
        self.key: str = key
        keys = ", ".join(valid_keys)
        super().__init__(f"Invalid key in button dictionary: {key!r}. Valid keys are: {keys}")
