from __future__ import annotations

__all__ = [
    "is_client_privmsg",
    "is_server_privmsg",
    "is_client_join",
    "is_server_join",
    "is_ping",
    "is_pong",
]

from typing import TypeGuard

from .commands import (ClientJoin, ClientPrivmsg, Ping, Pong, ServerJoin,
                       ServerPrivmsg)


def is_client_privmsg(value: object, /) -> TypeGuard[ClientPrivmsg]:
    """Return true if ``value`` is a ``ClientPrivmsg``, otherwise false"""
    return type(value) is ClientPrivmsg


def is_server_privmsg(value: object, /) -> TypeGuard[ServerPrivmsg]:
    """Return true if ``value`` is a ``ServerPrivmsg``, otherwise false"""
    return type(value) is ServerPrivmsg


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
