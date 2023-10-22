import pytest

from whool.cli import main


def test_help(capsys):
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
def test_help_sysexit(help_args, capsys):
    with pytest.raises(SystemExit) as e:
        main(help_args)
        assert e.value == 2
    captured = capsys.readouterr()
    assert captured.out.startswith("usage: ")
