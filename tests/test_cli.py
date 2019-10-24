import os
import json
import pytest
import textwrap
from unittest.mock import patch
from multiprocessing import Process, Event
from pymem.cli import main, format_output
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
        assert "Could not find debugger in your bin path.\n" == result.output


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


def test_format_output():
    text = r"""{
        "objects": [
            {
                "type": "<class 'list'>",
                "count": 5797,
                "total_size": "6.24 MiB"
            },
            {
                "type": "<class 'str'>",
                "count": 26988,
                "total_size": "3.21 MiB"
            }
        ],
        "garbages": {
            "count": 1,
            "objects": ["<__main__.A at 0x7f7a8d781b50>"]
        },
        "malloc_stats": {
            "arenas_allocated_total": 1725,
            "arenas_reclaimed": 1661,
            "arenas_highwater_mark": 73,
            "arenas_allocated_current": 64,
            "bytes_in_allocated_blocks": 15942032,
            "bytes_in_available_blocks": 127776,
            "bytes_lost_to_pool_headers": 192528,
            "bytes_lost_to_quantization": 166720,
            "bytes_lost_to_arena_alignment": 0
        },
        "summary": {
            "private": "39.28 MiB",
            "shared": "41.82 MiB",
            "total": "81.10 MiB",
            "swap": "0.00 MiB"
        }
    }"""
    data = json.loads(text)
    output = format_output(data, "text")
    expect = textwrap.dedent("""\
        summary:
        +---------+-----------+
        | private | 39.28 MiB |
        |  shared | 41.82 MiB |
        |   total | 81.10 MiB |
        |    swap |  0.00 MiB |
        +---------+-----------+

        garbages(total: 1):
        +--------------------------------+
        | <__main__.A at 0x7f7a8d781b50> |
        +--------------------------------+

        malloc stats:
        +-------------------------------+----------+
        |        arenas_allocated_total |     1725 |
        |              arenas_reclaimed |     1661 |
        |         arenas_highwater_mark |       73 |
        |      arenas_allocated_current |       64 |
        |     bytes_in_allocated_blocks | 15942032 |
        |     bytes_in_available_blocks |   127776 |
        |    bytes_lost_to_pool_headers |   192528 |
        |    bytes_lost_to_quantization |   166720 |
        | bytes_lost_to_arena_alignment |        0 |
        +-------------------------------+----------+

        objects:
        +----------------+-------+------------+
        |           type | count | total_size |
        +----------------+-------+------------+
        | <class 'list'> |  5797 |   6.24 MiB |
        |  <class 'str'> | 26988 |   3.21 MiB |
        +----------------+-------+------------+
    """)

    assert output == expect
