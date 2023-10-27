from __future__ import annotations

__all__ = [
    "is_client_private_message",
    "is_server_private_message",
    "is_client_join",
    "is_server_join",
    "is_ping",
    "is_pong",
    "is_room_state",
]

from typing import TypeGuard

from .commands import (ClientJoin, ClientPrivateMessage, Ping, Pong, RoomState,
                       ServerJoin, ServerPrivateMessage)


def is_client_private_message(value: object, /) -> TypeGuard[ClientPrivateMessage]:
    """Return true if ``value`` is a ``ClientPrivateMessage``, otherwise false"""
    return type(value) is ClientPrivateMessage


def is_server_private_message(value: object, /) -> TypeGuard[ServerPrivateMessage]:
    """Return true if ``value`` is a ``ServerPrivateMessage``, otherwise false"""
    return type(value) is ServerPrivateMessage


def is_client_join(value: object, /) -> TypeGuard[ClientJoin]:
    """Return true if ``value`` is a ``ClientJoin``, otherwise false"""
    return type(value) is ClientJoin


def is_server_join(value: object, /) -> TypeGuard[ServerJoin]:
    """Return true if ``value`` is a ``ServerJoin``, otherwise false"""
    return type(value) is ServerJoin


def is_ping(value: object, /) -> TypeGuard[Ping]:
    """Return true if ``value`` is a ``Ping``, otherwise false"""
    return type(value) is Ping


def is_pong(value: object, /) -> TypeGuard[Pong]:
    """Return true if ``value`` is a ``Pong``, otherwise false"""
    return type(value) is Pong


def is_room_state(value: object, /) -> TypeGuard[RoomState]:
    """Return true if ``value`` is a ``RoomState``, otherwise false"""
    return type(value) is RoomState
