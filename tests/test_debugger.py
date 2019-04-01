import os
import sys
import pytest
import distutils.spawn
from types import MethodType
from pymem.debugger import BaseDebugger
from pymem.debugger import GDBDebugger
from pymem.debugger import LLDBDebugger


def test_BaseDebugger():
    debugger = BaseDebugger("/usr/bin/gdb", 15532)
    assert debugger.target_pid == 15532
    assert debugger.bin_path == "/usr/bin/gdb"
    assert debugger.verbose is False

    def _format_command(self, debug_code):
        return [
            sys.executable,
            "-c",
            f"import base64; exec(base64.b64decode('{debug_code}').decode());",
        ]

    debugger._format_command = MethodType(_format_command, debugger)
    result = debugger.debug_with(r"""f.write('{"status": "OK"}')""")
    assert result == {"status": "OK"}


def test_GDBDebugger_format_command():
    debugger = GDBDebugger("fake-path", 1)
    commands = debugger._format_command(r"""f.write('{"status": "OK"}')""")
    assert commands == [
        "fake-path",
        "-p",
        "1",
        "-batch",
        "-eval-command=call (void *) PyGILState_Ensure()",
        '-eval-command=call (void) PyRun_SimpleString("import base64;exec(base64.b64decode(\\\'f.write(\'{"status": "OK"}\')\\\').decode());")',
        "-eval-command=call (void) PyGILState_Release((void *) $1)",
    ]


def test_LLDBDebugger_format_command():
    debugger = LLDBDebugger("fake-path", 1)
    commands = debugger._format_command(r"""f.write('{"status": "OK"}')""")
    assert commands == [
        "fake-path",
        "-p",
        "1",
        "--batch",
        "--one-line=expr void * $gil = (void *) PyGILState_Ensure()",
        '--one-line=expr (void) PyRun_SimpleString("import base64;exec(base64.b64decode(\\\'f.write(\'{"status": "OK"}\')\\\').decode());")',
        "--one-line=expr (void) PyGILState_Release($gil)",
    ]


@pytest.mark.skipif(
    not distutils.spawn.find_executable("gdb"),
    reason="Required GDB to run this test.",
)
def test_GDBDebugger():
    pid = os.getpid()
    bin_path = distutils.spawn.find_executable("gdb")
    debugger = GDBDebugger(bin_path, pid)
    result = debugger.debug_with(r"""f.write('{"status": "OK"}')""")
    assert result == {"status": "OK"}


@pytest.mark.skipif(
    not distutils.spawn.find_executable("lldb"),
    reason="Required LLDB to run this test.",
)
def test_LLDBDebugger():
    pid = os.getpid()
    bin_path = distutils.spawn.find_executable("lldb")
    debugger = LLDBDebugger(bin_path, pid)
    result = debugger.debug_with(r"""f.write('{"status": "OK"}')""")
    assert result == {"status": "OK"}
