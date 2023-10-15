from __future__ import annotations

__all__ = [
    "User",
    "ClientPrivmsg",
    "ServerPrivmsg",
    "ClientJoin",
    "ServerJoin",
    "Ping",
    "Pong",
]

from abc import abstractmethod
from collections.abc import Mapping, Sequence
from typing import Final, Literal, Optional, Protocol, Self, final, override

from ...protocols import (IRCv3ClientCommandProtocol, IRCv3CommandProtocol,
                          IRCv3ServerCommandProtocol)

MIN_NAME_SIZE: Final[Literal[3]] = 3  #: Size of the shortest possible Twitch name


@final
class User:

    __slots__ = ("_tags", "_source")
    __match_args__ = ("id", "name", "color", "mod", "vip", "sub")
    _tags: Mapping[str, str]
    _source: str

    def __init__(self, tags: Mapping[str, str], source: str) -> None:
        self._tags = tags
        self._source = source

    def __str__(self) -> str:
        return self.name

    @property
    def id(self) -> str:
        """The user's identifier"""
        value = self._tags.get("user-id")
        assert value is not None
        return value

    @property
    def name(self) -> str:
        """The user's name

        The user's display name if it was set, otherwise their IRC name.
        """
        value = self._tags.get("display-name")
        if not value:
            source = self._source
            return source[:source.find("!", MIN_NAME_SIZE)]
        return value

    @property
    def color(self) -> Optional[str]:
        """The user's name color

        ``None`` if the user has not set a name color.
        """
        value = self._tags.get("color")
        assert value is not None
        return value or None

    @property
    def mod(self) -> bool:
        """True if the user is a moderator, otherwise false"""
        value = self._tags.get("mod")
        assert value is not None
        return not not int(value)

    @property
    def vip(self) -> bool:
        """True if the user is a VIP, otherwise false"""
        return "vip" in self._tags  # Presence indicates they're a VIP

    @property
    def sub(self) -> bool:
        """True if the user is a subscriber, otherwise false"""
        value = self._tags.get("subscriber")
        assert value is not None
        return not not int(value)


class PrivmsgProtocol(IRCv3CommandProtocol, Protocol):

    name: Final[Literal["PRIVMSG"]] = "PRIVMSG"

    @property
    @override
    def arguments(self) -> tuple[str]:
        return (self.room,)

    @property
    @override
    @abstractmethod
    def comment(self) -> str:  # No longer optional
        raise NotImplementedError

    @property
    @abstractmethod
    def room(self) -> str:
        """The room this message was sent to"""
        raise NotImplementedError


@final
class ClientPrivmsg(IRCv3ClientCommandProtocol, PrivmsgProtocol):

    __slots__ = ("_room", "_comment", "_tags")
    _room: str
    _comment: str
    _tags: Optional[Mapping[str, str]]
    source: Final[None] = None

    def __init__(self, room: str, comment: str, *, tags: Optional[Mapping[str, str]] = None) -> None:
        self._room = room
        self._comment = comment
        self._tags = tags

    @property
    @override
    def comment(self) -> str:
        return self._comment

    @property
    @override
    def tags(self) -> Optional[Mapping[str, str]]:
        return self._tags

    @property
    @override
    def room(self) -> str:
        return self._room


