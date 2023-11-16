from __future__ import annotations

__all__ = [
    "is_ping",
    "is_pong",
]

from typing import TypeGuard

from .commands import Ping, Pong


def is_pong(value: object, /) -> TypeGuard[Pong]:
    """Return true if ``value`` is a ``Pong``, otherwise false"""
    return type(value) is Pong


def is_ping(value: object, /) -> TypeGuard[Ping]:
    """Return true if ``value`` is a ``Ping``, otherwise false"""
    return type(value) is Ping
