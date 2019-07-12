from . import BaseDebugger

from typing import List


class LLDBDebugger(BaseDebugger):
    def _format_command(self, debug_code: str) -> List[str]:
        arguments = ["-p", str(self.target_pid), "--batch"]
        lldb_commands = [
            r"expr void * $gil = (void *) PyGILState_Ensure()",
            (
                r"expr (void) PyRun_SimpleString("
                r'"import base64;'
                rf'exec(base64.b64decode(\'{debug_code}\').decode());"'
                r")"
            ),
            r"expr (void) PyGILState_Release($gil)",
        ]
        arguments = ["-p", str(self.target_pid), "--batch"]
        for command in lldb_commands:
            arguments.extend(['--one-line', command])
        return [self.bin_path] + arguments
