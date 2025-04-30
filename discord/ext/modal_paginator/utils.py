from __future__ import annotations

from typing import Any, Generator, Generic, Iterable, Iterator, Tuple, TypeVar

import discord

T = TypeVar('T')


IS_DPY2_5 = discord.version_info >= (2, 5, 0)
# refs:
# https://canary.discord.com/channels/336642139381301249/1341405833640022098
# https://github.com/Rapptz/discord.py/issues/10107
IS_DPY_2_5_WITH_INTERACTIONEDITFIXED = discord.version_info >= (2, 5, 1)


class step_enumerate(Generic[T]):
    """A class that simulates :class:`enumerate`, but allows passing a custom
    step to increment the enumeration.

    .. versionadded:: 1.3

    Parameters
    ----------
    iterable: Iterable[Any]
        The iterable to enumerate.
    start: :class:`int`
        Where should the count start. Defaults to ``0``.
    step: :class:`int`
        How much should the count increment every time an item is returned.
        Defaults to ``1``.
    """

    __slots__ = (
        '_iterable',
        'start',
        'step',
    )

    def __init__(self, iterable: Iterable[T], start: int = 0, step: int = 1) -> None:
        self._iterable: Iterable[T] = iterable
        self.start: int = start
        self.step: int = step

    def enumerate(self) -> Generator[Tuple[int, T], Any, None]:
        """An iterator that yields a tuple of ``(pos, item)`` pair.

        Yields
        ------
        Tuple[:class:`int`, Any]
            The (pos, item) pairs.
        """

        pos = self.start

        for item in self._iterable:
            yield (pos, item)

            pos += self.step

    def __iter__(self) -> Iterator[Tuple[int, T]]:
        return iter(self.enumerate())
