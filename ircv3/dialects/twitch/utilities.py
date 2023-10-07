from __future__ import annotations

__all__ = ["is_privmsg"]

from typing import TypeGuard

from .commands import ServerPrivmsg


def is_privmsg(value: object, /) -> TypeGuard[ServerPrivmsg]:
    """Return true if ``value`` is a ``ServerPrivmsg``, otherwise false"""
    return type(value) is ServerPrivmsg  # Exact type check is faster for negative tests
