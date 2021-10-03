from pathlib import Path

import pytest


@pytest.fixture  # type: ignore
def data_path() -> Path:
    return Path(__file__).parent / "data"
