from __future__ import annotations

__all__ = [
    "ExternalClient",
    "ClientMessage",
    "ServerMessage",
    "ClientJoin",
    "ServerJoin",
    "ClientPart",
    "ServerPart",
    "RoomState",
    "Notice",
    "GlobalUserState",
    "UserState",
]

from abc import ABCMeta, abstractmethod
from collections.abc import Mapping
from typing import Final, Literal, Optional, Self, final, override

from ..abc import (ClientCommandProtocol, CommandProtocol,
                    ServerCommandProtocol)

MIN_NAME_SIZE: Final[Literal[3]] = 3  #: Size of the shortest possible Twitch name


@final
class ExternalClient:
    """A data class that represents the sending client of a PRIVMSG command
    arriving from the Twitch IRC server - an "external" client
    """

    __slots__ = ("_message",)
    _message: ServerMessage

    def __init__(self, message: ServerMessage) -> None:
        self._message = message

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if type(other) is ExternalClient:
            return self.id == other.id
        return NotImplemented

    @property
    def message(self) -> ServerMessage:
        """The client's message"""
        return self._message

    @property
    def name(self) -> str:
        """The client's name"""
        source = self.message.source
        return source[:source.find("!", MIN_NAME_SIZE)]

    @property
    def display_name(self) -> str:
        """The client's display name

        Equivalent to ``name`` if a display name is not available.
        """
        return self.message.tags["display-name"] or self.name

    @property
    def handle(self) -> str:
        """The client's handle"""
        return "@" + self.display_name

    @property
    def room(self) -> str:
        """The client's room"""
        return "#" + self.name

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
    def broadcaster(self) -> bool:
        """True if the client is the broadcaster associated with the message's
        room, otherwise false
        """
        return self.room == self.message.room

    @property
    def moderator(self) -> bool:
        """True if the client is a moderator, otherwise false"""
        return self.message.tags["mod"] == "1"

    @property
    def vip(self) -> bool:
        """True if the client is a VIP, otherwise false"""
        return "vip" in self.message.tags  # Presence indicates VIP

    @property
    def subscriber(self) -> bool:
        """True if the client is a subscriber, otherwise false"""
        return self.message.tags["subscriber"] == "1"


class Message(CommandProtocol, metaclass=ABCMeta):

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
class ClientMessage(Message, ClientCommandProtocol):

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
        """Reinterpret ``command`` as a new ``ClientMessage`` instance"""
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
class ServerMessage(Message, ServerCommandProtocol):

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

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if type(other) is ServerMessage:
            return self.id == other.id
        return NotImplemented

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
        """Reinterpret ``command`` as a new ``ServerMessage`` instance"""
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

    def reply(self, comment: str) -> ClientMessage:
        """Return a new ``ClientMessage`` in reply to this message"""
        return ClientMessage(
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
        return cls(command.arguments[0], source=command.source)


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
        return cls(command.arguments[0], source=command.source)


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


@final
class Notice(ServerCommandProtocol):

    __slots__ = ("_room", "_comment", "_tags", "_source")
    _room: str
    _comment: str
    _tags: Optional[Mapping[str, str]]
    _source: str
    name: Final[Literal["NOTICE"]] = "NOTICE"

    def __init__(
        self,
        room: str,
        comment: str,
        *,
        tags: Optional[Mapping[str, str]] = None,
        source: str,
    ) -> None:
        self._room = room
        self._comment = comment
        self._tags = tags
        self._source = source

    @property
    @override
    def arguments(self) -> tuple[str]:
        return (self.room,)

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
    def room(self) -> str:
        """The room this notice pertains to

        Set to ``"*"`` if a global notice.
        """
        return self._room

    @classmethod
    def cast(cls, command: CommandProtocol) -> Self:
        """Reinterpret ``command`` as a new ``Notice`` instance"""
        assert command.name == "NOTICE"
        assert len(command.arguments) == 1
        assert command.comment is not None
        assert command.source is not None
        return cls(
            command.arguments[0],
            command.comment,
            tags=command.tags,
            source=command.source,
        )


@final
class GlobalUserState(ServerCommandProtocol):

    __slots__ = ("_tags", "_source")
    _tags: Mapping[str, str]
    _source: str
    name: Final[Literal["GLOBALUSERSTATE"]] = "GLOBALUSERSTATE"
    arguments: Final[tuple[()]] = ()
    comment: Final[None] = None

    def __init__(self, *, tags: Mapping[str, str], source: str) -> None:
        self._tags = tags
        self._source = source

    @property
    @override
    def tags(self) -> Mapping[str, str]:
        return self._tags

    @property
    @override
    def source(self) -> str:
        return self._source

    @property
    def id(self) -> str:
        return self.tags["user-id"]

    @property
    def display_name(self) -> str:
        return self.tags["display-name"]

    @property
    def color(self) -> str:
        return self.tags["color"]

    @classmethod
    def cast(cls, command: CommandProtocol) -> Self:
        """Reinterpret ``command`` as a new ``GlobalUserState`` instance"""
        assert command.name == "GLOBALUSERSTATE"
        assert len(command.arguments) == 0
        assert command.comment is None
        assert command.tags is not None
        assert command.source is not None
        return cls(
            tags=command.tags,
            source=command.source,
        )


@final
class UserState(ServerCommandProtocol):

    __slots__ = ("_room", "_tags", "_source")
    _room: str
    _tags: Mapping[str, str]
    _source: str
    name: Final[Literal["USERSTATE"]] = "USERSTATE"
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
        return self._room

    @property
    def display_name(self) -> str:
        return self.tags["display-name"]

    @property
    def color(self) -> str:
        return self.tags["color"]

    @property
    def moderator(self) -> bool:
        return self.tags["mod"] == "1"

    @property
    def subscriber(self) -> bool:
        return self.tags["subscriber"] == "1"

    @classmethod
    def cast(cls, command: CommandProtocol) -> Self:
        """Reinterpret ``command`` as a new ``UserState`` instance"""
        assert command.name == "USERSTATE"
        assert len(command.arguments) == 1
        assert command.tags is not None
        assert command.source is not None
        return cls(
            command.arguments[0],
            tags=command.tags,
            source=command.source,
        )
