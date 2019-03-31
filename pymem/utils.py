import os

from typing import Union


def human(
    num: Union[int, float],
    *,
    src_unit: str = "KiB",
    dst_unit: str = "MiB",
    include_unit: bool = False
) -> str:
    """
    Convert num from source unit to target unit.
    >>> human(1024 * 1024)
    '1024.00'
    >>> human(1024 * 1024, dst_unit="GiB")
    '1.00'
    >>> human(1024, src_unit="MiB", dst_unit="KiB")
    '1048576.00'
    """
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    try:
        diff = units.index(dst_unit) - units.index(src_unit)
    except IndexError:
        # TODO
        pass
    for _ in range(abs(diff)):
        if diff < 0:
            num = num * 1024.0
        else:
            num = num / 1024.0
    if include_unit:
        return f"{num:.2f} {dst_unit}"
    return f"{num:.2f}"


def check_process_exist(pid: int) -> bool:
    """
    Check process exist through pid.
    >>> check_process_exist(15767)
    True
    """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


__all__ = ["human", "check_process_exist"]
