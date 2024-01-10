from __future__ import annotations

__all__ = [
    "is_local_server_command",
    "is_server_private_message",
    "is_client_private_message",
    "is_server_join",
    "is_server_part",
    "is_room_state",
    "is_notice",
    "is_global_user_state",
]

from typing import TypeGuard

from .commands import (ClientPrivateMessage, GlobalUserState,
                       LocalServerCommand, Notice, RoomState, ServerJoin,
                       ServerPart, ServerPrivateMessage)


def is_local_server_command(value: object, /) -> TypeGuard[LocalServerCommand]:
    """Return true if ``value`` is a room-local server command, otherwise false"""
    return type(value) in {
        ServerPrivateMessage,
        ServerJoin,
        ServerPart,
        RoomState,
        Notice,
        GlobalUserState,
    }


def is_server_private_message(value: object, /) -> TypeGuard[ServerPrivateMessage]:
    """Return true if ``value`` is a ``ServerPrivateMessage``, otherwise false"""
    return type(value) is ServerPrivateMessage


def is_client_private_message(value: object, /) -> TypeGuard[ClientPrivateMessage]:
    """Return true if ``value`` is a ``ClientPrivateMessage``, otherwise false"""
    return type(value) is ClientPrivateMessage


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
