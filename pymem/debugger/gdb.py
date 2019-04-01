from . import BaseDebugger

from typing import List


class GDBDebugger(BaseDebugger):
    def _format_command(self, debug_code: str) -> List[str]:
        arguments = ["-p", str(self._target_pid), "-batch"]
        gdb_commands = [
            r"call (void *) PyGILState_Ensure()",
            (
                r"call (void) PyRun_SimpleString("
                r'"import base64;'
                rf'exec(base64.b64decode(\'{debug_code}\').decode());"'
                r")"
            ),
            r"call (void) PyGILState_Release((void *) $1)",
        ]
        arguments.extend(
            f"-eval-command={command}" for command in gdb_commands
        )
        return [self.bin_path] + arguments
