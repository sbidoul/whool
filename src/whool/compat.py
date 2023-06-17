import sys

__all__ = [
    "importlib_metadata",
    "tomllib",
]

if sys.version_info < (3, 8):  # pragma: no cover (<PY38)
    import importlib_metadata
else:  # pragma: no cover (PY38+)
    import importlib.metadata as importlib_metadata

if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib
