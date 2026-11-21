"""Core path canonicalization logic.

The canonical form is defined as a pure string transformation:

* Empty input becomes ``"."``.
* Redundant separators are collapsed.
* ``.`` segments are removed.
* ``..`` segments remove the preceding segment when possible; otherwise they
  are kept (for relative paths) or dropped (for absolute paths).
* On case-insensitive filesystems, ASCII letters in each segment are lowercased.

The implementation deliberately does not touch the filesystem, so it is
portable and deterministic.  This means it cannot resolve symlinks; callers
that need that should use :func:`os.path.realpath` after canonicalization.
"""

from __future__ import annotations

import ntpath
import posixpath
import sys

__all__ = ["canonicalize"]


def _normalize_case(path: str, case_insensitive: bool) -> str:
    """Lowercase ASCII letters in *path* when *case_insensitive* is true.

    We restrict the transformation to ASCII so that the result is stable
    across locales and does not accidentally mangle non-ASCII path segments
    that may be case-sensitive on some filesystems.
    """
    if not case_insensitive:
        return path
    return "".join(ch.lower() if "A" <= ch <= "Z" else ch for ch in path)


def _is_absolute(path: str, flavour: str) -> bool:
    """Return whether *path* is absolute for the given path flavour."""
    if flavour == "nt":
        return ntpath.isabs(path)
    return posixpath.isabs(path)


def _split(path: str, flavour: str) -> list[str]:
    """Split a path into segments, ignoring the root marker."""
    if flavour == "nt":
        # ntpath.splitdrive returns (drive, tail) where drive may be "C:" or "\\server\share".
        drive, tail = ntpath.splitdrive(path)
        segments = tail.replace("\\", "/").split("/")
    else:
        segments = path.split("/")
    return [seg for seg in segments if seg not in ("", ".")]


def _join_root(path: str, flavour: str) -> str:
    """Return the root prefix of *path* (drive plus initial separator)."""
    if flavour == "nt":
        drive, tail = ntpath.splitdrive(path)
        if tail.startswith("\\") or tail.startswith("/"):
            return drive + "\\"
        return drive
    return "/" if path.startswith("/") else ""


def canonicalize(path: str, *, case_insensitive: bool | None = None, flavour: str | None = None) -> str:
    """Return the canonical form of *path*.

    Parameters
    ----------
    path:
        The path to canonicalize.  It may be relative or absolute.
    case_insensitive:
        If ``True``, ASCII letters are lowercased.  If ``None`` (the default),
        the value is chosen from the current platform: ``True`` on Windows and
        macOS, ``False`` elsewhere.
    flavour:
        ``"posix"`` or ``"nt"``.  If ``None`` (the default), the flavour is
        chosen from the current platform.  This controls how absolute paths
        and drive letters are recognized.

    Returns
    -------
    str
        The canonical path.  The empty string becomes ``"."``.  A path that
        becomes empty after processing (for example ``"a/.."``) is returned
        as ``"."`` for relative paths and as the root for absolute paths.

    Examples
    --------
    >>> canonicalize("a//b/./c/../d")
    'a/b/d'
    >>> canonicalize("/a/../../b")
    '/b'
    >>> canonicalize("", case_insensitive=False)
    '.'
    """
    if not isinstance(path, str):
        raise TypeError("path must be a string")

    if flavour is None:
        flavour = "nt" if sys.platform.startswith("win") else "posix"
    if flavour not in ("posix", "nt"):
        raise ValueError("flavour must be 'posix' or 'nt'")

    if case_insensitive is None:
        case_insensitive = flavour == "nt" or sys.platform == "darwin"

    if path == "":
        return "."

    absolute = _is_absolute(path, flavour)
    root = _join_root(path, flavour) if absolute else ""
    segments = _split(path, flavour)

    resolved: list[str] = []
    for segment in segments:
        if segment == "..":
            if resolved and resolved[-1] != "..":
                resolved.pop()
            elif not absolute:
                resolved.append("..")
            # For absolute paths, ".." at the root is dropped.
        else:
            resolved.append(segment)

    if case_insensitive:
        resolved = [_normalize_case(seg, True) for seg in resolved]
        root = _normalize_case(root, True)

    if flavour == "nt":
        # Use backslash as the separator for Windows-style paths.
        joined = "\\".join(resolved)
        if absolute:
            if joined:
                return root + joined
            return root
        return joined if joined else "."
    else:
        joined = "/".join(resolved)
        if absolute:
            return root + joined if joined else root
        return joined if joined else "."
