from __future__ import annotations

__all__ = [
    "is_privmsg",
    "is_ping",
]

from typing import TypeGuard

from .commands import Ping, ServerPrivmsg


def is_privmsg(value: object, /) -> TypeGuard[ServerPrivmsg]:
    """Return true if ``value`` is a ``ServerPrivmsg``, otherwise false"""
    return type(value) is ServerPrivmsg


def is_ping(value: object, /) -> TypeGuard[Ping]:
    """Return true if ``value`` is a ``Ping``, otherwise false"""
    return type(value) is Ping
