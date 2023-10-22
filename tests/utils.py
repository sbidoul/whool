import os
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Iterator


@contextmanager
def dir_changer(path: Path) -> Iterator[None]:
    """A context manager that changes the current working directory"""
    old_cwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_cwd)


@contextmanager
def env_changer(env: Dict[str, str]) -> Iterator[None]:
    """A context manager that changes the current working directory"""
    old_env = os.environ.copy()
    os.environ.update(env)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_env)
