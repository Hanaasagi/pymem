import sys
import json
import distutils.spawn

import click

from . import __version__
from .api import get_objects
from .api import get_summary
from .api import get_garbages
from .utils import check_process_exist
from .debugger import GDBDebugger
from .debugger import BaseDebugger
from .debugger import LLDBDebugger

from typing import Type


@click.command()
@click.argument("pid", required=True, type=int)
@click.option(
    "-d",
    "--debugger",
    "debugger_kind",
    type=click.Choice(["gdb", "lldb"]),
    default="gdb",
)
@click.option("-v", "--verbose", default=False, is_flag=True)
@click.version_option(
    version=__version__,
    prog_name="pymem-debugger",
    message='%(prog)s version: %(version)s'
)
def main(pid: int, debugger_kind: str, verbose: bool) -> None:
    if not check_process_exist(pid):
        click.echo(f"Process(pid={pid}) is not found.", err=True)
        click.get_current_context().exit(1)

    debugger_bin_path = distutils.spawn.find_executable(debugger_kind)
    if not debugger_bin_path:
        click.echo("Could not find debugger in your bin path.", err=True)
        click.get_current_context().exit(1)

    if debugger_kind == "gdb":
        debugger_cls: Type[BaseDebugger] = GDBDebugger
    else:
        debugger_cls: Type[BaseDebugger] = LLDBDebugger  # type: ignore

    data = {}
    debugger: BaseDebugger = debugger_cls(
        bin_path=debugger_bin_path, target_pid=pid, verbose=verbose
    )
    data["objects"] = get_objects(debugger)
    data["garbages"] = get_garbages(debugger)
    data["summary"] = get_summary(pid)
    output = json.dumps(data, indent=4)

    sys.stdout.write(output)
    sys.stdout.flush()


if __name__ == "__main__":
    main()
