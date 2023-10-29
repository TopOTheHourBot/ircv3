from __future__ import annotations

__all__ = [
    "IRCv3CommandProtocol",
    "IRCv3ClientCommandProtocol",
    "IRCv3ServerCommandProtocol",
]

import itertools
from abc import ABCMeta, abstractmethod
from collections.abc import Mapping, Sequence
from typing import Final, Optional


class IRCv3CommandProtocol(metaclass=ABCMeta):

    __slots__ = ()

    def __str__(self) -> str:
        parts = []
        if (tags := self.tags) is not None:
            parts.append("@" + ";".join(itertools.starmap(lambda label, value: f"{label}={value}", tags.items())))
        if (source := self.source) is not None:
            parts.append(":" + source)
        parts.append(self.name)
        parts.extend(self.arguments)
        if (comment := self.comment) is not None:
            parts.append(":" + comment)
        return " ".join(parts)

    @property
    @abstractmethod
    def name(self) -> str:
        """The command's name"""
        raise NotImplementedError

    @property
    @abstractmethod
    def arguments(self) -> Sequence[str]:
        """The command's arguments

        Note that this does not include the commentary (AKA trailing) argument.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def comment(self) -> Optional[str]:
        """The command's commentary argument"""
        raise NotImplementedError

    @property
    @abstractmethod
    def tags(self) -> Optional[Mapping[str, str]]:
        """The command's tags"""
        raise NotImplementedError

    @property
    @abstractmethod
    def source(self) -> Optional[str]:
        """The command's source"""
        raise NotImplementedError


class IRCv3ClientCommandProtocol(IRCv3CommandProtocol, metaclass=ABCMeta):

    __slots__ = ()
    source: Final[None] = None  # Clients must not provide a source


class IRCv3ServerCommandProtocol(IRCv3CommandProtocol, metaclass=ABCMeta):

    __slots__ = ()
