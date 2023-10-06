from __future__ import annotations

__all__ = ["IRCv3CommandProtocol"]

import itertools
from abc import abstractmethod
from collections.abc import Mapping, Sequence
from typing import Optional, Protocol


class IRCv3CommandProtocol(Protocol):

    def __str__(self) -> str:
        parts = []
        if self.tags is not None:
            parts.append("@" + ";".join(itertools.starmap(lambda label, value: f"{label}={value}", self.tags.items())))
        if self.source is not None:
            parts.append(":" + self.source)
        parts.append(self.name)
        parts.extend(self.arguments)
        if self.comment is not None:
            parts.append(":" + self.comment)
        return " ".join(parts)

    @property
    @abstractmethod
    def name(self) -> str:
        """The command's name"""

    @property
    @abstractmethod
    def arguments(self) -> Sequence[str]:
        """The command's arguments

        Note that this does not include the commentary (AKA trailing) argument.
        """

    @property
    @abstractmethod
    def comment(self) -> Optional[str]:
        """The command's commentary argument"""

    @property
    @abstractmethod
    def tags(self) -> Optional[Mapping[str, str]]:
        """The command's tags"""

    @property
    @abstractmethod
    def source(self) -> Optional[str]:
        """The command's source"""
