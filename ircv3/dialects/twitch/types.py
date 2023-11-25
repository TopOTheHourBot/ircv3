from __future__ import annotations

__all__ = ["SupportsClientProperties"]

from abc import abstractmethod
from typing import Protocol


class SupportsClientProperties(Protocol):

    @property
    @abstractmethod
    def name(self) -> str:
        """The client's source IRC name"""
        raise NotImplementedError

    @property
    def display_name(self) -> str:
        """The client's display name

        Equivalent to ``name`` if a display name is not available.
        """
        return self.name

    @property
    def handle(self) -> str:
        """The client's handle"""
        return "@" + self.display_name

    @property
    def room(self) -> str:
        """The client's room"""
        return "#" + self.name
