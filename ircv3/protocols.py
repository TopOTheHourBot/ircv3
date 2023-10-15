from __future__ import annotations

__all__ = [
    "Side",
    "IRCv3CommandProtocol",
    "IRCv3ClientCommandProtocol",
    "IRCv3ServerCommandProtocol",
]

import enum
import itertools
from abc import abstractmethod
from collections.abc import Mapping, Sequence
from enum import Flag
from typing import Literal, Optional, Protocol, override


class Side(Flag):
    CLIENT = enum.auto()
    SERVER = enum.auto()


class IRCv3CommandProtocol(Protocol):

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

    @property
    def side(self) -> Optional[Side]:
        """The command's side

        If ``None`` (the default), the command may be sent by either the client
        or server.
        """
        return


class IRCv3ClientCommandProtocol(IRCv3CommandProtocol, Protocol):

    @property
    @override
    def side(self) -> Literal[Side.CLIENT]:
        return Side.CLIENT


class IRCv3ServerCommandProtocol(IRCv3CommandProtocol, Protocol):

    @property
    @override
    def side(self) -> Literal[Side.SERVER]:
        return Side.SERVER
