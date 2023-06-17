import sys

__all__ = ["tomllib"]

if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib
