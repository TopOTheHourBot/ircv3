from __future__ import annotations

__all__ = [
    "is_local_server_command",
    "is_server_message",
    "is_client_message",
    "is_server_join",
    "is_server_part",
    "is_room_state",
    "is_notice",
    "is_global_user_state",
]

from typing import TypeGuard

from .commands import (ClientMessage, GlobalUserState, LocalServerCommand,
                       Notice, RoomState, ServerJoin, ServerMessage,
                       ServerPart)


def is_local_server_command(value: object, /) -> TypeGuard[LocalServerCommand]:
    """Return true if ``value`` is a room-local server command, otherwise false"""
    return type(value) in {
        ServerMessage,
        ServerJoin,
        ServerPart,
        RoomState,
        Notice,
    }


def is_server_message(value: object, /) -> TypeGuard[ServerMessage]:
    """Return true if ``value`` is a ``ServerMessage``, otherwise false"""
    return type(value) is ServerMessage


def is_client_message(value: object, /) -> TypeGuard[ClientMessage]:
    """Return true if ``value`` is a ``ClientMessage``, otherwise false"""
    return type(value) is ClientMessage


def is_server_join(value: object, /) -> TypeGuard[ServerJoin]:
    """Return true if ``value`` is a ``ServerJoin``, otherwise false"""
    return type(value) is ServerJoin


def is_server_part(value: object, /) -> TypeGuard[ServerPart]:
    """Return true if ``value`` is a ``ServerPart``, otherwise false"""
    return type(value) is ServerPart


def is_room_state(value: object, /) -> TypeGuard[RoomState]:
    """Return true if ``value`` is a ``RoomState``, otherwise false"""
    return type(value) is RoomState


def is_notice(value: object, /) -> TypeGuard[Notice]:
    """Return true if ``value`` is a ``Notice``, otherwise false"""
    return type(value) is Notice


def is_global_user_state(value: object, /) -> TypeGuard[GlobalUserState]:
    """Return true if ``value`` is a ``GlobalUserState``, otherwise false"""
    return type(value) is GlobalUserState
