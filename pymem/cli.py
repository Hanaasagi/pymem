import sys
import json
import distutils.spawn

import click

from . import __version__
from .api import get_objects
from .api import get_summary
from .api import get_garbages
from .api import get_malloc_stats
from .utils import check_process_exist
from .debugger import GDBDebugger
from .debugger import BaseDebugger
from .debugger import LLDBDebugger

from typing import Any
from typing import Dict
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
@click.option(
    "-f",
    "--format",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="json",
)
@click.option("-l", "--limit", "objects_limit", type=click.INT, default=15)
@click.option("-v", "--verbose", default=False, is_flag=True)
@click.version_option(
    version=__version__,
    prog_name="pymem-debugger",
    message="%(prog)s version: %(version)s",
)
def main(
    pid: int,
    debugger_kind: str,
    output_format: str,
    objects_limit: int,
    verbose: bool,
) -> None:
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
    data["objects"] = get_objects(debugger, objects_limit)
    data["garbages"] = get_garbages(debugger)
    data["malloc_stats"] = get_malloc_stats(debugger)
    data["summary"] = get_summary(pid)

    output = format_output(data, output_format)
    sys.stdout.write(output)
    sys.stdout.flush()


def format_output(data: Dict[Any, Any], output_format: str) -> str:
    output = ""
    if output_format == "json":
        output += json.dumps(data, indent=4)
    elif output_format == "text":
        from prettytable import PrettyTable

        table = PrettyTable()
        table.header = False
        for name, value in data["summary"].items():
            table.add_row([name, value])
        table.align = "r"
        output += f"summary:\n{table.get_string()}\n\n"

        if data["garbages"]["count"] > 0:
            output += f"garbages(total: {data['garbages']['count']}):\n"
            table = PrettyTable()
            table.header = False
            for obj in data["garbages"]["objects"]:
                table.add_row([obj])
            table.align = "r"
            output += f"{table.get_string()}\n\n"

        table = PrettyTable()
        table.header = False
        for name, value in data["malloc_stats"].items():
            table.add_row([name, value])
        table.align = "r"
        output += f"malloc stats:\n{table.get_string()}\n\n"

        table = PrettyTable()
        table.field_names = ["type", "count", "total_size"]
        for obj in data["objects"]:
            table.add_row([obj["type"], obj["count"], obj["total_size"]])
        table.align = "r"
        output += f"objects:\n{table.get_string()}\n"
    else:
        raise ValueError("Invalid format")
    return output


if __name__ == "__main__":
    main()
