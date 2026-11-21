# path-canonicalization-resolver

A small, dependency-free path canonicalizer that collapses redundant separators, resolves `.` and `..` segments, and optionally normalizes ASCII case for case-insensitive filesystems.

```python
from path_canonicalization_resolver import canonicalize

canonicalize("a//b/./c/../d")
# 'a/b/d'

canonicalize("/a/../../b")
# '/b'

canonicalize("C:\\A\\..\\B", flavour="nt", case_insensitive=True)
# 'c:\\b'
```

## Why this exists

`os.path.normpath` is close, but it does not let you choose a path flavour independently of the host platform, and it does not normalize case. This library makes both choices explicit so the same code can canonicalize Windows-style paths on Linux (useful for tests and for tools that process paths from other systems) and can apply case folding when the target filesystem is known to be case-insensitive.

The trade-off is that canonicalization is a pure string operation. It never touches the filesystem, so it cannot resolve symlinks, and it cannot know whether a particular path component is actually case-insensitive. If you need symlink resolution, pass the result to `os.path.realpath` afterward.

## The awkward edge

For relative paths, `..` segments that cannot be resolved are kept rather than dropped. `canonicalize("../a")` returns `"../a"`, because removing the leading `..` would change the meaning of the path. For absolute paths, `..` at the root is dropped, because the root has no parent. The empty path becomes `"."`, and a relative path that collapses to nothing (for example `"a/.."`) also becomes `"."`.

## API

### `canonicalize(path, *, case_insensitive=None, flavour=None) -> str`

Returns the canonical form of `path`.

- `path`: the path to canonicalize. Must be a `str`.
- `case_insensitive`: if `True`, ASCII letters are lowercased. If `None`, the value is chosen from the current platform: `True` on Windows and macOS, `False` elsewhere.
- `flavour`: `"posix"` or `"nt"`. If `None`, the flavour is chosen from the current platform. This controls how absolute paths and drive letters are recognized and which separator is used in the result.

Raises `TypeError` if `path` is not a string and `ValueError` if `flavour` is not `"posix"` or `"nt"`.
