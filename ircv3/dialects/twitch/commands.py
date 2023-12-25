from __future__ import annotations

__all__ = [
    "LocalServerCommand",
    "ExternalClient",
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

from ...abc import (ClientCommandProtocol, CommandProtocol,
                    ServerCommandProtocol)
from .types import SupportsClientProperties

type LocalServerCommand = ServerPrivateMessage | ServerJoin | ServerPart | RoomState

MIN_NAME_SIZE: Final[Literal[3]] = 3  #: Size of the shortest possible Twitch name


@final
class ExternalClient(SupportsClientProperties):
    """A data class that represents the sending client of a PRIVMSG command
    arriving from the Twitch IRC server - an "external" client
    """

    __slots__ = ("_message",)

    _message: ServerPrivateMessage

    def __init__(self, message: ServerPrivateMessage) -> None:
        self._message = message

    def __str__(self) -> str:
        return self.handle

    @property
    @override
    def name(self) -> str:
        source = self.message.source
        return source[:source.find("!", MIN_NAME_SIZE)]

    @property
    @override
    def display_name(self) -> str:
        return self.message.tags["display-name"] or super().display_name

    @property
    def message(self) -> ServerPrivateMessage:
        """The client's message"""
        return self._message

    @property
    def id(self) -> str:
        """The client's identifier"""
        return self.message.tags["user-id"]

    @property
    def color(self) -> str:
        """The client's name color

        An empty string if the client has not set a color.
        """
        return self.message.tags["color"]

    @property
    def is_broadcaster(self) -> bool:
        """True if the client is the broadcaster associated with the message's
        room, otherwise false
        """
        return self.room == self.message.room

    @property
    def is_moderator(self) -> bool:
        """True if the client is a moderator, otherwise false"""
        return self.message.tags["mod"] == "1"

    @property
    def is_vip(self) -> bool:
        """True if the client is a VIP, otherwise false"""
        return "vip" in self.message.tags  # Presence indicates VIP

    @property
    def is_subscriber(self) -> bool:
        """True if the client is a subscriber, otherwise false"""
        return self.message.tags["subscriber"] == "1"


class PrivateMessage(CommandProtocol, metaclass=ABCMeta):

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
class ClientPrivateMessage(PrivateMessage, ClientCommandProtocol):

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

    @classmethod
    def cast(cls, command: CommandProtocol) -> Self:
        """Reinterpret ``command`` as a new ``ClientPrivateMessage`` instance"""
        assert command.name == "PRIVMSG"
        assert len(command.arguments) == 1
        assert command.comment is not None
        assert command.source is None
        return cls(
            command.arguments[0],
            command.comment,
            tags=command.tags,
        )


@final
class ServerPrivateMessage(PrivateMessage, ServerCommandProtocol):

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
    def sender(self) -> ExternalClient:
        """The message's sender"""
        return ExternalClient(self)

    @classmethod
    def cast(cls, command: CommandProtocol) -> Self:
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


class Join(CommandProtocol, metaclass=ABCMeta):

    name: Final[Literal["JOIN"]] = "JOIN"
    comment: Final[None] = None
    tags: Final[None] = None


@final
class ClientJoin(Join, ClientCommandProtocol):

    __slots__ = ("_rooms",)

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

    @classmethod
    def cast(cls, command: CommandProtocol) -> Self:
        assert command.name == "JOIN"
        assert len(command.arguments) == 1
        assert command.comment is None
        assert command.tags is None
        assert command.source is None
        return cls(*command.arguments[0].split(","))


@final
class ServerJoin(Join, ServerCommandProtocol):

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
    def cast(cls, command: CommandProtocol) -> Self:
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


class Part(CommandProtocol, metaclass=ABCMeta):

    name: Final[Literal["PART"]] = "PART"
    comment: Final[None] = None
    tags: Final[None] = None


@final
class ClientPart(Part, ClientCommandProtocol):

    __slots__ = ("_rooms",)

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

    @classmethod
    def cast(cls, command: CommandProtocol) -> Self:
        assert command.name == "PART"
        assert len(command.arguments) == 1
        assert command.comment is None
        assert command.tags is None
        assert command.source is None
        return cls(*command.arguments[0].split(","))


@final
class ServerPart(Part, ServerCommandProtocol):

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
    def cast(cls, command: CommandProtocol) -> Self:
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
class RoomState(ServerCommandProtocol):

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
    def cooldown(self) -> Optional[int]:
        """The room's message cooldown, in seconds

        ``None`` if the room's message cooldown has not changed.
        """
        cooldown = self.tags.get("slow")
        return None if cooldown is None else int(cooldown)

    @property
    def emote_only(self) -> Optional[bool]:
        """True if the room is in emote-only mode, otherwise false

        ``None`` if the room's emote-only mode has not changed.
        """
        emote_only = self.tags.get("emote-only")
        return None if emote_only is None else emote_only == "1"

    @property
    def subscribers_only(self) -> Optional[bool]:
        """True if the room is in subscribers-only mode, otherwise false

        ``None`` if the room's subscribers-only mode has not changed.
        """
        subscribers_only = self.tags.get("subs-only")
        return None if subscribers_only is None else subscribers_only == "1"

    @classmethod
    def cast(cls, command: CommandProtocol) -> Self:
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
