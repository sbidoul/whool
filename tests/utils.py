import os
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def dir_changer(path: Path) -> None:
    """A context manager that changes the current working directory"""
    old_cwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_cwd)