@final
class ServerPrivmsg(IRCv3ServerCommandProtocol, PrivmsgProtocol):

    __slots__ = ("_room", "_comment", "_tags", "_source")
    _room: str
    _comment: str
    _tags: Optional[Mapping[str, str]]
    _source: str

    def __init__(self, room: str, comment: str, *, tags: Optional[Mapping[str, str]] = None, source: str) -> None:
        self._room = room
        self._comment = comment
        self._tags = tags
        self._source = source

    @property
    @override
    def comment(self) -> str:
        return self._comment

    @property
    @override
    def tags(self) -> Optional[Mapping[str, str]]:
        return self._tags

    @property
    @override
    def source(self) -> str:
        return self._source

    @property
    @override
    def room(self) -> str:
        return self._room

    @property
    def id(self) -> Optional[str]:
        """The message's identifier

        ``None`` if the message is untagged.
        """
        tags = self.tags or {}
        return tags.get("id")

    @property
    def timestamp(self) -> Optional[int]:
        """The time at which the message was sent

        ``None`` if the message is untagged.
        """
        tags = self.tags or {}
        value = tags.get("tmi-sent-ts")
        if value is None:
            return
        return int(value)

    @property
    def author(self) -> User | str:
        """The message's author

        The author's IRC name if the message is untagged, otherwise an instance
        of ``User``.
        """
        source = self.source
        tags = self.tags
        if tags is None:
            return source[:source.find("!", MIN_NAME_SIZE)]
        return User(tags, source)

    @classmethod
    def cast(cls, command: IRCv3CommandProtocol) -> Self:
        """Reinterpret ``command`` as a new ``ServerPrivmsg`` instance"""
        assert command.name == "PRIVMSG"
        assert len(command.arguments) == 1
        assert command.comment is not None
        assert command.source is not None
        return cls(
            command.arguments[0],
            command.comment,
            tags=command.tags,
            source=command.source,
        )

    def reply(self, comment: str) -> ClientPrivmsg:
        """Return a new ``ClientPrivmsg`` in reply to this message

        Uses the tag-based reply system provided by the Twitch server if the
        message is tagged, otherwise begins ``comment`` by at-mentioning the
        user with their IRC name.
        """
        id = self.id
        if id is None:
            comment = f"@{self.author} {comment}"
            tags = None
        else:
            tags = {"reply-parent-msg-id": id}
        return ClientPrivmsg(self.room, comment, tags=tags)


class JoinProtocol(IRCv3CommandProtocol, Protocol):

    name: Final[Literal["JOIN"]] = "JOIN"
    comment: Final[None] = None
    tags: Final[None] = None

    @property
    @override
    def arguments(self) -> tuple[str]:
        return (",".join(self.rooms),)

    @property
    @abstractmethod
    def rooms(self) -> Sequence[str]:
        """The rooms to join"""
        raise NotImplementedError


@final
class ClientJoin(IRCv3ClientCommandProtocol, JoinProtocol):

    __slots__ = ("_rooms")
    _rooms: tuple[str, ...]
    source: Final[None] = None

    def __init__(self, *rooms: str) -> None:
        self._rooms = rooms

    @property
    @override
    def rooms(self) -> tuple[str, ...]:
        return self._rooms


@final
class ServerJoin(IRCv3ServerCommandProtocol, JoinProtocol):

    __slots__ = ("_rooms", "_source")
    _rooms: tuple[str, ...]
    _source: str

    def __init__(self, *rooms: str, source: str) -> None:
        self._rooms = rooms
        self._source = source

    @property
    @override
    def rooms(self) -> tuple[str, ...]:
        return self._rooms

    @property
    @override
    def source(self) -> str:
        return self._source

    @classmethod
    def cast(cls, command: IRCv3CommandProtocol) -> Self:
        """Reinterpret ``command`` as a new ``ServerJoin`` instance"""
        assert command.name == "JOIN"
        assert len(command.arguments) == 1
        assert command.comment is None
        assert command.tags is None
        assert command.source is not None
        return cls(
            *command.arguments[0].split(","),
            source=command.source,
        )


class PingPongProtocol(IRCv3CommandProtocol, Protocol):

    arguments: Final[tuple[()]] = ()
    tags: Final[None] = None
    source: Final[None] = None

    @property
    @override
    @abstractmethod
    def comment(self) -> str:  # No longer optional
        raise NotImplementedError


@final
class Pong(PingPongProtocol):

    __slots__ = ("_comment")
    _comment: str
    name: Final[Literal["PONG"]] = "PONG"

    def __init__(self, comment: str) -> None:
        self._comment = comment

    @property
    @override
    def comment(self) -> str:
        return self._comment


@final
class Ping(PingPongProtocol):

    __slots__ = ("_comment")
    _comment: str
    name: Final[Literal["PING"]] = "PING"

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
