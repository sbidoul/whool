from typing import List

import pytest

from whool.cli import main


def test_help(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 2
    captured = capsys.readouterr()
    assert captured.out.startswith("usage: ")


@pytest.mark.parametrize(
    "help_args",
    (
        ["--help"],
        ["init", "--help"],
    ),
)
def test_help_sysexit(help_args: List[str], capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as e:
        main(help_args)
        assert e.value.code == 2
    captured = capsys.readouterr()
    assert captured.out.startswith("usage: ")
