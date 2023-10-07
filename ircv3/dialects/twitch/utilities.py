from __future__ import annotations

__all__ = ["is_privmsg"]

from typing import TypeGuard

from .commands import Privmsg


def is_privmsg(value: object, /) -> TypeGuard[Privmsg]:
    """Return true if ``value`` is a ``Privmsg``, otherwise false"""
    return type(value) is Privmsg  # Exact type check is faster for negative tests
