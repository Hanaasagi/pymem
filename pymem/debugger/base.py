import io
import os
import sys
import json
import base64
import tempfile
import functools
import subprocess

from typing import Any
from typing import Dict
from typing import List


class BaseDebugger:
    def __init__(self, bin_path: str, target_pid: int, verbose: bool = False):
        self._bin_path = bin_path
        self._target_pid = target_pid
        self._verbose = verbose

    @property
    def bin_path(self) -> str:
        return self._bin_path

    @property
    def target_pid(self) -> int:
        return self._target_pid

    @property
    def verbose(self) -> bool:
        return self._verbose

    def _format_command(self, debug_code: str) -> List[str]:
        raise NotImplementedError()

    def debug_with(self, debug_code: str) -> Dict[Any, Any]:
        tmp_fd, tmp_path = tempfile.mkstemp()
        os.chmod(tmp_path, 0o777)
        debug_code = os.linesep.join(
            [f'f = open("{tmp_path}", "w")', debug_code, r"f.close()"]
        )

        command = self._format_command(
            base64.b64encode(debug_code.encode()).decode()
        )
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        if self.verbose:
            sys.stderr.write(f"Standard Output:\n{stdout}\n")
            sys.stderr.write(f"Standard Error:\n{stderr}\n")
            sys.stderr.flush()
        info = io.StringIO()
        for chunk in iter(functools.partial(os.read, tmp_fd, 1024), b""):
            info.write(chunk.decode())
        info.write("\n")
        info.flush()

        os.close(tmp_fd)
        os.unlink(tmp_path)
        info.seek(0)
        return json.loads(info.read())
