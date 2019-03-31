import json
import distutils.spawn

import click
import pkg_resources

from .utils import check_process_exist
from .summary import get_summary
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
def main(pid: int, debugger_kind: str, verbose: bool) -> None:
    pretty = True
    if not check_process_exist(pid):
        click.echo(f"Process(pid={pid}) is not found.", err=True)
        click.get_current_context().exit(1)

    debugger_bin_path = distutils.spawn.find_executable(debugger_kind)
    if not debugger_bin_path:
        click.echo(f"Could not find debugger in your bin path.", err=True)
        click.get_current_context().exit(1)

    if debugger_kind == "gdb":
        debugger_cls: Type[BaseDebugger] = GDBDebugger
    else:
        debugger_cls: Type[BaseDebugger] = LLDBDebugger  # type: ignore

    data = {}
    debugger: BaseDebugger = debugger_cls(
        bin_path=debugger_bin_path, target_pid=pid, verbose=verbose
    )
    code = pkg_resources.resource_string(__name__, "snippets/objects.py")
    data["objects"] = debugger.debug_with(code.decode())
    code = pkg_resources.resource_string(__name__, "snippets/garbages.py")
    data["garbages"] = debugger.debug_with(code.decode())
    data["summary"] = get_summary(pid)
    if pretty:
        output = json.dumps(data, indent=4)
    else:
        output = json.dumps(data)
    print(output)


if __name__ == "__main__":
    main()
