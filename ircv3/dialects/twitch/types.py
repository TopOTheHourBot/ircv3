from __future__ import annotations

__all__ = ["SupportsClientProperties"]

from abc import abstractmethod
from typing import Protocol


class SupportsClientProperties(Protocol):

    @property
    @abstractmethod
    def name(self) -> str:
        """The client's name"""
        raise NotImplementedError

    @property
    def handle(self) -> str:
        """The client's handle"""
        return "@" + self.name

    @property
    def room(self) -> str:
        """The client's room"""
        return "#" + self.name
