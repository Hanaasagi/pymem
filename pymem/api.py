import pkg_resources
from ps_mem import get_memory_usage

from .utils import human
from .debugger import BaseDebugger

from typing import Any
from typing import Dict


def get_malloc_stats(debugger: BaseDebugger) -> Dict[Any, Any]:
    """Get process malloc stats."""
    code = pkg_resources.resource_string(__name__, "snippets/mallocstats.py")
    return debugger.debug_with(code.decode())


def get_objects(debugger: BaseDebugger, limit: int = 15) -> Dict[Any, Any]:
    """Get process objects."""
    code = pkg_resources.resource_string(__name__, "snippets/objects.py")
    return debugger.debug_with(code.decode(), limit=limit)


def get_garbages(debugger: BaseDebugger) -> Dict[Any, Any]:
    """Get process garbages."""
    code = pkg_resources.resource_string(__name__, "snippets/garbages.py")
    return debugger.debug_with(code.decode())


def get_summary(pid: int) -> Dict[str, str]:
    """
    Get process memory usage summary by pid.
    >>> get_summary(pid=32554)
    {
        "private": "17.56 MiB",
        "shared": "1.23 MiB",
        "total": "18.79 MiB",
        "swap": "0.00 MiB"
    }
    """
    summary = {}
    sorted_cmds, shareds, count, total, swaps, total_swap = get_memory_usage(
        [pid], False, False
    )
    cmd = sorted_cmds[0]
    summary["private"] = human(cmd[1] - shareds[cmd[0]], include_unit=True)
    summary["shared"] = human(shareds[cmd[0]], include_unit=True)
    summary["total"] = human(cmd[1], include_unit=True)
    summary["swap"] = human(swaps[cmd[0]], include_unit=True)
    return summary


__all__ = ["get_malloc_stats", "get_objects", "get_garbages", "get_summary"]
