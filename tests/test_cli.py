import os
import json
import pytest
from unittest.mock import patch
from multiprocessing import Process, Event
from pymem.cli import main
from click.testing import CliRunner


@pytest.fixture
def cli():
    return CliRunner()


def test_invalid_pid(cli):
    pid = os.getpid()
    with patch("pymem.cli.check_process_exist") as mock_check_process_exist:
        mock_check_process_exist.return_value = False
        result = cli.invoke(main, [str(pid)])
        assert result.exit_code == 1
        assert f"Process(pid={pid}) is not found.\n" == result.output


def test_no_debugger(cli):
    pid = os.getpid()
    with patch("distutils.spawn.find_executable") as mock_find_executable:
        mock_find_executable.return_value = ""
        result = cli.invoke(main, [str(pid)])
        assert result.exit_code == 1
        assert f"Could not find debugger in your bin path.\n" == result.output


def test_print(cli):
    def sleep_until_wake(e):
        e.wait()

    e = Event()
    p = Process(target=sleep_until_wake, args=(e,))
    p.start()
    pid = p.pid
    with patch("distutils.spawn.find_executable") as mock_find_executable:
        mock_find_executable.return_value = "/usr/bin/gdb"
        with patch("pymem.cli.get_objects") as mock_get_objects:
            mock_get_objects.return_value = [
                {
                    "type": "<class 'abc.ABCMeta'>",
                    "count": 91,
                    "total_size": "88.88 KiB",
                }
            ]
            with patch("pymem.cli.get_garbages") as mock_get_garbages:
                mock_get_garbages.return_value = {"count": 0, "objects": []}
                with patch("pymem.cli.get_malloc_stats") as mock_get_malloc_stats:
                    mock_get_malloc_stats.return_value = {"arenas_allocated_total": 1048}
                    result = cli.invoke(main, [str(pid)])
                    # make sure subprocess exit, before throwing AssertionError.
                    e.set()
                    p.join()
                    assert result.exit_code == 0
                    data = json.loads(result.output)
                    assert data["objects"] == [
                        {
                            "type": "<class 'abc.ABCMeta'>",
                            "count": 91,
                            "total_size": "88.88 KiB",
                        }
                    ]
                    assert data["garbages"] == {"count": 0, "objects": []}
                    assert "summary" in data
                    assert data["malloc_stats"] == {"arenas_allocated_total": 1048}
