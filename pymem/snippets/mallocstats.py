import os
import re
import sys
import json
import tempfile
import contextlib

f = globals().get("f")

# sys._debugmallocstats print all message to C level stderr
# contextlib.redirect_stderr is not working here
@contextlib.contextmanager
def redirect_stderr(new_fd):
    origin_fd = os.dup(sys.stderr.fileno())
    os.dup2(new_fd, sys.stderr.fileno())
    yield
    os.dup2(origin_fd, sys.stderr.fileno())


def get_malloc_stats():
    content = ""
    with tempfile.TemporaryFile(mode="w+") as temp_f:
        with redirect_stderr(temp_f.fileno()):
            sys._debugmallocstats()
        temp_f.flush()
        temp_f.seek(0)
        content = temp_f.read()

    assert content != ""

    malloc_stats = iter(content.splitlines())
    skip = 2  # skip class size
    for line in malloc_stats:
        if line == "":
            skip -= 1
        if skip == 0:
            break
    result = {}
    for line in malloc_stats:
        if line.startswith("Total"):
            break
        match = re.match(
            r"^#\s*(?P<name>[\w ]+\w)\s*=\s*(?P<value>[\d,]+)", line
        )
        if match is not None:
            group = match.groupdict()
            result[group["name"].replace(" ", "_")] = int(
                group["value"].replace(",", "")
            )  # remove comma

    return result


stats = get_malloc_stats()
json.dump(stats, f)
