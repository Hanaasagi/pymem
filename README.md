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
            "type": "<class 'str'>",
            "objects": 19380,
            "total_size": "2.31 MiB"
        }
    ],
    "garbages": {
        "count": 0,
        "objects": []
    },
    "summary": {
        "private": "19.20 MiB",
        "shared": "1.28 MiB",
        "total": "20.48 MiB",
        "swap": "0.00 MiB"
    }
}
```

It will show
- Top 15 objects(order by size)
- GC garbage info
- Process memory summay
