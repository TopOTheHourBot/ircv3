from __future__ import annotations

__all__ = [
    "is_local_server_command",
    "is_server_private_message",
    "is_server_join",
    "is_server_part",
    "is_ping",
    "is_room_state",
]

from typing import TypeGuard

from .commands import (Ping, RoomState, ServerJoin, ServerPart,
                       ServerPrivateMessage)

type LocalServerCommand = ServerPrivateMessage | ServerJoin | ServerPart | RoomState


def is_local_server_command(value: object, /) -> TypeGuard[LocalServerCommand]:
    """Return true if ``value`` is a room-local server command, otherwise false"""
    return type(value) in {
        ServerPrivateMessage,
        ServerJoin,
        ServerPart,
        RoomState,
    }


def is_server_private_message(value: object, /) -> TypeGuard[ServerPrivateMessage]:
    """Return true if ``value`` is a ``ServerPrivateMessage``, otherwise false"""
    return type(value) is ServerPrivateMessage


def is_server_join(value: object, /) -> TypeGuard[ServerJoin]:
    """Return true if ``value`` is a ``ServerJoin``, otherwise false"""
    return type(value) is ServerJoin


def is_server_part(value: object, /) -> TypeGuard[ServerPart]:
    """Return true if ``value`` is a ``ServerPart``, otherwise false"""
    return type(value) is ServerPart


def is_ping(value: object, /) -> TypeGuard[Ping]:
    """Return true if ``value`` is a ``Ping``, otherwise false"""
    return type(value) is Ping


def is_room_state(value: object, /) -> TypeGuard[RoomState]:
    """Return true if ``value`` is a ``RoomState``, otherwise false"""
    return type(value) is RoomState
