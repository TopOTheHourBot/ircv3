from __future__ import annotations

__all__ = [
    "Pong",
    "Ping",
    "Welcome",
]

from typing import Final, Literal, Self, final, override

from ..abc import (ClientCommandProtocol, CommandProtocol,
                    ServerCommandProtocol)


@final
class Pong(ClientCommandProtocol):

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
class Ping(ServerCommandProtocol):

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
    def cast(cls, command: CommandProtocol) -> Self:
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


@final
class Welcome(ServerCommandProtocol):

    __slots__ = ("_user", "_comment", "_source")
    _user: str
    _comment: str
    _source: str
    name: Final[Literal["001"]] = "001"
    tags: Final[None] = None

    def __init__(self, user: str, comment: str, *, source: str) -> None:
        self._user = user
        self._comment = comment
        self._source = source

    @property
    @override
    def arguments(self) -> tuple[str]:
        return (self._user,)

    @property
    @override
    def comment(self) -> str:
        return self._comment

    @property
    @override
    def source(self) -> str:
        return self._source

    @classmethod
    def cast(cls, command: CommandProtocol) -> Self:
        """Reinterpret ``command`` as a new ``Welcome`` instance"""
        assert command.name == "001"
        assert len(command.arguments) == 1
        assert command.comment is not None
        assert command.tags is None
        assert command.source is not None
        return cls(
            command.arguments[0],
            command.comment,
            source=command.source,
        )
