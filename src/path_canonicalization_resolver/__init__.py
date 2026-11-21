"""Path canonicalization resolver.

This package exposes the :func:`canonicalize` function, which collapses
redundant separators, resolves ``.`` and ``..`` segments, and optionally
normalizes case for case-insensitive filesystems.
"""

from .core import canonicalize

__all__ = ["canonicalize"]
