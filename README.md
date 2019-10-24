# pymem
[![python](https://img.shields.io/pypi/pyversions/pymem.svg?logo=python&logoColor=fed749&colorB=3770a0&label=)](https://www.python.org)
[![Travis-CI Status](https://travis-ci.com/Hanaasagi/pymem.svg?token=wFiDySkCsstZBhsxAoPK&branch=master)](https://travis-ci.com/Hanaasagi/pymem/)
[![Coverage Status](https://coveralls.io/repos/github/Hanaasagi/pymem/badge.svg?t=p9J8th)](https://coveralls.io/github/Hanaasagi/pymem)
[![black](https://img.shields.io/badge/code_style-black-000000.svg)](https://github.com/ambv/black)
[![License](https://img.shields.io/github/license/Hanaasagi/pymem.svg)](https://github.com/Hanaasagi/pymem/blob/master/LICENSE)
![](https://img.shields.io/github/languages/code-size/Hanaasagi/pymem.svg)

pymem is a tool to analysis your Python process.

### Install

```
$ pip install git+https://github.com:Hanaasagi/pymem.git
```

### Usage

You may need to run it with sudo.

```Bash
$ sudo pymem --help
Usage: pymem [OPTIONS] PID

Options:
  -d, --debugger [gdb|lldb]
  -v, --verbose
  --help                     Show this message and exit.

$ sudo pymem [pid]
{
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
        "count": 0,
        "objects": []
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
}
```

It will show
- Top 15 objects(order by size)
- GC garbage info
- Process memory summay
