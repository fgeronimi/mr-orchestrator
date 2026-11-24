from mr_orchestrator.cli import main


def test_help_returns_zero(capsys):
    assert main([]) == 0
    assert "mro" in capsys.readouterr().out


def test_unimplemented_command_returns_two():
    assert main(["sync"]) == 2
