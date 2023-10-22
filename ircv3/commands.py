from __future__ import annotations

__all__ = [
    "IRCv3Command",
    "IRCv3CommonCommand",
    "IRCv3ClientCommand",
    "IRCv3ServerCommand",
]

from collections.abc import Mapping, Sequence
from typing import Optional, Self

from .abc import (IRCv3ClientCommandProtocol, IRCv3CommandProtocol,
                  IRCv3CommonCommandProtocol, IRCv3ServerCommandProtocol)
from .parser import Parser


class IRCv3Command(IRCv3CommandProtocol):

    __slots__ = (
        "_name",
        "_arguments",
        "_comment",
        "_tags",
        "_source",
    )
    __match_args__ = (
        "name",
        "arguments",
        "comment",
        "tags",
        "source",
    )
    _name: str
    _arguments: Sequence[str]
    _comment: Optional[str]
    _tags: Optional[Mapping[str, str]]
    _source: Optional[str]

    def __init__(
        self,
        name: str,
        arguments: Sequence[str] = (),
        comment: Optional[str] = None,
        *,
        tags: Optional[Mapping[str, str]] = None,
        source: Optional[str] = None,
    ) -> None:
        self._name = name
        self._arguments = arguments
        self._comment = comment
        self._tags = tags
        self._source = source

    @property
    def name(self) -> str:
        return self._name

    @property
    def arguments(self) -> Sequence[str]:
        return self._arguments

    @property
    def comment(self) -> Optional[str]:
        return self._comment

    @property
    def tags(self) -> Optional[Mapping[str, str]]:
        return self._tags

    @property
    def source(self) -> Optional[str]:
        return self._source

    @classmethod
    def from_string(cls, string: str, /) -> Self:
        """Return a new command from a raw data string"""
        parser = Parser(string)

        if parser.peek() == "@":
            tags = {
                label.removeprefix("+"): value  # TODO: Unescape values
                for label, _, value in map(
                    lambda tag: tag.partition("="),
                    parser.take_until().split(";"),
                )
            }
            parser.advance()
        else:
            tags = None

        if parser.peek() == ":":
            source = parser.take_until()
            parser.advance()
        else:
            source = None

        name = parser.take_until(exclude_current=False)
        arguments = parser.take_until(" :", exclude_current=False).split()

        if parser.ok():
            comment = parser.advance().take_all()
        else:
            comment = None

        return cls(
            name=name,
            arguments=arguments,
            comment=comment,
            tags=tags,
            source=source,
        )


class IRCv3CommonCommand(IRCv3Command, IRCv3CommonCommandProtocol):

    __slots__ = ()


class IRCv3ClientCommand(IRCv3Command, IRCv3ClientCommandProtocol):

    __slots__ = ()


class IRCv3ServerCommand(IRCv3Command, IRCv3ServerCommandProtocol):

    __slots__ = ()
