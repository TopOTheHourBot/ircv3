from __future__ import annotations

__all__ = [
    "Pong",
    "Ping",
]

from typing import Final, Literal, Self, final, override

from ...abc import (IRCv3ClientCommandProtocol, IRCv3CommandProtocol,
                    IRCv3ServerCommandProtocol)


@final
class Pong(IRCv3ClientCommandProtocol):

    __slots__ = ("_comment")
    _comment: str
    name: Final[Literal["PONG"]] = "PONG"
    arguments: Final[tuple[()]] = ()
    tags: Final[None] = None

    def __init__(self, comment: str) -> None:
        self._comment = comment

    @property
    @override
    def comment(self) -> str:
        return self._comment


@final
class Ping(IRCv3ServerCommandProtocol):

    __slots__ = ("_comment")
    _comment: str
    name: Final[Literal["PING"]] = "PING"
    arguments: Final[tuple[()]] = ()
    tags: Final[None] = None
    source: Final[None] = None

    def __init__(self, comment: str) -> None:
        self._comment = comment

    @property
    @override
    def comment(self) -> str:
        return self._comment

    @classmethod
    def cast(cls, command: IRCv3CommandProtocol) -> Self:
        """Reinterpret ``command`` as a new ``Ping`` instance"""
        assert command.name == "PING"
        assert len(command.arguments) == 0
        assert command.comment is not None
        assert command.tags is None
        assert command.source is None
        return cls(command.comment)

    def reply(self) -> Pong:
        """Return a new ``Pong`` in reply to this ping"""
        return Pong(self.comment)
