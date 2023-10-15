from __future__ import annotations

__all__ = [
    "User",
    "ClientPrivmsg",
    "ServerPrivmsg",
    "ClientJoin",
    "ServerJoin",
    "Ping",
    "Pong",
    "RoomState",
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
        return self._tags["user-id"]

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
        return self._tags["color"] or None

    @property
    def mod(self) -> bool:
        """True if the user is a moderator, otherwise false"""
        return not not int(self._tags["mod"])

    @property
    def vip(self) -> bool:
        """True if the user is a VIP, otherwise false"""
        return "vip" in self._tags  # Presence indicates they're a VIP

    @property
    def sub(self) -> bool:
        """True if the user is a subscriber, otherwise false"""
        return not not int(self._tags["subscriber"])


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
    _tags: Mapping[str, str]
    _source: str

    def __init__(self, room: str, comment: str, *, tags: Mapping[str, str], source: str) -> None:
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
    def tags(self) -> Mapping[str, str]:
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
    def id(self) -> str:
        """The message's identifier"""
        return self.tags["id"]

    @property
    def timestamp(self) -> int:
        """The time at which the message was sent"""
        return int(self.tags["tmi-sent-ts"])

    @property
    def author(self) -> User:
        """The message's author"""
        return User(self.tags, self.source)

    @classmethod
    def cast(cls, command: IRCv3CommandProtocol) -> Self:
        """Reinterpret ``command`` as a new ``ServerPrivmsg`` instance"""
        assert command.name == "PRIVMSG"
        assert len(command.arguments) == 1
        assert command.comment is not None
        assert command.source is not None
        assert command.tags is not None
        return cls(
            command.arguments[0],
            command.comment,
            tags=command.tags,
            source=command.source,
        )

    def reply(self, comment: str) -> ClientPrivmsg:
        """Return a new ``ClientPrivmsg`` in reply to this message"""
        return ClientPrivmsg(
            self.room,
            comment,
            tags={"reply-parent-msg-id": self.id},
        )


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


@final
class RoomState(IRCv3ServerCommandProtocol):

    __slots__ = ("_room", "_tags", "_source")
    _room: str
    _tags: Mapping[str, str]
    _source: str
    name: Final[Literal["ROOMSTATE"]] = "ROOMSTATE"
    comment: Final[None] = None

    def __init__(self, room: str, *, tags: Mapping[str, str], source: str) -> None:
        self._room = room
        self._tags = tags
        self._source = source

    @property
    @override
    def arguments(self) -> tuple[str]:
        return (self.room,)

    @property
    @override
    def tags(self) -> Mapping[str, str]:
        return self._tags

    @property
    @override
    def source(self) -> str:
        return self._source

    @property
    def room(self) -> str:
        """The room this state pertains to"""
        return self._room

    @property
    def delay(self) -> Optional[int]:
        """The amount of time, in seconds, for which subsequent messages are
        allowed to be sent to the room

        Also known as "slow mode" in the Twitch moderator interface. ``None``
        if the delay has not been changed.
        """
        delay = self.tags.get("slow")
        if delay is None:
            return
        return int(delay)
