from __future__ import annotations

__all__ = [
    "User",
    "Privmsg",
    "Join",
]

from collections.abc import Mapping
from typing import Final, Literal, Optional, Self, final

from ...protocols import IRCv3CommandProtocol

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


@final
class Privmsg(IRCv3CommandProtocol):

    __slots__ = ("_room", "_comment", "_tags", "_source")
    __match_args__ = ("room", "comment", "tags", "source")
    _room: str
    _comment: str
    _tags: Optional[Mapping[str, str]]
    _source: Optional[str]
    name: Literal["PRIVMSG"] = "PRIVMSG"

    def __init__(
        self,
        room: str,
        comment: str,
        *,
        tags: Optional[Mapping[str, str]] = None,
        source: Optional[str] = None,
    ) -> None:
        self._room = room
        self._comment = comment
        self._tags = tags
        self._source = source

    @property
    def arguments(self) -> tuple[str]:
        return (self.room,)

    @property
    def comment(self) -> str:
        return self._comment

    @property
    def tags(self) -> Optional[Mapping[str, str]]:
        return self._tags

    @property
    def source(self) -> Optional[str]:
        return self._source

    @property
    def room(self) -> str:
        """The room this message was sent to"""
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
        assert source is not None
        if tags is None:
            return source[:source.find("!", MIN_NAME_SIZE)]
        return User(tags, source)

    @classmethod
    def cast(cls, command: IRCv3CommandProtocol) -> Self:
        """Reinterpret ``command`` as a new ``Privmsg`` instance"""
        assert command.name == "PRIVMSG"
        assert len(command.arguments) == 1
        assert command.comment is not None
        return cls(
            command.arguments[0],
            command.comment,
            tags=command.tags,
            source=command.source,
        )

    def reply(self, comment: str) -> Privmsg:
        """Return a new ``Privmsg`` in reply to this message

        Uses the tag-based reply system provided by the Twitch server if the
        message is tagged, otherwise begins ``comment`` by at-mentioning the
        user with their IRC name.
        """
        id = self.id
        if id is None:
            return Privmsg(self.room, f"@{self.author} {comment}")
        return Privmsg(self.room, comment, tags={"reply-parent-msg-id": id})


@final
class Join(IRCv3CommandProtocol):

    __slots__ = ("_rooms", "_source")
    _rooms: tuple[str, ...]
    _source: Optional[str]
    name: Literal["JOIN"] = "JOIN"
    comment: None = None
    tags: None = None

    def __init__(self, *rooms: str, source: Optional[str] = None) -> None:
        self._rooms = rooms
        self._source = source

    @property
    def arguments(self) -> tuple[str]:
        return (",".join(self.rooms),)

    @property
    def source(self) -> Optional[str]:
        return self._source

    @property
    def rooms(self) -> tuple[str, ...]:
        """The rooms to join"""
        return self._rooms

    @classmethod
    def cast(cls, command: IRCv3CommandProtocol) -> Self:
        """Reinterpret ``command`` as a new ``Join`` instance"""
        assert command.name == "JOIN"
        assert len(command.arguments) == 1
        assert command.comment is None
        assert command.tags is None
        return cls(
            *command.arguments[0],
            source=command.source,
        )
