from __future__ import annotations

__all__ = [
    "LocalServerCommand",
    "User",
    "ClientPrivateMessage",
    "ServerPrivateMessage",
    "ClientJoin",
    "ServerJoin",
    "ClientPart",
    "ServerPart",
    "RoomState",
]

from abc import ABCMeta, abstractmethod
from collections.abc import Mapping
from typing import Final, Literal, Optional, Self, final, override

from ...abc import (IRCv3ClientCommandProtocol, IRCv3CommandProtocol,
                    IRCv3ServerCommandProtocol)

type LocalServerCommand = ServerPrivateMessage | ServerJoin | ServerPart | RoomState

MIN_NAME_SIZE: Final[Literal[3]] = 3  #: Size of the shortest possible Twitch name


@final
class User:

    __slots__ = ("_message")
    __match_args__ = (
        "id",
        "name",
        "source_name",
        "display_name",
        "color",
        "mod",
        "vip",
        "sub",
    )
    _message: ServerPrivateMessage

    def __init__(self, message: ServerPrivateMessage) -> None:
        self._message = message

    def __str__(self) -> str:
        return self.name

    @property
    def id(self) -> str:
        """The user's identifier"""
        return self._message.tags["user-id"]

    @property
    def name(self) -> str:
        """The user's name

        The user's display name if it was set, otherwise their source name.
        """
        return self.display_name or self.source_name

    @property
    def source_name(self) -> str:
        """The user's source name"""
        source = self._message.source
        return source[:source.find("!", MIN_NAME_SIZE)]

    @property
    def display_name(self) -> Optional[str]:
        """The user's display name"""
        return self._message.tags["display-name"] or None

    @property
    def color(self) -> Optional[str]:
        """The user's name color

        ``None`` if the user has not set a name color.
        """
        return self._message.tags["color"] or None

    @property
    def mod(self) -> bool:
        """True if the user is a moderator, otherwise false"""
        return not not int(self._message.tags["mod"])

    @property
    def vip(self) -> bool:
        """True if the user is a VIP, otherwise false"""
        return "vip" in self._message.tags  # Presence indicates they're a VIP

    @property
    def sub(self) -> bool:
        """True if the user is a subscriber, otherwise false"""
        return not not int(self._message.tags["subscriber"])


class BasePrivateMessage(IRCv3CommandProtocol, metaclass=ABCMeta):

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
class ClientPrivateMessage(BasePrivateMessage, IRCv3ClientCommandProtocol):

    __slots__ = ("_room", "_comment", "_tags")
    _room: str
    _comment: str
    _tags: Optional[Mapping[str, str]]

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
class ServerPrivateMessage(BasePrivateMessage, IRCv3ServerCommandProtocol):

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
    def sent(self) -> int:
        """The time at which the message was sent"""
        return int(self.tags["tmi-sent-ts"])

    @property
    def sender(self) -> User:
        """The message's sender"""
        return User(self)

    @classmethod
    def cast(cls, command: IRCv3CommandProtocol) -> Self:
        """Reinterpret ``command`` as a new ``ServerPrivateMessage`` instance"""
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

    def reply(self, comment: str) -> ClientPrivateMessage:
        """Return a new ``ClientPrivateMessage`` in reply to this message"""
        return ClientPrivateMessage(
            self.room,
            comment,
            tags={"reply-parent-msg-id": self.id},
        )


class BaseJoin(IRCv3CommandProtocol, metaclass=ABCMeta):

    name: Final[Literal["JOIN"]] = "JOIN"
    comment: Final[None] = None
    tags: Final[None] = None


@final
class ClientJoin(BaseJoin, IRCv3ClientCommandProtocol):

    __slots__ = ("_rooms")
    _rooms: tuple[str, ...]

    def __init__(self, *rooms: str) -> None:
        self._rooms = rooms

    @property
    @override
    def arguments(self) -> tuple[str]:
        return (",".join(self.rooms),)

    @property
    def rooms(self) -> tuple[str, ...]:
        """The rooms to join"""
        return self._rooms


@final
class ServerJoin(BaseJoin, IRCv3ServerCommandProtocol):

    __slots__ = ("_room", "_source")
    _room: str
    _source: str

    def __init__(self, room: str, *, source: str) -> None:
        self._room = room
        self._source = source

    @property
    @override
    def arguments(self) -> tuple[str]:
        return (self.room,)

    @property
    @override
    def source(self) -> str:
        return self._source

    @property
    def room(self) -> str:
        """The room that was joined"""
        return self._room

    @classmethod
    def cast(cls, command: IRCv3CommandProtocol) -> Self:
        """Reinterpret ``command`` as a new ``ServerJoin`` instance"""
        assert command.name == "JOIN"
        assert len(command.arguments) == 1
        assert command.comment is None
        assert command.tags is None
        assert command.source is not None
        return cls(
            command.arguments[0],
            source=command.source,
        )


class BasePart(IRCv3CommandProtocol, metaclass=ABCMeta):

    name: Final[Literal["PART"]] = "PART"
    comment: Final[None] = None
    tags: Final[None] = None


@final
class ClientPart(BasePart, IRCv3ClientCommandProtocol):

    __slots__ = ("_rooms")
    _rooms: tuple[str, ...]

    def __init__(self, *rooms: str) -> None:
        self._rooms = rooms

    @property
    @override
    def arguments(self) -> tuple[str]:
        return (",".join(self.rooms),)

    @property
    def rooms(self) -> tuple[str, ...]:
        """The rooms to part from"""
        return self._rooms


@final
class ServerPart(BasePart, IRCv3ServerCommandProtocol):

    __slots__ = ("_room", "_source")
    _room: str
    _source: str

    def __init__(self, room: str, *, source: str) -> None:
        self._room = room
        self._source = source

    @property
    @override
    def arguments(self) -> tuple[str]:
        return (self.room,)

    @property
    @override
    def source(self) -> str:
        return self._source

    @property
    def room(self) -> str:
        """The room that was parted"""
        return self._room

    @classmethod
    def cast(cls, command: IRCv3CommandProtocol) -> Self:
        """Reinterpret ``command`` as a new ``ServerPart`` instance"""
        assert command.name == "PART"
        assert len(command.arguments) == 1
        assert command.comment is None
        assert command.tags is None
        assert command.source is not None
        return cls(
            command.arguments[0],
            source=command.source,
        )


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
        """The room's slow mode duration

        ``None`` if the room's slow mode has not changed.
        """
        delay = self.tags.get("slow")
        if delay is None:
            return
        return int(delay)

    @property
    def emote_only(self) -> Optional[bool]:
        """True if the room is in emote-only mode, otherwise false

        ``None`` if the room's emote-only mode has not changed.
        """
        emote_only = self.tags.get("emote-only")
        if emote_only is None:
            return
        return not not int(emote_only)

    @property
    def subs_only(self) -> Optional[bool]:
        """True if the room is in subscribers-only mode, otherwise false

        ``None`` if the room's subscribers-only mode has not changed.
        """
        subs_only = self.tags.get("subs-only")
        if subs_only is None:
            return
        return not not int(subs_only)

    @classmethod
    def cast(cls, command: IRCv3CommandProtocol) -> Self:
        """Reinterpret ``command`` as a new ``RoomState`` instance"""
        assert command.name == "ROOMSTATE"
        assert len(command.arguments) == 1
        assert command.comment is None
        assert command.tags is not None
        assert command.source is not None
        return cls(
            command.arguments[0],
            tags=command.tags,
            source=command.source,
        )
